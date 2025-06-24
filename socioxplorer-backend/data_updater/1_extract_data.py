#!/usr/bin/env python3

"""
Python script for extract the information from raw tweets stored in files within the located folder.

This script reads tweets from a file and imports them into combined dict.
It assumes that the tweets are stored in a JSON format in which each tweet is in a separate line.

Usage:
    python 1_extract_data.py -s source_folder_path -o output_folder_path

Requirements:
"""
import json
import ijson
from os import makedirs
import datetime
from os.path import isfile, join, exists
import argparse
from utils import *
import sys
logger = create_logger(f"1_extract_data", file=f"extract_data")

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
    
    data_path = data_path[:-1] if data_path.endswith("/") else data_path
    if OUTPUT_FOLDER == None:
        OUTPUT_FOLDER = f"{data_path}_processed"
    logger.info(f"[{__name__}]: The processed tweets will be written to the folder {OUTPUT_FOLDER}")
    if not exists(OUTPUT_FOLDER):
        makedirs(OUTPUT_FOLDER, exist_ok=True)
            
        
    users_files = []
    day = datetime.datetime.now()
    limit = day.strftime('%Y_%m_%d')
    limit_day = day.strftime('%Y_%m_%d')

    import glob

    workfiles = list(set([f for f in glob.glob(f"{data_path}/**/*", recursive=True) if isfile(f) and not f.endswith('.gz') and not f.endswith('.bz2')]))
    logger.info(f'[{__name__}]: work_files: {workfiles}')
    
        
    for workFile in sorted(workfiles):
        logger.info(f"[{__name__}]: {workFile}")
        retweets_dict = dict()
        replies_dict = dict()
        quotes_dict = dict()
        tweets_dict = dict()
        users_dict = dict()
        media_dict = dict()
        places_dict = dict()
        tweets = []
        if exists(workFile):
            with open(workFile, 'r' , encoding='utf-8') as fin:
                try:
                    parser = ijson.items(fin, '', multiple_values=True)
                
                    for objects in parser:
                        if objects != None:
                            tweets, users, includes, places, media, poll = extract_raw_responses(objects)
                            places_dict = extractResponseContentsFromDict(places, places_dict)
                            media_dict = extractMediaContentsFromDict(media, media_dict)
                            users_dict = extractResponseContentsFromDict(users, users_dict)
                            if type(includes) == list:
                                for obj_ in includes:
                                    tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(obj_, tweets_dict, False, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                            else:
                                tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(includes, tweets_dict, False, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                            if type(tweets) == list:
                                for obj_ in tweets:
                                    tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(obj_, tweets_dict, True, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                            else:
                                tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(tweets, tweets_dict, True, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                except Exception as exp:
                    print(f"[{__name__}]: Error while reading the file {workFile}: {exp}")
                    continue

            combined_dict = tweets_dict.copy()

            for k in replies_dict.keys():
                for j in replies_dict[k].keys():
                    if j not in combined_dict.keys():
                        combined_dict[j] = replies_dict[k][j]
            for k in quotes_dict.keys():
                for j in quotes_dict[k].keys():
                    if j not in combined_dict.keys():
                        combined_dict[j] = quotes_dict[k][j]

            for k in replies_dict.keys():
                for j in replies_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'repliesTweets' not in combined_dict[k].keys():
                            combined_dict[k]['repliesTweets'] = [j]
                        else:
                            if j not in combined_dict[k]['repliesTweets']:
                                combined_dict[k]['repliesTweets'].append(j)

                        repliesTimes = f"{replies_dict[k][j]['userScreenName']} {replies_dict[k][j]['createdAt']}"
                        if 'repliesTimes' not in combined_dict[k].keys():
                            combined_dict[k]['repliesTimes'] = [repliesTimes]
                        if repliesTimes not in combined_dict[k]['repliesTimes']:
                            combined_dict[k]['repliesTimes'].append(repliesTimes)

            for k in retweets_dict.keys():
                for j in retweets_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'retweeters' not in combined_dict[k].keys():
                            combined_dict[k]['retweeters'] = [retweets_dict[k][j]['userScreenName']]
                        else:
                            if retweets_dict[k][j]['userScreenName'] not in combined_dict[k]['retweeters']:
                                combined_dict[k]['retweeters'].append(retweets_dict[k][j]['userScreenName'])
                        if 'createdAtDays' in retweets_dict[k][j].keys():
                            retweetTimes = f"{retweets_dict[k][j]['userScreenName']} {retweets_dict[k][j]['createdAtDays']}"
                        elif 'createdAt' in retweets_dict[k][j].keys():
                            retweetTimes = f"{retweets_dict[k][j]['userScreenName']} {retweets_dict[k][j]['createdAt'][0:10]}"
                        else:
                            retweetTimes = f"{retweets_dict[k][j]['userId']}"

                        if 'retweetTimes' not in combined_dict[k].keys():
                            combined_dict[k]['retweetTimes'] = [retweetTimes]
                        if retweetTimes not in combined_dict[k]['retweetTimes']:
                            combined_dict[k]['retweetTimes'].append(retweetTimes)

            for k in quotes_dict.keys():
                for j in quotes_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'quoteTweets' not in combined_dict[k].keys():
                            combined_dict[k]['quoteTweets'] = [j]
                        else:
                            if j not in combined_dict[k]['quoteTweets']:
                                combined_dict[k]['quoteTweets'].append(j)

                        if 'quoters' not in combined_dict[k].keys():
                            combined_dict[k]['quoters'] = [quotes_dict[k][j]['userScreenName']]
                        else:
                            if quotes_dict[k][j]['userScreenName'] not in combined_dict[k]['quoters']:
                                combined_dict[k]['quoters'].append(quotes_dict[k][j]['userScreenName'])
                        if 'createdAtDays' in quotes_dict[k][j].keys():
                            quoteTimes = f"{quotes_dict[k][j]['userScreenName']} {quotes_dict[k][j]['createdAtDays']}"
                        elif 'createdAt' in quotes_dict[k][j].keys():
                            quoteTimes = f"{quotes_dict[k][j]['userScreenName']} {quotes_dict[k][j]['createdAt'][0:10]}"
                        else:
                            quoteTimes = f"{quotes_dict[k][j]['userId']}"

                        if 'quoteTimes' not in combined_dict[k].keys():
                            combined_dict[k]['quoteTimes'] = [quoteTimes]

                        if quoteTimes not in combined_dict[k]['quoteTimes']:
                            combined_dict[k]['quoteTimes'].append(quoteTimes)



            outputFile = workFile.split("/")[-1] if len(workFile.split("/")) > 1 else "outputFile"

            with open(join(OUTPUT_FOLDER, outputFile), 'a+', encoding='utf-8') as fout:
                for k in combined_dict.keys():
                    fout.write(f"{json.dumps(combined_dict[k], ensure_ascii=False)}\n")
                    
            compress_file(workFile, f"{workFile}.tar.gz")
