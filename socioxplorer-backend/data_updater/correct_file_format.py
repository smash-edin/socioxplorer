# -*- coding: utf-8 -*-
import ijson
import argparse
import json
from os.path import split, join, exists, splitext
from os import remove
import gzip
import shutil
from dateutil import parser

def convert_dates(obj):
    """Recursively traverse a nested dictionary/list and convert 'created_at' timestamps to ISO 8601 format."""
    if isinstance(obj, dict):  # If obj is a dictionary
        for key, value in obj.items():
            if key == "created_at" and isinstance(value, str):
                try:
                    obj[key] = parser.parse(value).strftime('%Y-%m-%dT%H:%M:%S.%fZ')  # Convert to ISO 8601
                except ValueError:
                    pass  # Skip if parsing fails
            else:
                convert_dates(value)  # Recurse into nested dicts/lists
    elif isinstance(obj, list):  # If obj is a list
        for item in obj:
            convert_dates(item)  # Recurse into list elements
    return obj         

def confirm_new_file(file_name):
    """
    Check if a file exists and if so, create a new file name by adding a counter to the file name.
    
    :param file_name: Path to the file to be checked.
    """
    directory, filename = split(file_name)
    base, ext = splitext(filename)
    new_file_name = file_name
    counter = 1
    while exists(new_file_name):
        new_file_name = join(directory, f"{base}_{counter}{ext}").strip()
        counter += 1
    if new_file_name != file_name:
        shutil.copy(file_name, new_file_name)
        
def compress_file(input_file, output_file):
    """
    Compress a file using gzip and remove the original file if successful.

    :param input_file: Path to the file to be compressed.
    :param output_file: Path where the compressed file will be saved.
    """
    try:
        confirm_new_file(output_file)
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        if exists(output_file):
            remove(input_file)
            print(f"Compression successful. Original file '{input_file}' removed.")
        else:
            print(f"Error: Compressed file '{output_file}' not found.")
    
    except Exception as e:
        print(f"Compression failed: {e}")

     
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input_file', help="The path to the file with multiple lines JSON objects.", default=None)
    arg_parser.add_argument('-o', '--output_file', help="The path to the processed tweets to write the data to.", default=None)

    args = arg_parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    
    if input_file is None:
        print("Please provide the input file with the -i flag.")
        exit(1)
    if output_file is None:
        output_file = input_file.replace('.json', '_processed.json')
    
    objects = {'data': [], 'includes': {'tweets': [], 'users': [], 'media': [], 'places': [], 'polls': []}}

    
    with open(input_file, "r", encoding="utf-8") as file:
        for tweet_objs in ijson.items(file, "data.item"):
            objects['data'].append(tweet_objs)
            
    with open(input_file, "r", encoding="utf-8") as file:
        for tweet_includes_obj in ijson.items(file, "includes.tweets.item"):
            objects['includes']['tweets'].append(tweet_includes_obj)
    with open(input_file, "r", encoding="utf-8") as file:    
        for user_includes_obj in ijson.items(file, "includes.users.item"):
            objects['includes']['users'].append(user_includes_obj)
            
    with open(input_file, "r", encoding="utf-8") as file:
        for media_obj in ijson.items(file, "includes.media.item"):
            objects['includes']['media'].append(media_obj)
    with open(input_file, "r", encoding="utf-8") as file:
        for places_objs in ijson.items(file, "includes.places.item"):
            objects['includes']['places'].append(places_objs)
    with open(input_file, "r", encoding="utf-8") as file:
        for polls_objs in ijson.items(file, "includes.poll.item"):
            objects['includes']['polls'].append(polls_objs)
            
    
    converted_objects = convert_dates(objects)
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(converted_objects, file, ensure_ascii=False)
        
    compress_file(input_file, f"{input_file}.tar.gz")