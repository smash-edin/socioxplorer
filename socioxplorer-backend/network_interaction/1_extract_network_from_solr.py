#!/usr/bin/env python3
"""
Python script for extracting the network interaction from Apache Solr.

This script interacts with solr_class with the function get_network_interaction
to retrieve the network of users as a dict object that holds the target objects as keys,
and the values are dicts of keys (sources) and values (weights)
It writes the source, target, weight table into a csv file.

Usage:
    python 1_extract_network_from_solr.py -c core_name

Requirements:
    - Apache Solr instance running and accessible.
    - the solr_class.py inside the root folder of the repo (the second parent level of the process).
    - Python library 'pysolr' installed (install via 'pip install pysolr')
    - Python library 'networkx' installed (install via 'pip install networkx')
    - Python library 'pandas' installed (install via 'pip install pandas')
"""
import pandas as pd
import subprocess
import sys
from os.path import abspath, join, exists
from os import makedirs
import sys
try:
    source_dir = abspath(join('../data_updater/'))
    sys.path.append(source_dir)
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationPaths, ApplicationConfig
from solr_class import *
from utils import print_this

DATA_DIR = ApplicationPaths.SNA_DATA_DIR
DATA_FILE = ApplicationPaths.SNA_DATA_FILE
SNA_THRESHOLD = ApplicationConfig.SNA_THRESHOLD
MAX_SNA_TIMER = ApplicationConfig.SNA_TIMER

if not exists(DATA_DIR):
    makedirs(DATA_DIR)
        

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="please specify core", default=None)
    parser.add_argument('-s', '--source', help="please specify source file name", default=None)
    parser.add_argument('-a', '--consider_all', default=False, help='Consider reprocessing all data.')
    
    args = parser.parse_args()
    core = args.core
    source =args.source
    consider_all = args.consider_all
    try:
        threshold = int(SNA_THRESHOLD)
    except:
        threshold = 'all'

    solr = SolrClass({})
    if core != None or source != None:
        for interaction in ['reply', 'retweet']:
            if core != None:
                users_edges, hits = solr.get_network_interaction(core, interaction)
                # convert the dict to records.
                if len(users_edges) > 0:
                    
                    records = [{'source': source, 'target': target, 'weight': weight}
                            for target, edges in users_edges.items()
                            for source, weight in edges.items()]

                    # convert the records to DataFrame
                    data_df = pd.DataFrame.from_records(records)
                    print_this(f"Number of records: {len(data_df)}")
                    #data_df[['source','target','weight']].to_csv(f'{DATA_FILE}_{core}_all_{interaction}.csv', index=False)
                else:
                    data_df = pd.DataFrame(columns=['source','target','weight'])
                output_file = f'{DATA_FILE}_{core}_{threshold}_{interaction}.csv'
            elif source != None:
                data_df = pd.read_csv(source)
                output_file = f'{source.replace(".csv","")}_{threshold}_{interaction}.csv'
            
            if len(data_df) == 0:
                print_this("No records found in the core for SNA.")
                sys.exit(0)
            original_len = len(data_df)
            
            # neglect the self loop nodes:
            data_df = data_df[data_df['source'] != data_df['target']]
            no_self_loop_len = original_len - len(data_df)
            
            # Calculate the frequencies of each node (account):
            combined_series = pd.concat([data_df['source'], data_df['target']])
            combined_freq = combined_series.value_counts()

            # Add frequency counts to the DataFrame:
            data_df['source_freq'] = data_df['source'].map(combined_freq).fillna(0).astype(int)
            data_df['target_freq'] = data_df['target'].map(combined_freq).fillna(0).astype(int)
            data_df['freq'] = data_df['source_freq'] + data_df['target_freq']

            # limiting the network to the maximum number of edges (required for resource constraints)
            # Write out the dataframe to csv file.
            if not exists(DATA_DIR):
                makedirs(DATA_DIR)
            
            if type(threshold) == int and threshold >= 0: 
                data_df = data_df[data_df['weight']>=threshold]
            
            cleaned_len = len(data_df)
            
            if len(data_df) > 0:
                data_df[['source','target','weight']].to_csv(output_file, index=False)
                print_this(f"Data written to file {output_file}")
            else:
                if original_len > cleaned_len:
                    print_this(f"Please reduce the interaction threshold to include more data by setting SNA_THRESHOLD value in configs.py file to lower value (minimum is 0).")
            
            if len(data_df) > 0 or consider_all:
                fileName = f"{DATA_FILE}_{core}_{threshold}_{interaction}.csv"
                networkFilePath = f"{DATA_FILE}_{core}_{threshold}_{interaction}.gexf"
                if exists(fileName):
                    command = [
                        f"java -cp .:./gephi-toolkit-0.10.0-all.jar Main {MAX_SNA_TIMER} {fileName} {networkFilePath} {consider_all}"
                    ]
                    result = subprocess.run(command, 
                                            check=True, shell=True, text=True, executable='/bin/bash')

                    # Print the output and errors
                    print("Output:", result.stdout)
                    print("Errors:", result.stderr)
                else:
                    print(f"File [{fileName}] does not exist")
            
    else:
        print_this("Please identify the core. You can run the code with command: python 1_extract_network_from_solr.py -c new_core")