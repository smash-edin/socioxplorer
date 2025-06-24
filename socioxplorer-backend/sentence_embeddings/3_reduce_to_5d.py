#!/usr/bin/env python3
import os
import subprocess
import sys
import math
import random
import argparse
import pandas as pd
from umap.parametric_umap import ParametricUMAP, load_ParametricUMAP
from extract_text_data import DATA_DIR, DATA_FILE
from tqdm import tqdm
import sys

try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    sys.exit(-1)
from solr_class import *
from utils import print_this

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser.add_argument('-c', '--core', default=None, help='Core name of the Solr data collection.')
    parser.add_argument('-d', '--data', default=None, help='Name of data file')
    parser.add_argument('--source-column', type=str, default='sbert_embedding', help='Name of column containing input embeddings')
    parser.add_argument('--training-size', type=int, default=200000, help='Number of examples to train reducer from')
    parser.add_argument('--out-file-reducer', default=None, help='Name of target file containing reducer')
    parser.add_argument('-a', '--consider_all', type=str, default=False, help='Consider reprocessing all data.')
    # parser.add_argument('--out-file-data', default=None, help='Name of target file containing reduced embeddings')

    args = parser.parse_args()
    return args

def convert_string_to_array(text):
    try:
        return eval(",".join(text.replace("[ ", "[").replace(" ]", "]").split()))
    except Exception:
        print("Data in the input file is not as expected. Please start the steps after cleaning the data folder.")
        sys.exit(-1)

if __name__ == '__main__':

    args = get_args()
    if args.core is not None:

        # Get command line arguments
        core = args.core
        source_column = args.source_column
        data_path = args.data
        training_size = args.training_size
        consider_all = args.consider_all

        if args.data is None:
            data_path = f'{DATA_FILE}_{core}_w_embeddings.csv' # Location of files with SBERT embeddings
        
        if not os.path.exists(data_path):
            print_this("Data path not found!")
            sys.exit(-1)

        # Create folder to hold embedder model if it doesn't exist
        reducer_dir = "./embedder"
        if not os.path.exists(reducer_dir):
            os.makedirs(reducer_dir)

        # Define embedder model sub-folder path
        if args.out_file_reducer is None:
            out_file_reducer = f"{reducer_dir}/{core}"
        else:
            out_file_reducer = f"{reducer_dir}/{args.out_file_reducer}"

        print('Target file name for 5D reducer:', out_file_reducer)

        # Check if data path point to a single file or an entire directory
        
        
        if os.path.isfile(data_path):
            if consider_all:
                folder_path = os.path.dirname(data_path)
                all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith("_w_embeddings.csv") and f"_{core}_" in f]
            else:
                all_files = [data_path]
        elif os.path.isdir(data_path):
            # If it points to a directory, list all the files containing the SBERT embeddings
            all_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith("_w_embeddings.csv") and f"_{core}_" in f]
        else:
            print_this("Data path is neither a file nor a directory!")
            sys.exit(-1)

        print("1. Getting 5D embedder model...")
        if len(all_files) > 1 or not os.path.isdir(out_file_reducer):
            # If the data path points to a directory or the embedder model sub-folder does not exist, it means we
            # need to train the embedder model

            total_examples = sum([int(f.split("_NB_")[1].replace("_w_embeddings.csv", "")) for f in all_files]) # Retrieve number of examples in file from file name
            prop_needed = training_size / total_examples # Figure out what proportion of each file to sample to end with the correct number of training examples

            train_embeddings = list()

            print("\tA. Sampling training data...")
            for file in tqdm(all_files):
                df = pd.read_csv(file) # Load the dataframe with the embeddings
                if pd.api.types.is_string_dtype(df[source_column].dtype):
                    df[source_column] = df[source_column].apply(convert_string_to_array)
                embeddings_all = df[source_column].to_list()

                # Sample the correct number of examples
                if prop_needed < 1:
                    # If there are more examples available in total than the required training size, sample only a subset
                    nb_needed = math.ceil(prop_needed * len(embeddings_all))
                    train_embeddings += random.sample(embeddings_all, nb_needed)
                else:
                    # Otherwise, just add all the data to the training set
                    train_embeddings += embeddings_all
                print("\t...", len(train_embeddings), "embeddings used for training")

            print("\tB. Training...")
            embedder = ParametricUMAP(n_components=5).fit(train_embeddings)

            print("\tC. Saving 5d reducer...")
            embedder.save(out_file_reducer)
        else:
            print("\tLoading model from memory...")
            embedder = load_ParametricUMAP(out_file_reducer)

        print("2. Applying 5D model...")
        for i,file_path in enumerate(all_files):
            print("\tFile number", i + 1, "out of", len(all_files))
            out_file_data = file_path.replace('.csv', '_5d.pkl')
            print('\tTarget file name for data:', out_file_data)

            print("\tA. Loading data...")
            df = pd.read_csv(file_path)
            if pd.api.types.is_string_dtype(df[source_column].dtype):
                df[source_column] = df[source_column].apply(convert_string_to_array)
            embeddings_all = df[source_column].to_list()

            print("\tB. Running model on all data...")
            reduced_embeddings = embedder.transform(embeddings_all)

            print("\tC. Saving 5d embeddings...")
            df['embedding_5d'] = reduced_embeddings.tolist()
            df.drop(source_column, axis=1, inplace=True)
            df.to_pickle(out_file_data)
        
        
        print(f"[handleReProcessTopics]: Dimentionality reduction to 5D for core: '{core}' completed successfully.")
        
        command = f"python3 4_reduce_to_2d.py -c {core} -d {out_file_data}"
        subprocess.run(
            [command],
            check=True, shell=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
        )

    else:
        print_this("Please identify the core. You can run the code with command: python 3_reduce_to_5d.py -c new_core")

