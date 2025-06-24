import os
import subprocess
import sys
import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from sentence_transformers import SentenceTransformer
from torch.cuda import is_available
from tqdm import tqdm
from extract_text_data import DATA_DIR, DATA_FILE
import shutil
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    sys.exit(-1)
from solr_class import *
from utils import print_this
from configs import ApplicationPaths

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser.add_argument('-c', '--core', default=None, help='Core name of the Solr data collection.')
    parser.add_argument('-d', '--data', default=None, help='Name of data file')
    parser.add_argument('--source-column', type=str, default='text', help='Name of column contain input text')
    parser.add_argument('--model-name', type=str, default=None, help='Model name')
    parser.add_argument('-a', '--consider_all', type=str, default=False, help='Consider reprocessing all data.')
    # parser.add_argument('--out-file', default=None, help='Name of target file')

    args = parser.parse_args()
    return args


def df_apply_sbert(classifier, sub_df, source_column, target_column="sbert_embedding"):
    texts = sub_df[source_column].to_list()
    embeddings = list(classifier.encode(texts))
    sub_df[target_column] = embeddings
    return sub_df


def run(classifier, dataframe, out_file, source_column):
    number_lines = len(dataframe)
    chunksize = 12

    if os.path.isfile(out_file):
        try:
            already_done = pd.read_csv(out_file)
            start_line = len(already_done)
        except Exception as exp:
            print(f"ERROR: {exp}")
            start_line = 0

    else:
        start_line = 0

    for i in tqdm(range(start_line, number_lines, chunksize)):

        sub_df = dataframe.iloc[i: i + chunksize]
        sub_df = df_apply_sbert(classifier, sub_df, source_column)

        if i == 0:
            sub_df.to_csv(out_file, mode='a', index=False)
        else:
            sub_df.to_csv(out_file, mode='a', index=False, header=False)


if __name__ == '__main__':

    args = get_args()
    core = args.core
    
    if core != None:
        source_column = args.source_column
        model_name = args.model_name
        if model_name == None:
            model_name = ApplicationPaths.EMBEDDINGS_MODEL_PATH
        data_path = args.data
        consider_all = args.consider_all
        
        if args.data is None:
            data_path = f'{DATA_FILE}_{core}.csv'
        
        if data_path != None and os.path.exists(data_path):
            processed_data_path = data_path.replace(".csv", ".processed.csv")
            print(f"0. Loading data... {data_path}")
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
            else:
                print_this("Data file not found!")
                sys.exit(-1)
            
            if len(df) == 0:
                print_this("No data to perform Topic modelling!")
                sys.exit(0)
                
            print("1. Loading model...")
            use_cuda = is_available()
            if use_cuda:
                print('Using GPU')
                classifier = SentenceTransformer(model_name, device='cuda')
            else:
                print("Using CPU")
                classifier = SentenceTransformer(model_name)
                
            target_path = data_path.replace('.csv', "_NB_" + str(len(df)) + '_w_embeddings.csv')

            print('Target file name:', target_path)

            print("2. Running model...")
            run(classifier, df, target_path, source_column)
            
            
            print(f"[handleReProcessTopics]: Generating sentence embeddings for core: '{core}' completed successfully.")
                
            command = f"python3 3_reduce_to_5d.py -c {core} -d {target_path} -a {consider_all}"
            subprocess.run(
                [command],
                check=True, shell=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
            )
            
            shutil.move(data_path, processed_data_path)
            print("Done!")
            
        elif consider_all: #If the data file is not found and consider_all is True, then we will reprocess all data
            command = f"python3 3_reduce_to_5d.py -c {core} -d {DATA_DIR} -a {consider_all}"
            subprocess.run(
                [command],
                check=True, shell=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
            )
    else:
        print_this("Please identify the core. You can run the code with command: python 2_generate_sentence_embeddings.py -c new_core")

