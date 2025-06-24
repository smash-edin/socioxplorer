# -*- coding: utf-8 -*-
"""
Python script to manage running all services and clients in the system.

This script reads tweets from a file and imports them into combined dict.
It assumes that the tweets are stored in a JSON format in which each tweet is in a separate line.

Usage:
    python 1_extract_data.py -s source_folder_path -o output_folder_path

Requirements:
"""
import os
import subprocess
import time
import sys
from utils import create_logger
logger = create_logger(f"run_system", file='run_system')

try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    logger.warning("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    logger.warning("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig, ApplicationPaths
import psutil
import json

#logging.basicConfig(level=logging.INFO)

SENTIMENT_API_PORT = ApplicationConfig.SENTIMENT_API_PORT
LOCATION_API_PORT = ApplicationConfig.LOCATION_API_PORT
CONDA_VENV = ApplicationConfig.CONDA_VENV
workers = 1 if ApplicationConfig.LIMITED_RESOURCE else 2
threads = 2 if ApplicationConfig.LIMITED_RESOURCE else 4

DATA_EXTRACTION_SERVICE_PATH = ApplicationPaths.DATA_EXTRACTION_SERVICE_PATH
YOUTUBE_DATA_EXTRACTION_SERVICE_PATH = ApplicationPaths.YOUTUBE_DATA_EXTRACTION_SERVICE_PATH
IMPORT_DATA_TO_SOLR_SERVICE_PATH = ApplicationPaths.IMPORT_DATA_TO_SOLR_SERVICE_PATH
IMPORT_YOUTUBE_DATA_TO_SOLR_SERVICE_PATH = ApplicationPaths.IMPORT_YOUTUBE_DATA_TO_SOLR_SERVICE_PATH
LOCATION_CLIENT_PATH = ApplicationPaths.LOCATION_CLIENT_PATH
SENTIMENT_CLIENT_PATH = ApplicationPaths.SENTIMENT_CLIENT_PATH
LOCATION_GUNICORN_COMMAND = f"gunicorn -b 0.0.0.0:{LOCATION_API_PORT} -t 1000 {ApplicationPaths.LOCATION_API_CODE}:app --workers={workers} --threads={threads}"
SENTIMENT_GUNICORN_COMMAND = f"gunicorn -b 0.0.0.0:{SENTIMENT_API_PORT} -t 1000 {ApplicationPaths.SENTIMENT_API_CODE}:app --workers={workers} --threads={threads}"
TOPICS_EXTRACTION_PATH = ApplicationPaths.TOPICS_EXTRACTION_PATH
NETWORK_INTERACTION_PATH = ApplicationPaths.NETWORK_INTERACTION_PATH


def isServiceRunning(port):
    """
    Check if the service API is running by looking for the process.

    Args:
        port int: The port number of the service. Defaults to 10077.

    Returns:
        boolean: The status of the service.
    """
    try:
        for process in psutil.process_iter(attrs=["cmdline"]):
            cmdline = process.info["cmdline"]
            if cmdline and len(cmdline) > 5 and "gunicorn" in cmdline[5] and str(port) in cmdline[5]:
                return True
        return False
    except Exception as exp:
        logger.warning(f"[{isServiceRunning.__name__}]: An error occurred in function '\n{exp}\n")
        return False

def checkProcessIsRunning(screen_name):
    """A function to check if a screen session for a given name is running.

    Args:
        screen_name (str): The name of the session to check.

    Returns:
        _type_: Boolean, the status of the screen session.
    """
    try:
        result = subprocess.run([f'screen -ls | grep {screen_name}'], shell=True, capture_output=True, text=True, executable='/bin/bash')
        if screen_name in result.stdout:
            return True
        return False
    except subprocess.CalledProcessError as exp:
        logger.warning(f"[{checkProcessIsRunning.__name__}]: An error occurred while checking screen sessions: {exp}")
        return False
    except Exception as exp:
        logger.warning(f"[{checkProcessIsRunning.__name__}]: An error occurred in function \n{exp}\n")
        return False

def runService(service = "sentiment"):
    f"""Start the service API in a new screen session with a Conda environment.

    Args:
        service (str, optional): The analysis required (currently either {' or '.join(ApplicationConfig.ANALYSIS_SERVICES)}). Defaults to "sentiment".
    """
    try:
        screen_name = f"socioxplorer_{service}_api"
        
        service_command = LOCATION_GUNICORN_COMMAND if service == "location" else SENTIMENT_GUNICORN_COMMAND
        command = (
            f"screen -dmS {screen_name} bash -c 'cd ../{service}_api && " +
            f"source $(conda info --base)/etc/profile.d/conda.sh && " +
            f"conda activate {CONDA_VENV}" +
            f" && {service_command}'" if service_command else "'"
        )
        
        print(command)
        
        temp = subprocess.Popen(command, shell=True, executable="/bin/bash")
        time.sleep(2) 
        
        if checkProcessIsRunning(screen_name):
            logger.info(f"[{runService.__name__}]: Screen session '{screen_name}' started successfully with Conda environment '{CONDA_VENV}'.")
        else:
            logger.warning(f"[{runService.__name__}]: Failed to start screen session '{screen_name}'. Check your command and environment setup.")

    except subprocess.CalledProcessError as e:
        logger.warning(f"[{runService.__name__}]: An error occurred while starting screen session '{screen_name}': \n{e.stderr or str(e)}\n")
    except Exception as e:
        logger.warning(f"[{runService.__name__}]: Unexpected error: {e}")
        
def runClient(service = None, core = None, queryString = {}):
    f""" a function to run the client for the analysis service.

    Args:
        service (str, optional): the analysis service to be performed. Defaults to None.
        core (str, optional): the name of the Solr core collection which will be updated. Defaults to None.
    """
    try:
        if service not in ApplicationConfig.ANALYSIS_SERVICES:
            logger.warning(f"[{runClient.__name__}-{service}]: Please specify the service to run: {' or '.join(ApplicationConfig.ANALYSIS_SERVICES)}.")
            return
        if core not in ApplicationConfig.SOLR_CORES:
            logger.warning(f"[{runClient.__name__}-{service}]: Please specify a valid Solr core for the {service} processing.")
            return
        screen_name = f"socioxplorer_{service}_{core}_client"
        if checkProcessIsRunning(screen_name):
            logger.info(f"[{runClient.__name__}-{service}]: Screen session '{screen_name}' is already running.")
            return
        else:
            conda_env = f"source $(conda info --base)/etc/profile.d/conda.sh && conda activate {CONDA_VENV}"
            client_path = LOCATION_CLIENT_PATH if service == 'location' else SENTIMENT_CLIENT_PATH
            
            qs = f"  -qs {json.dumps(queryString)}'" if queryString else "'"
            command = f"screen -dmS {screen_name} bash -c '{conda_env} && python3 {client_path} -c {core}{qs}"
            
            subprocess.Popen(command, shell=True, executable='/bin/bash')
                        
            if checkProcessIsRunning(screen_name):
                logger.info(f"[{runClient.__name__}-{service}]: Screen session '{screen_name}' started successfully.")
            else:
                logger.warning(f"[{runClient.__name__}-{service}]: Failed to start screen session '{screen_name}'. Check your command and environment setup.")

    except Exception as exp:
        logger.warning(f"[{runClient.__name__}-{service}]: An error occurred: \n{exp}\n")


def handleProcessing(service=None, core = None, queryString = {}):
    """A function to start the service API, it expects to get the service name and core name.

    Args:
        service (str, optional): the service name, the . Defaults to None.
        core (str, optional): _description_. Defaults to None.
    """
    if not service or service not in ApplicationConfig.ANALYSIS_SERVICES:
        logger.warning(f"[{handleProcessing.__name__}]: Please specify the service to run: {' or '.join(ApplicationConfig.ANALYSIS_SERVICES)}.")
        return
        
    if not core or core not in ApplicationConfig.SOLR_CORES:
        logger.warning(f"[{handleProcessing.__name__}-{service}]: Please specify the Solr core for the {service} processing.")
        return
    
    api_port = LOCATION_API_PORT if service == "location" else SENTIMENT_API_PORT
    if not isServiceRunning(api_port):
        logger.info(f"[{handleProcessing.__name__}]: {service.capitalize()} API is not running. Attempting to start it...")
        runService(service=service)
        time.sleep(5)
    else:
        logger.info(f"[{handleProcessing.__name__}]: {service.capitalize()} API is already running.")
    
    if isServiceRunning(api_port):
        logger.info(f"[{handleProcessing.__name__}]: Running {service.capitalize()} analysis client request for core '{core}'...")
        runClient(service=service, core=core, queryString=queryString)
    else:
        logger.warning(f"[{handleProcessing.__name__}]: {service.capitalize()} API is not running. The client service will not be started.")

def handleDataExtraction(dataSource, youTube=False):
    """Run the data extraction script on the specified data source.

    Args:
        dataSource (str): Path of the data source directory containing files to process.
        youTube (bool, optional): If True, uses the YouTube data extraction script. Defaults to False.
    """
    # Ensure the dataSource is a valid directory
    if not os.path.isdir(dataSource):
        logger.warning(f"[{handleDataExtraction.__name__}]: Invalid data source path: {dataSource}")
        return
    
    output_dir = f"{dataSource.rstrip('/')}_processed"
    logger.info(f"[{handleDataExtraction.__name__}]: Running system extraction script for dataSource: {dataSource}, and Output Directory: {output_dir}")

    # Select the appropriate script path
    script_path = YOUTUBE_DATA_EXTRACTION_SERVICE_PATH if youTube else DATA_EXTRACTION_SERVICE_PATH
    
    try:
        result = subprocess.run([f"python3 {script_path} -s {dataSource}  -o {output_dir}"], 
                                check=True, text=True, shell=True, executable='/bin/bash')
        logger.info(f"[{handleDataExtraction.__name__}]: Data extraction completed successfully.")

    except subprocess.CalledProcessError as exp:
        logger.warning(f"[{handleDataExtraction.__name__}]: Data extraction failed with error: {exp.stderr}")
    except Exception as exp:
        logger.warning(f"[{handleDataExtraction.__name__}]: An unexpected error occurred. {exp}")


def handleDataImportToSolr(core, dataSource,youTube=False):
    """A function to start importing the data to solr.

    Args:
        core (str): The name of the Solr core that the data will be imported to. 
        dataSource (str): the path of the data source to be imported.
        youTube (bool, optional): YouTube flag, to select the corresponding processing path for Twitter or YouTube. Defaults to False which means to process a Twitter core and data.
    """
    if core and core in ApplicationConfig.SOLR_CORES and dataSource:
        if not os.path.isdir(dataSource):
            logger.warning(f"[{handleDataImportToSolr.__name__}]: Invalid data source path: '{dataSource}' does not exist or is not a directory.")
            return
        
        screen_name = f"socioxplorer_solr_import_{core}"
        try:
            logger.info(f"[{handleDataImportToSolr.__name__}]: Running data import script for Core: {core}, and DataSource: {dataSource} and it is {'' if youTube else ' not '} YouTube data.")
            script_path = IMPORT_YOUTUBE_DATA_TO_SOLR_SERVICE_PATH if youTube else IMPORT_DATA_TO_SOLR_SERVICE_PATH
                        
            command = f'python3 {script_path}'
            result = subprocess.run(
                [f'python3 {script_path} -c {core} -s {dataSource}'],
                check=True, shell=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
            )
            logger.info(f"[{handleDataImportToSolr.__name__}]: Data import to Solr for core '{core}' completed successfully.")

        except subprocess.CalledProcessError as exp:
            logger.warning(f"[{handleDataImportToSolr.__name__}]: Data import script failed with error: {exp}")
        except Exception as exp:
            logger.warning(f"[{handleDataImportToSolr.__name__}]: Unexpected error in 'handleDataImportToSolr': {exp}")
      
def handleReProcessTopics(core, youTube=False, reProcessTopics=False):
    if core and core in ApplicationConfig.SOLR_CORES:
        screen_name = f"socioxplorer_process_topics_{core}"
        try:
            logger.info(f"[{handleReProcessTopics.__name__}]: Running data extract topics with{'out' if reProcessTopics else '' } reprocessing all data for Core: {core}.")

            script_path = TOPICS_EXTRACTION_PATH
            
            cmd_ = f"cd {script_path} && " if not os.path.exists(f"extract_text_data.py") else ""
            command = f"{cmd_} python3 extract_text_data.py -c {core}"
            subprocess.run(
                [command],
                check=True, shell=True, text=True, executable='/bin/bash'
            )
            logger.info(f"[{handleReProcessTopics.__name__}]: Data extraction for Topic analysis for core: '{core}' completed successfully.")
            
            command = f"{cmd_} python3 2_generate_sentence_embeddings.py -c {core} -a {reProcessTopics} --source-column text --model-name {ApplicationPaths.EMBEDDINGS_MODEL_PATH}"
            subprocess.run(
                [command],
                check=True, shell=True, text=True, executable='/bin/bash' # Raise an error if the subprocess fails
            )
            
        except subprocess.CalledProcessError as exp:
            logger.warning(f"[{handleReProcessTopics.__name__}]: topic modelling script failed with error: {exp}")
        except Exception as exp:
            logger.warning(f"[{handleReProcessTopics.__name__}]: Unexpected error in 'handleReProcessTopics': {exp}")



def handleReProcessSNA(core, youTube=False, reProcessSNA=False):
    if core and core in ApplicationConfig.SOLR_CORES:
        screen_name = f"socioxplorer_process_SNA_{core}"
        try:
            logger.info(f"[{handleReProcessSNA.__name__}]: Running SNA processing with{'out' if reProcessSNA else '' } reprocessing all data for Core: {core}.")

            script_path = NETWORK_INTERACTION_PATH
            
            # extract and process the data:
            cmd_ = f"cd '{script_path}'  && " if not os.path.exists(f"1_extract_network_from_solr.py") else ""
            command = f"{cmd_} python3 1_extract_network_from_solr.py -c {core} -a {reProcessSNA}"
            subprocess.run(
                command,
                check=True, shell=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
            )
            logger.info(f"[{handleReProcessSNA.__name__}]: Data extraction for Topic analysis for core: '{core}' completed successfully.")
    
            # import data to Solr
            command = f"{cmd_} python3 2_import_networks_to_solr.py -c {core} -i reply"
            subprocess.run(
                command,
                check=True, shell=True, capture_output=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
            )
            
            if not youTube:
                command = f"{cmd_} python3 2_import_networks_to_solr.py -c {core} -i retweet"
                subprocess.run(
                command,
                check=True, shell=True, capture_output=True, text=True, executable='/bin/bash'  # Raise an error if the subprocess fails
                )
                    
        except subprocess.CalledProcessError as exp:
            logger.warning(f"[{handleReProcessSNA.__name__}]: SNA script failed with error: {exp}")
        except Exception as exp:
            logger.warning(f"[{handleReProcessSNA.__name__}]: Unexpected error in 'handleReProcessSNA': {exp}")

    
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-tc', '--coreTwitter', help="Twitter core to be be processed", default=None)
    parser.add_argument('-td', '--twitterDataSource', help="The path of the Twitter data source so the system monitor.", default=None)
    parser.add_argument('-tqs', '--twitterQueryString', help="The setting for the queries.", default='')
    parser.add_argument('-yc', '--coreYouTube', help="The YouTube core to be processed", default=None)
    parser.add_argument('-yd', '--youtubeDataSource', help="The path of the YouTube data source so the system monitor.", default=None)
    parser.add_argument('-yqs', '--youtubeQueryString', help="The setting for the queries.", default='')
    try: 
        args = parser.parse_args()
        coreTwitter = args.coreTwitter
        twitterDataSource = args.twitterDataSource
        twitterQueryString = args.twitterQueryString if args.twitterQueryString else {}
        coreYouTube = args.coreYouTube
        youtubeDataSource = args.youtubeDataSource
        youtubeQueryString = args.youtubeQueryString if args.youtubeQueryString else {}
        
        try:
            twitterQueryString = json.loads(twitterQueryString) if twitterQueryString and len(twitterQueryString) > 0 else {}
        except Exception as queryStringExp:
            logger.info(f"[{__name__}][twitterQueryString]: An unexpected error occurred: {queryStringExp}")
            twitterQueryString = {}
        
        try:
            youtubeQueryString = json.loads(youtubeQueryString) if youtubeQueryString and len(youtubeQueryString) > 0 else {}
        except Exception as queryStringExp:
            logger.info(f"[{__name__}][youtubeQueryString]: An unexpected error occurred: {queryStringExp}")
            youtubeQueryString = {}
            
        logger.info(f"twitterQueryString: {twitterQueryString}")
        logger.info(f"youtubeQueryString: {youtubeQueryString}")
        
        twitterDataSource = twitterDataSource.rstrip('/') if twitterDataSource else twitterDataSource
        youtubeDataSource = youtubeDataSource.rstrip('/') if youtubeDataSource else youtubeDataSource
        
        
        logger.info(f"[{__name__}]: coreTwitter: {coreTwitter},\ttwitterDataSource: {twitterDataSource},\tcoreYouTube: {coreYouTube},\tyoutubeDataSource: {youtubeDataSource}")
        
        
        if not any([coreTwitter, coreYouTube]) or (coreTwitter and not twitterDataSource) or (coreYouTube and not youtubeDataSource):
            logger.error(f"[{__name__}]: Please specify both core and data source for each service. Example usage: python3 run_system.py -tc <coreTwitter> -td <twitterDataSource> -yc <coreYouTube> -yd <youtubeDataSource>")
            sys.exit(1)
            
        #If core is not registered in the system, exit.
        if not any([coreTwitter in ApplicationConfig.SOLR_CORES, coreYouTube in ApplicationConfig.SOLR_CORES]):
            logger.warn(f"[{__name__}]: Please specify a valid core, and confirm that the core is registered in the system. Please check the passed core is listed in the configuration file.")
            sys.exit(-1)
        
        logger.info(f"twitterDataSource: {twitterDataSource}")
        logger.info(f"youtubeDataSource: {youtubeDataSource}")
        
        
        
        if coreTwitter and twitterDataSource:
            handleDataExtraction(twitterDataSource, youTube=False)
            handleDataImportToSolr(coreTwitter, f"{twitterDataSource}_processed", youTube=False)
        
        
        if coreYouTube and youtubeDataSource:
            handleDataExtraction(youtubeDataSource, youTube=True)
            handleDataImportToSolr(coreYouTube, f"{youtubeDataSource}_processed", youTube=True)
        
        
        if coreTwitter:
            handleProcessing(service="sentiment", core=coreTwitter, queryString=twitterQueryString.get('rePreProcessData', None))
            handleProcessing(service="location", core=coreTwitter, queryString=twitterQueryString.get('rePreProcessData', None))
            
        if coreYouTube:
            handleProcessing(service="sentiment", core=coreYouTube, queryString=youtubeQueryString.get('rePreProcessData', None))
            handleProcessing(service="location", core=coreYouTube, queryString=youtubeQueryString.get('rePreProcessData', None))
        
        if twitterDataSource != None:
            logger.info(f"twitterQueryString.get('reProcessSNA', None): {twitterQueryString.get('reProcessSNA', None)}")
            handleReProcessTopics(coreTwitter, youTube=False, reProcessTopics=twitterQueryString.get('reProcessTopics', None))
            handleReProcessSNA(coreTwitter, youTube=False, reProcessSNA=twitterQueryString.get('reProcessSNA', None))
            
        if youtubeDataSource != None:
            logger.info(f"youtubeQueryString.get('reProcessSNA', None): {youtubeQueryString.get('reProcessSNA', None)}")
            handleReProcessTopics(coreYouTube, youTube=True, reProcessTopics=youtubeQueryString.get('reProcessTopics', None))
            handleReProcessSNA(coreYouTube, youTube=True, reProcessSNA=youtubeQueryString.get('reProcessSNA', None))
        
    except argparse.ArgumentError as exp:
        logger.error(f"[{__name__}]: Argument parsing error: {exp}")
        sys.exit(1)
    except Exception as exp:
        logger.error(f"[{__name__}]: An unexpected error occurred: {exp}")
        sys.exit(1)

if __name__ == "__main__":
    main()