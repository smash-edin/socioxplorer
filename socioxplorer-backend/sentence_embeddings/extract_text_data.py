#!/usr/bin/env python3
"""
Python script for extracting the text data of tweets from Apache Solr.

This script interacts with solr_class with the function get_text_data
to retrieve the network of users as a dict object that holds the target objects as keys,
and the values are dicts of keys (sources) and values (weights)
It writes the source, target, weight table into a csv file.

Usage:
    python extract_network.py -c core_name

Requirements:
    - Apache Solr instance running and accessible.
    - the solr_class.py inside the root folder of the repo (the second parent level of the process).
    - Python library 'pysolr' installed (install via 'pip install pysolr')
    - Python library 'pandas' installed (install via 'pip install pandas')
"""
import pandas as pd
from os import makedirs
from os.path import abspath, join, exists
import sys
import argparse
import re
try:
    source_dir = abspath(join('../data_updater/'))
    sys.path.append(source_dir)
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *
from utils import print_this
from configs import ApplicationPaths
DATA_DIR = ApplicationPaths.EMBEDDINGS_DATA_DIR
DATA_FILE = ApplicationPaths.EMBEDDINGS_DATA_FILE

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser = argparse.ArgumentParser('Extract Text Data from Solr')
    parser.add_argument('-c', '--core', help="The Solr core of which the data will be retrieved from", default=None)
    parser.add_argument('-a', '--consider_all', type=str, default=False, help='Consider reprocessing all data.')
    
    args = parser.parse_args()
    return args

def preprocess_text(text):
    # remove the http links.
    new = " ".join([t for t in str(text).split() if t[:4] != "http"])
    # replace the encrypted names with the flag [USERNAME]
    new = re.sub("[a-f0-9]{16}", "[USERNAME]", new)
    #replace mentions with the flag [USERNAME]
    new = " ".join([t if not t.startswith('@') else "[USERNAME]" for t in new.split()])
    # remove the http links.
    new = " ".join([t for t in new.split() if t[:4] != "http"])
    return new

if __name__== "__main__":

    args = get_args()
    core = args.core
    consider_all = args.consider_all
    
    solr = SolrClass({})
    if core != None:
        records, hits = solr.get_text_data(core, consider_all)
        
        if hits == 0 or len(records) == 0:
            print_this("No records found in the core.")
            sys.exit(0)
            
        data_df = pd.DataFrame.from_records(records)
        data_df['text'] = data_df.fullText.apply(lambda x: preprocess_text(x))

        # Write out the dataframe to csv file.
        if not exists(DATA_DIR):
            makedirs(DATA_DIR)
        output_file = f'{DATA_FILE}_{core}.csv'
        data_df[['id','fullText','text']].to_csv(output_file, index=False)
        print_this(f"Data written to file {output_file}")

    else:
        print_this("Please identify the core. You can run the code with command: python 1_extract_text_data.py -c new_core")