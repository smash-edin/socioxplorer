#!/usr/bin/env python3

"""
Python script for extract the information from raw YouTube comments stored in files within the located folder.

This script reads YouTube comments from a file and imports them into combined dict.
It assumes that the YouTube comments are stored in a JSON format in which each tweet is in a separate line.

Usage:
    python 1_extract_data.py -s source_folder_path -o output_folder_path

Requirements:
"""
from os import makedirs
import pandas as pd
import argparse
from os.path import isfile, exists
from utils import *
import sys
logger = create_logger(f"1_extract_youtube_data", file=f"extract_data")


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--data_path', help="The path to the folder that the raw tweets files located in, in the files, each tweet in expected to be in a separate line.", default=None)
    parser.add_argument('-o', '--output_path', help="The path to the processed tweets to write the data to.", default=None)

    args = parser.parse_args()
    data_path = args.data_path

    OUTPUT_FOLDER = args.output_path
    if data_path == None:
        logger.warning(f"[{__name__}]: Please enter the folder of which the source data located in.")
        sys.exit(-1)
    
    if data_path.endswith("/"):
        data_path = data_path[:-1]
    if OUTPUT_FOLDER == None:
        OUTPUT_FOLDER = f"{data_path}_processed"
    logger.info(f"[{__name__}]: The processed tweets will be written to the folder {OUTPUT_FOLDER}")
    if not exists(OUTPUT_FOLDER):
        makedirs(OUTPUT_FOLDER, exist_ok=True)
            
        
    users_files = []
    import glob

    workfiles = list(set([f for f in glob.glob(f"{data_path}/**/*", recursive=True) if isfile(f) and not f.endswith('.gz') and not f.endswith('.bz2')]))
    logger.info(f'[{__name__}]: work_files: {workfiles}')
    
    for workFile in sorted(workfiles):
        extract_youtube_data(workFile, OUTPUT_FOLDER)
        if isfile(workFile):
            compress_file(workFile, f"{workFile}.gz")
