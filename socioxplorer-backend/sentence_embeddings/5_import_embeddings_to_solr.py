#!/usr/bin/env python3
import shutil
from os.path import abspath, join, exists
from os import makedirs
import sys
import pandas as pd
import argparse
from extract_text_data import DATA_DIR, DATA_FILE
from utils import print_this

try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    sys.exit(-1)
from solr_class import *
from configs import ApplicationConfig

limit = 100000

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser = argparse.ArgumentParser('Update Embeddings in Solr')
    parser.add_argument('-c', '--core', help="The Solr core.", default=None)
    parser.add_argument('-s', '--input_file', help="The embeddings file.", default=None,)

    args = parser.parse_args()
    return args

def get_embedding_from_file(fileName):
    try:
        df = pd.read_pickle(fileName)
        return df, True
    except Exception as exp:
        print_this(f"Error at loading data from file {fileName}")
        return None, False

def copy_embeddings(core):
    try:
        # Create the destination folder if it does not exist
        for folder in ['embedder', 'embedder_2D']:
            if not exists(f'../../socioxplorer-frontend/api/{folder}/'):
                makedirs(f'../../socioxplorer-frontend/api/{folder}/')

            # Copy the entire contents of the source folder to the destination folder
            shutil.copytree(f'./{folder}/{core}', join(f'../../socioxplorer-frontend/api/{folder}/{core}'))
    except Exception as exp:
        print_this("Warning: Please notice that you may need to copy the embeddings (both embedder and embedder_2D) manually to the `socioxplorer/socioxplorer-frontend/api` folder.")
        
if __name__== "__main__":

    # current version works only on retweeting interaction. preparing fields name in Solr
    network_label = 'retweet'
    network = 'retweetTimes'

    # getting passed arguments
    args = get_args()
    core = args.core
    input_file = args.input_file
    
    if core is not None:
        if input_file is None:
            input_file = join(DATA_DIR, f'{DATA_FILE}_{core}_w_embeddings_5d_2d.pkl')

        if not exists(input_file):
            print(f"File {input_file} does not exist. Please provide a valid file.")
            sys.exit(1)
        
        embeddings_df, fileLoaded = get_embedding_from_file(input_file)
        
        if not fileLoaded:
            print("Input file does not loaded properly. Check the existence of the file, and then enter the command:\n python import_networks_to_solr.py -c new_core -s edges_GRAPH.json.\n")
        elif core in ApplicationConfig.SOLR_CORES:
            dataSource = SolrClass({})

            embeddings_df.index = embeddings_df['id']
            
            if not embeddings_df.index.is_unique:
                print("Duplicate indices detected. Resetting index.")
                embeddings_df = (
                    embeddings_df
                    .dropna(subset=['embedding_5d', 'embedding_2d'])
                    .drop_duplicates(subset=['id'], keep='first')
                    .set_index('id')
                )
            
            embeddings_dict = embeddings_df[['id','embedding_5d','embedding_2d']].to_dict(orient="index")

            print(f"Saving embeddings to Solr")
            try:
                dataSource.add_items_to_solr(core, list(embeddings_dict.values()))
            except Exception as exp:
                print_this("Error at saving embeddings to Solr")
                
            try:
                copy_embeddings(core)
                
            except Exception as exp:
                print_this("Error at copying embeddings to socioxplorer_ui")
                        
        else:
            print("Loading data file and accessing Solr core failed.")
    else:
        print("Please provide the Solr core. The command might be:\n python import_networks_to_solr.py -c new_core.\n")