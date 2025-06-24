# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime as dt

import schedule

import subprocess
from utils import create_logger
import json

logger = create_logger(f"run_scheduler", file=f"run_scheduler")
processing_requests = '../processing_requests.json'

def update_processing_settings(processingSettings=dict(), cores_list =[]):
    if os.path.exists(processing_requests):
        with open(processing_requests, 'r') as fin:
            try:
                processing_settings = json.load(fin)
                if len(processing_settings) > 0:
                    for k in processing_settings.keys():
                        if k in k in cores_list:
                            if k not in processingSettings.keys():
                                processingSettings[k] = dict()
                            processingSettings[k]['rePreProcessData'] = processing_settings[k].get('rePreProcessData', '')
                            processingSettings[k]['reProcessTopics'] = processing_settings[k].get('reProcessTopics', False)
                            processing_settings[k]['reProcessTopics'] = False
                            processingSettings[k]['reProcessSNA'] = processing_settings[k].get('reProcessSNA', False)
                            processing_settings[k]['reProcessSNA'] = False
                    # the updates has been considered, reset the flags.
                    with open(processing_requests, 'w') as fout:
                        json.dump(processing_settings, fout, ensure_ascii=False, indent=4)
            except Exception as exp:
                print(exp)
    return processingSettings
                
        
            
def job(coreTwitter=None, twitterDataSource=None, coreYouTube=None, youtubeDataSource=None,processingSettings=dict()):
    """Executes data extraction and analysis job."""
    processingSettings = update_processing_settings(processingSettings, [coreTwitter ,coreYouTube])
        
    print(f"processingSettings: {processingSettings}")
    try:
        tqs = f" -tqs '{json.dumps(processingSettings[coreTwitter])}'" if coreTwitter in processingSettings.keys() else ""
        yqs = f" -yqs '{json.dumps(processingSettings[coreYouTube])}'" if coreYouTube in processingSettings.keys() else ""
        
        # Prepare command arguments based on input values
        twitter_items = f"-tc {coreTwitter} -td {twitterDataSource} {tqs}" if coreTwitter and twitterDataSource else ""
        youtube_items = f"-yc {coreYouTube} -yd {youtubeDataSource} {yqs}" if coreYouTube and youtubeDataSource else "" 
        
        cmd = f"python ./run_system.py {twitter_items} {youtube_items}"
        
        # Log the command and execute it
        logger.info(f"[{job.__name__}]: Starting data extraction with command: {cmd}")
        result = subprocess.run(cmd, shell=True)

        # Log command completion and check exit status
        if result.returncode == 0:
            logger.info(f"[{job.__name__}]: system finished successfully.")
        else:
            logger.warning(f"[{job.__name__}]: system failed with exit status {result.returncode}.\nOutput: {result.stderr}")
        
    except Exception as exp:
        logger.error(f"[{job.__name__}]: Job execution failed due to an exception: {exp}")


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-tc', '--coreTwitter', help="Specify Twitter core", default=None)
parser.add_argument('-td', '--twitterDataSource', help="Specify the path of the Twitter data source so the system monitor.", default=None)
parser.add_argument('-yc', '--coreYouTube', help="Specify YouTube core", default=None)
parser.add_argument('-yd', '--youtubeDataSource', help="Specify the path of the YouTube data source so the system monitor.", default=None)

args = parser.parse_args()

coreTwitter = args.coreTwitter
twitterDataSource = args.twitterDataSource
coreYouTube = args.coreYouTube
youtubeDataSource = args.youtubeDataSource
processingSettings = dict()

if not any([any([coreTwitter, coreYouTube]), all([coreTwitter, twitterDataSource]), all([coreYouTube, youtubeDataSource])]):
    print(f"""{"-"*10}\nAn error occured\n{"-"*10}
          Please specify the core (required) and the data source (optional).
          At least one of (core or both the core and data source) are required to start the system correctly.
          To start the system, you can use the following command:
          \tpython3 run_scheduler.py -tc <coreTwitter> -td <twitterDataSource> -yc <coreYouTube> -yd <youtubeDataSource>\n{"="*10}\n""" )
    logger.warning("[run_scheduler]: Insufficient core or data source specified to start the system.")
    sys.exit(1)

job(coreTwitter, twitterDataSource, coreYouTube, youtubeDataSource, processingSettings)

#Let the system runs every day at 00:30.
schedule.every().day.at("00:30").do(job, coreTwitter=coreTwitter, twitterDataSource=twitterDataSource, coreYouTube=coreYouTube, youtubeDataSource=youtubeDataSource, processingSettings=processingSettings)

while True:
    schedule.run_pending()
    time.sleep(5)