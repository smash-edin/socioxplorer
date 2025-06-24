# SocioXplorer Project PreProcessing Modules

## Description

This section contains instructions for deploying the preprocessing modules for the "Social Contextual Intelligence and Observation for Exploration of Human Behavior in Digital Environments" (SocioXplorer) narratives analysis tool. It contains the following modules:

## Table of Contents

* [A. Before installation](#a-before-installation)
    * [Prerequisites](#1-prerequisites)
    * [Required data format](#2-required-data-format)
* [B. Installation](#b-installation)
    * [1. Installing dependencies](#1-installing-dependencies)
    * [2. Creating environment variables](#2-creating-environment-variables)
    * [3. Downloading and starting Solr](#3-downloading-and-starting-solr)
    * [4. Downloading models for offline use (Optional)](#4-downloading-models-for-offline-use-optional)
    * [5. Pre-processing the data](#4-pre-processing-the-data)
        * [a. Manual Updating](#a-manual-updating)
        * [b. Automatic Updating](#b-automatic-updating)
* [Additional Information](#additional-information)
    * [Configuration variables](#configuration-variables)
* [Credits](#credits)
* [License](#license)

## A. Before installation

### 1. Prerequisites

If you haven't done so already, make sure you have installed all prerequisite tools and services as specified on [the general README.md file](../README.md#a-installing-prerequisite-tools-and-services) of this repository (see **A. Installing Prerequisite Tools and Services** section).

## 2. Required data format

Make sure your data is in the correct format. The SocioXplorer system is designed to use data in the exact format (currently) returned by the Twitter API V2 (for Twitter data), or as returned by YouTube API (for YouTube data). If such "raw" (i.e. API-formatted) data is available, the system data extraction module should be able to process it and load it to Solr without issue. 

However, in case the "raw" data is not available (e.g. the data was previously pre-processed) then it must be provided as a list of dictionaries (JSON format) with a single dictionary per tweet/comment, and with each dictionary containing the required fields from the table below. Note that, as APIs evolve, the data received from Twitter/YouTube APIs may end up have different field names: e.g., favoriteCount may appear as like_count or favorite_count. In this case, the misnamed fields must be mapped to the field names listed in the table below for the system to function correctly. These fields must be available before processing.


|   **Field name**  |**Type** |                               **Description**                              |**Twitter**|**YouTube**|
|:-----------------:|:-------:|:--------------------------------------------------------------------------:|:---:|:---:|
| id	            | String  | The tweet’s/comment’s id                                                   |  Y  |  Y  |
| createdAt         | Date    | The timestamp of the creation. It is in the format: YYYY-MM-DDTHH:mm:ssZ|  Y  |  Y  |
| createdAtDays     | String  | The processed date of creation in the format: YYYY-MM-DD                      |  Y  |  Y  |
| favoriteCount     | Integer | The favorite counts (likes) the document has (from like_count).            |  Y  |  Y  |
| fullText          | String    | The text (of tweet or YouTube comment) as received from the platform       |  Y  |  Y  |
| hashtags          | List of Strings  | The hashtags as extracted from the document.                                 |  Y  |  Y  |
| inReplyToId       | String  | The original tweet/comment id, if this document is a reply to that original tweet/comment/video.|Y| Y |
| language          | String  | The identified language of the document.                                      |  Y  |  Y  |
| media             | List of Strings  | The links to media contents in the tweet.                                  |  Y  |     |
| mentions          | List of Strings  | The accounts mentioned in the tweet.                                       |  Y  |  Y  |
| placeCountry      | String  | The original geo location information of the tweet.                        |  Y  |     |
| placeFullName     | String  | The original geo location information of the tweet, which includes the full name.|  Y  |     |
| processedDescTokens| String | The processed words from the author’s description.                         |  Y  |  Y  |
| processedTokens   | List of Strings  | The processed words from the document. Which is a list of words after removing the URLs, mentions, hashtags and stopwords.|Y|Y|
| repliesTimes      | List of Strings  | The usernames and time stamp for the accounts replied to this tweet (separated with a space).| Y | Y |
| repliesTweets     | List of Strings  | The list of tweets’ ids of the tweets replied to this tweet.               |  Y  |     |
| replyCount        | Long    | The number of replies the document received.                        |  Y  |     |
| retweetCount      | Integer | The re-posting times (retweet) the tweet has.                               |  Y  |     |
| retweetTimes      | List of Strings  | The accounts retweeted this tweet including the date of retweeting (separated by a space).| Y  |     |
| retweeters        | List of Strings  | The accounts retweeted this tweet.                                         |  Y  |     |
| text              | String    | A copy of fullText field after removing the hashtags, mentions and URL.    |  Y  |  Y  |
| urls              | List of Strings  | The URLs included in the document.                                            |  Y  |  Y  |
| userId            | String  | The author’s unique identification number. It is unique and non-changeable.|  Y  |  Y  |
| userLocation      | String| The original location information in the account’s metadata.               |  Y  |     |
| userScreenName    | String  | The author’s screen name -the URL of X to the account and login username. It is unique but changeable.|Y|Y|
| usersDescription  | String    | The author’s description as included in the account’s metadata.            |  Y  |     |
| videoId           | String  | The id of the video.                                                       |     |  Y  |
| videoCreatedAt    | Date    | The timestamp of creating the Video. It is in the format: YYYY-MM-DDTHH:mm:ssZ|     |  Y  |


## B. Installation

### 1. Installing dependencies:

All the libraries needed by the `socioxplorer-backend` code can be installed with the following three steps:

1) Creating the virtual environment. Notice that this step is required only the first time you are installing the system on a machine. To create a virtual environment with the name `venv`, you can use the following command:

   ```
   conda create -n venv python=3.8.19
   ```

   Note: If you choose to use a different name than `venv` for your virtual environment, you will need to modify the `CONDA_VENV` configuration variable in the `configs.py` file (see the [Configuration variable](#configuration-variables) section below for more information on configuration variables).

2) After creating the virtual environment, you need to activate it. Please note that this is required every time you want to run any of the processes in this repository. You can activate the conda virtual environment `venv` by running the following command:

   ```
   conda activate venv
   ```

   For more details about handling the Conda virtual environments, please visit 
   [Managing environments from Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#).


3) Next, you need to install the required libraries. From inside the ***socioxplorer/socioxplorer-backend*** folder, run the following command for **Linux** and **Windows OS**:
   ```
   pip install -r requirements.txt
   ```

   ...and the following command for MacOS machines:
   ```
   pip install -r requirements_MacOS.txt
   ```

### 2. Creating environment variables

The system expects some environment variables to be set. You can do this easily by running the following command from the ***root*** folder of the SocioXplorer project as shown below:

```
python generate_codes.py
``` 

### 3. Downloading and starting Solr

At this point, please complete all the steps in the [Solr ReadMe.md](https://github.com/smash-edin/socioxplorer/tree/main/socioxplorer-backend/solr) file to download and start Apache Solr and create a new Solr core. Once you have done this, return here and continue.

Once the Solr core has been created, the system is ready to start processing data. The expected format for Twitter data is the Twitter API V2 format and must be stored as JSON file(s) in a given folder. The expected format for YouTube data is the one returned by the YouTube API and the data must be in two folders: one for YouTube comments and the other for video metadata.

**Note**: Adding cores **must** be done using the Solr controller module, as this will initiate the core with the required fields. We also highly recommend using this module for other Solr related operations. 


### 4. Downloading models for offline use (Optional)

The "Sentiment Analysis" and "Sentence Embeddings" pre-processing steps require using models from the internet. If accessing the internet is not an issue, you can ignore this instruction. However, if later on you will need to run the pre-processing steps off-line, please make sure to download the model weights into the desired folder as follows:

1. ***Sentiment Analysis***: We use the  twitter-XLM-roBERTa-base from [Cardiff NLP](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment). To use this model offline later on, please download its weights into the desired folder and update the `SENTIMENT_ANALYSIS_MODEL_PATH` variable in the `configs.py file` (see the [Configuration variable](#configuration-variables) section below for more information).

2. ***Sentence Embeddings***: The system uses [SBERT](https://sbert.net/) for the sentence modelling. By default the **`all-mpnet-base-v2`** model is used, however it can be swapped for the smaller **`paraphrase-MiniLM-L6-v2`** model if running the system with limited resources. Moreover, to use either of these models offline later on, please download their weights into the desired folder and update the `EMBEDDINGS_MODEL_PATH` variable in the `configs.py file` (see the [Configuration variable](#configuration-variables) section below for more information).


### 4. Pre-processing the data

The pre-processing modules of the SocioXplorer tool can be used in two ways. They can be used to ingest new data on demand: this usage is described in the "Manual Updating" section below. Or they can be configured to automatically ingest new data at regular intervals, as described in the "Automatic Updating" section below.

#### a. Manual Updating

The following steps describe how new data can be added to SocioXplorer on demand (i.e. as a "one off"). If this is your first time running the SocioXplorer tool and you have data you want to add, these are the steps you should follow. This "manual" approach is recommended if new data needs to be added to the system only occasionally and at irregular intervals.

**Step 1**: Adding documents (tweets/YouTube comments) to the Apache Solr instance

The following commands assume that you are in the terminal, inside the folder `socioxplorer/socioxplorer-backend/data_updater`.

1. ***Twitter data***:

    * **Extract relevant fields from raw Twitter data**: this step is **ONLY** required if your data is the raw output from the Twitter API V2 (for information about data format in the [**Required data format** section](#2-required-data-format) above). Otherwise simply move on to the **Upload data to Solr** step below. Assuming that your raw X (Twitter) data is stored as a set of files within a folder named `.sample_data` , run the following command from the `socioxplorer/socioxplorer-backend/data_updater/` folder:

      ```
      python 1_extract_data.py -s ../.sample_data/
      ```

      Please replace the path (`../sample_data`) with the path to your own data.

      The output of this step will be stored in a new folder that has the same name as the input folder, but with `_processed` added at the end. For example if the input folder is `../.sample_data`, then the results will be stored at `../.sample_data_processed/`.

      After this step, the files inside the source folder should be compressed. If the data is not compressed, then something has gone wrong when processing the Twitter source data.
      
      
      A sample of expected tweet objects is included in the root folder of this repository. To clarify the supported formats, we provide two example files:

      - `socioxplorer/sample_tweets.json`: Contains multiple JSON objects, each on a single line (newline-delimited JSON, or "JSONL" format).
      - `socioxplorer/sample_tweets2.json`: Contains multiple JSON objects, each possibly spanning multiple lines and formatted with indentation, as typically retrieved from the X (Twitter) platform API V2.
      
      These tweets were originally published on [X's developer's page](https://docs.x.com/x-api/posts/search/quickstart/full-archive-search) and in the article [Understanding the new Tweet payload in the Twitter API v2](https://dev.to/xdevs/understanding-the-new-tweet-payload-in-the-twitter-api-v2-1fg5). The system can process both formats automatically.

    * **Upload data to Solr**: from the same folder (`socioxplorer/socioxplorer-backend/data_updater/`), run the following command to upload the data into Solr:

      ```
      python 2_import_data_to_solr.py -c new_core -s ../.sample_data_processed/
      ```

      After this step, the files inside the processed data folder should be compressed. If the data is not compressed, then something has gone wrong when adding the processed Twitter data to Solr.

3. ***YouTube data***:

   * **Extract relevant fields from raw YouTube data**: this step is **ONLY** required if your data is the raw output from the YouTube API (for information about data format in the [**Required data format** section](#2-required-data-format) above). Otherwise simply move on to the **Upload data to Solr** step below. Assuming that your raw YouTube data is stored as a set of files within a folder named `.sample_youtube_data` , run the following command from the `socioxplorer/socioxplorer-backend/data_updater/` folder:

      ```
      python 1_extract_youtube_data.py -s ../.sample_youtube_data/
      ```

      Please replace the path (`../sample_youtube_data`) with the path to your own data.

      The output of this step will be stored in a new folder that has the same name as the input folder, but with `_processed` added at the end. For example if the input folder is `../.sample_youtube_data`, then the results will be stored at `../.sample_youtube_data_processed/`.

      After this step, the files inside the source folder should be compressed. If the data is not compressed, then something has gone wrong when processing the YouTube source data.

     * **Upload data to Solr**: from the same folder (`socioxplorer/socioxplorer-backend/data_updater/`), run the following command to upload the data into Solr:
     
      ```
      python 2_import_YouTube_data_to_solr.py -c new_core -s ../.sample_youtube_data_processed/
      ```

      After this step, the files inside the processed data folder should be compressed. If the data is not compressed, then something has gone wrong when adding the processed YouTube data to Solr.

**Step 2**: Processing the location details

1. **(Optional) Modify relevant configuration variables** in the `configs.py` file, i.e. `LOCATION_API_PORT`. For more information on configuration variables see the [Configuration Variables section](#configuration-variables) at this end of this file.

2. . ***Start the Location API Service***: To run the location process it is required to run the API. To perform that, follow these steps:

    1. Start a new terminal.

    2. Activate virtual environment with `conda activate venv` (replacing `venv` by the actual name of your virtual environment if different).

    3. Redirect the terminal to the folder `socioxplorer_backend/location_api`.
    
    4. Confirm the API resource configurations: If your machine is limited in resources, please reduce the resources required. To do so, please update the file `1_location_run.sh` to have the arguments as ***--workers=1 --thread 1***. Save the file and exit.

    5. Start the API: This can simply be done by executing the shell script `1_location_run.sh` in the `socioxplorer_backend/location_api` folder. To do this, please run the following command:

        ```
        ./1_location_run.sh
        ```

        > **Troubleshooting**: If the OS is unable to run the shell scripts (`.sh`), please try the following steps:
        >
        >  * Configuring the file to be executable with the following command: `chmod +x 1_location_run.sh`
        >  * Run the following command again: `./1_location_run.sh`
  
        
        > If this still does not work, try running the following command:
        > 
        > `gunicorn -b 0.0.0.0:10066 -t 1000 location_api:app --workers=2 --thread 4`
        >        
        > If your resources are limited, make sure to set the number of workers to 1 and thread to 1. The port number *10066* should be equal to the value of LOCATION_API_PORT in ***`configs.py`***.


3. ***Process the Locations***: Each time you want to run this step, please make sure that the location API is up and running. After starting the location API, you can process the locations by running the following command from the folder `socioxplorer/socioxplorer-backend/data_updater/`.

    ```
    python 3_update_locations.py -c new_core
    ```

    Or simply, configure the shell script `run_location_updater.sh` to have the desired core's name, and then run it by firing the command:


    ```
    ./run_location_updater.sh
    ```

    **Note**: The location process will take time to complete. It may take about 5~10 minutes to process about 10k to 20k documents. This depends on the resources available, whether you are using a GPU, number of workers and number of threads.


**Step 3**: Processing the Sentiments details

1. **(Optional) Modify relevant configuration variables** in the `configs.py` file, i.e. `SENTIMENT_ANALYSIS_MODEL_PATH` and `SENTIMENT_API_PORT`. For more information on configuration variables see the [Configuration Variables section](#configuration-variables) at this end of this file.

2. ***Start the Sentiment API Service***: A separate process is responsible for calculating the sentiment of tweets or YouTube comments. The following steps describe how to start this process. Note: This process needs to be running whenever you need to calculate sentiment (i.e. any time new data is ingested). Therefore, you will need to re-run these steps if for any reason the sentiment process has stopped running (e.g. because you have rebooted the machine).

    1. Start a new terminal window.

    2. Activate virtual environment with `conda activate venv` (replacing `venv` by the actual name of your virtual environment if different).

    3. In the Terminal, go to the folder `socioxplorer/socioxplorer-backend/sentiment_api/`.
    
    4. Confirm the configurations: If your machine is limited in resources, please reduce the resources required. To do so, please update the file `1_sentiment_run.sh` to have the arguments as ***--workers=1 --thread 1***. Save the file and exit.

    5. Start the API:

        Simply by executing the shell script `1_sentiment_run.sh` in the `socioxplorer_backend/sentiment_api` folder. To do this please fire the following command:

        ```
        ./1_sentiment_run.sh
        ```
  
        > **Troubleshooting**: If the OS is unable to run the shell scripts (`.sh`), please try the following steps:
        >
        >  * Configuring the file to be executable with the following command: `chmod +x 1_sentiment_run.sh`
        >  * Run the following command again: `./1_sentiment_run.sh`
  
        
        > If this still does not work, try running the following command:
        > 
        > `gunicorn -b 0.0.0.0:10077 -t 1000 analyser_main:app --workers=2 --thread 4`
        >        
        > If your resources are limited, make sure to set the number of workers to 1 and thread to 1. The port number *10077* should be equal to the value of SENTIMENT_API_PORT in ***`configs.py`***.
        
3. ***Process the sentiments***: Once the sentiment API is up and running (as explained in step 1), you can calculate sentiment for the data in `new_core` by running the following command from the folder `socioxplorer/socioxplorer-backend/data_updater/`.

    ```
    python 4_update_sentiments.py -c new_core
    ```

    Or simply configure the shell script `run_sentiment_updater.sh` with the desired core's name, and then run it by running the following command:

    ```
    ./run_sentiment_updater.sh
    ```

    **Note**: The sentiment process will take time to complete. It may take about 10~30 minutes to process about 10k to 20k documents. This depends on the resources available, whether you are using a GPU, the number of workers and threads available in the system. The system may look frozen for a period of time, but it is processing the sentiments in the Sentiment API.


**Step 4**: Obtaining embeddings representations of the data

1. **(Optional) Modify relevant configuration variables** in the `configs.py` file, i.e. `EMBEDDINGS_MODEL_PATH`, `EMBEDDINGS_DATA_DIR`, `EMBEDDINGS_DATA_FILE` and `BATCH_SIZE`. For more information on configuration variables see the [Configuration Variables section](#configuration-variables) at this end of this file.

2. ***Embeddings processing***: Redirect the terminal to the folder (**`socioxplorer/socioxplorer-backend/sentence_embeddings/`**) and then process the embeddings by performing the following steps:

    1.   If the virtual envrionment is not activated, activate it with `conda activate venv` (replacing `venv` by the actual name of your virtual environment if different).

    2.	Extract the text data from Solr by using the following command (still from the folder **`socioxplorer/socioxplorer-backend/sentence_embeddings/`**):

        ```
        python extract_text_data.py -c new_core
        ```

    3. Process the extracted data, and write it back to the Solr core by using the following command:

        ```
        python 2_generate_sentence_embeddings.py -c new_core
        ```
        
        > Under the hood, this command will perform the following steps in sequence, where the input for each command is the output of the previous one (you DO NOT need to run lines these yourself):
        >
        > 1. Generate sentence embeddings by calling `2_generate_sentence_embeddings.py`
        > 2. Reduce the dimensionality to 5d by calling `3_reduce_to_5d.py`
        > 3. Reduce the dimensionality to 2d by calling `4_reduce_to_2d.py`
        > 4. Update Solr with the embeddings by calling `5_import_embeddings_to_solr.py`

    
    * ***Note***: The embeddings process will take time to complete. It may take about 1 hour to process about 1 million documents. This depends on the resources available and whether you are using a GPU. 
    You may need to review the data inside the folder data inside the folder `sentence_embeddings`.


         > **Troubleshooting 1**: If you notice an error message regarding the Tensorflow and GPU, run the following command: `conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0`
         
         > **Troubleshooting 2**: The embedding classifier requires additional system resources to function properly. If you notice that the OS is killing the process due to resource constraints, consider the following options:
         > 1. Allocate More Resources: Increase CPU, RAM, or storage if possible.
         > 2. Optimise Resource utilisation by reducing memory and CPU usage as follows:
         >    * Set the `LIMITED_RESOURCE` flag in the ***`configs.py`*** file to True. By default, its value is set to False.
         >    * Reduce the value of `BATCH_SIZE` in the ***`configs.py`*** file. 1 is the minimum value you can use.


**Step 5**: Extracting the Social Network Analysis (SNA) information

1. ***Modify relevant configuration variables:*** Set the following configuration variables in the `configs.py` file (for more information on configuration variables see the [Configuration Variables section](#configuration-variables) at this end of this file):

    * ***SNA_DATA_DIR***: the directory where the data should be stored to.
    * ***SNA_DATA_FILE***: the file name where the data should be stored to.
    * ***SNA_TIMER***: the timer of the SNA algorithm to apply.
    * ***SNA_THRESHOLD***: the threshold of the minimum number of edges to cut-off the nodes from the network.


2. ***Extracting the network information from the data***: Run the following command from the **`socioxplorer/socioxplorer-backend/network_interaction`** folder to extract the social network information from the data: 

    ```
    python 1_extract_network_from_solr.py -c new_core
    ```
    
    ...where `new_core` should be replaced by the actual name of your Solr core.
   
    If the ***SNA_THRESHOLD*** configuration variable is too high, then the following error message will be printed:
      `Please reduce the interaction threshold to include more data by setting SNA_THRESHOLD value in configs.py file to lower value (minimum is 0).`

    You would then need to update the SNA_THRESHOLD value in the ***`configs.py`*** file.
   
    The output file, by default it is `socioxplorer/socioxplorer-backend/network_interaction/data/df_data_new_core.csv` (where `new_core` will be replaced by the actual name of your Solr core). This file will be the input for the next step.

    **Note**: This step may take some time.

    > **Troubleshooting 1**: This step uses Java code to extract network information from the data. If you encounter issues at this step, this might be due to the executable Java code (i.e. JAR file) we provide. You can try to solve the issue by compiling the Java source code yourself with the following command (from the folder **`socioxplorer/socioxplorer-backend/network_interaction`** folder):
    >
    > `javac -cp ./gephi-toolkit-0.10.0-all.jar Main.java GephiVis.java`

    > **Troubleshooting 2**: The following command should run automatically when you execute the `1_extract_network_from_solr.py` above. However, in case of any error, you can try running it yourself:
    >
    > `java -cp .:./gephi-toolkit-0.10.0-all.jar Main 10 ./data/df_data_new_core.csv`
    >
    > The output of this program will be written to a file similar to the path: `socioxplorer/socioxplorer-backend/network_interaction/data/df_data_GRAPH.json`. You will need to modify the output file name to `df_data_new_core.csv` (replacing `new_core` by the actual name of your Solr core).

    
    
2. ***Uploading network information to Solr***: Run the following command from the **`socioxplorer/socioxplorer-backend/network_interaction`** folder to upload the newly generated network information into your Solr core:

    * ***For YouTube data*** (it has reply interaction only):
    ```
    python 2_import_networks_to_solr.py -c new_core -i reply 
    ```
    * ***For Twitter data*** (it has both reply and retweet interactions):
    ```
    python 2_import_networks_to_solr.py -c new_core -i retweet
    ``` 
    and 
    ```
    python 2_import_networks_to_solr.py -c new_core -i reply 
    ```

#### b. Automatic Updating

The following steps describe how the system can be configured to ingest new data at regular intervals. Under this configuration, the system will monitor a given folder by checking it at regular intervals, determine if new data has been added to that folder and pre-process that data. 

The default configuration is to check for new data daily at 12:30 AM. To modify the timing, please update ***line number 96*** of the file `run_scheduler.py` inside the folder `socioxplorer/socioxplorer-backend/data_updater`. Below we explain the configuration of three different modes:

1. **To let the system run every day at 00:30**:

```
schedule.every().day.at("00:30").do(job, coreTwitter=coreTwitter, twitterDataSource=twitterDataSource, coreYouTube=coreYouTube, youtubeDataSource=youtubeDataSource, processingSettings=processingSettings)
```

2. **To let the system run every 20 minutes**:

(this time window is too short) - not recommended

```
schedule.every(20).minutes.do(job, coreTwitter=coreTwitter, twitterDataSource=twitterDataSource, coreYouTube=coreYouTube, youtubeDataSource=youtubeDataSource)
```

3. **To let the system run every 6 hours.**:

(this time window is moderate) - recommended if data updated more frequent and faster availability of the data is desired.

```
schedule.every(6).hours.do(job, coreTwitter=coreTwitter, twitterDataSource=twitterDataSource, coreYouTube=coreYouTube, youtubeDataSource=youtubeDataSource) 
```

### Running the system:

From the folder `socioxplorer/socioxplorer-backend/data_updater`, you can start the process that will check for and process any new Twitter data as follows:

```shell
python3 run_scheduler.py -tc twitter_core -td path_to_twitter_data
```

And for YouTube data:

```shell
python3 run_scheduler.py -yc youTube_core -yd path_to_youTube_data
```

The system will ingest new data, import it to Solr, and all relevant pre-processing tasks. the data extraction, importing to Solr and all other processing tasks at the desired interval.

The system supports simultaneous analysis of both YouTube and Twitter data with a single command that integrates information from both platforms, as shown below:

```shell
python3 run_scheduler.py -tc twitter_core -td path_to_twitter_data -yc youTube_core -yd path_to_youTube_data
```

NOTE: Please replace the Twitter core's name ***twitter_core*** and the path ***path_to_twitter_data*** in the commands above with the correct core name and the path to your Twitter data folder. The same applies to YouTube (***youTube_core*** and ***path_to_youTube_data***).




This concludes the pre-processing and setting up the data in Solr. The next step is to set up the dashboard, as described in [a separate README file](https://github.com/smash-edin/socioxplorer/blob/main/socioxplorer-frontend/README.md).


## Additional information

### Configuration variables
 
If needed, you can modify the following configuration variables in the `configs.py` file (see root folder of this repository). All these variables have default values so modifications might not be necessary:

1. ***CONDA_VENV*** : name of the virtual environment used in by the preprocessing modules of the system. The automatic update (see below) will use this name to automatically activate the conda environment. By default ***CONDA_VENV="venv"*** and this is the name we will be using in the installation instructions below (e.g. "Installing Conda environment").

2. ***SENTIMENT_ANALYSIS_MODEL_PATH***: the model of the sentiment analysis model. By default, this is set to `twitter-XLM-roBERTa-base`, which is a model from [Cardiff NLP](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment). Setting this variable to the model name will require internet access when running the system for the first time. To run the system without internet access (i.e. offline mode), you need to download the weights of the selected model to a local folder, and set the value of SENTIMENT_ANALYSIS_MODEL_PATH to the full path of that folder.

3. ***EMBEDDINGS_MODEL_PATH***: the model name of the sentence modelling model. By default, this is set to `all-mpnet-base-v2`, which is a model from [SBERT](https://sbert.net/). You can change this variable to `paraphrase-MiniLM-L6-v2`, which is another model from SBERT: this second model requires lower resources compared to the first model, making it better for low resources settings. Setting this variable to either model's name will configure the system to call them via an API, which will require an Internet access. To run the system without internet access (i.e. offline mode), you can download the weights of the selected model to a local folder, and set the value of `EMBEDDINGS_MODEL_PATH` to the full path of that folder. **Note**: The sentence modelling model needs to be accessible from both the ***socioxplorer/socioxplorer-backend/sentence_embeddings/*** and from ***socioxplorer/socioxplorer-frontend/api/***. We therefore recommend downloading the model to the root folder (***socioxplorer***) and setting `EMBEDDINGS_MODEL_PATH` equal to ***`../../all-mpnet-base-v2`*** if using the ***all-mpnet-base-v2*** model, or to ***`../../paraphrase-MiniLM-L6-v2`*** if using the ***paraphrase-MiniLM-L6-v2*** model. For more information regarding the models, please refer to the following resources: [https://huggingface.co/sentence-transformers](https://huggingface.co/sentence-transformers), [https://www.sbert.net/](https://www.sbert.net/)

6. ***LOCATION_API_PORT***: The port number used by the location API. By default, it is set to *10066*. If you change it here, you must also update the port number in 1_location_run.sh (located in the `socioxplorer_backend/location_api` folder) before running the location API.

7. ***SENTIMENT_API_PORT***: The port number used by the sentiment API. By default, it is set to *10077*. If you change it here, you must also update the port number in 1_sentiment_run.sh (located in the `socioxplorer_backend/sentiment_api` folder) before running the sentiment API.

8. ***EMBEDDINGS_DATA_DIR*** and ***EMBEDDINGS_DATA_FILE***: These paths point to where embeddings will be stored, with EMBEDDINGS_DATA_FILE being located inside EMBEDDINGS_DATA_DIR. By default ***EMBEDDINGS_DATA_DIR*** points to a folder called ***data*** and is located inside the folder defined by TOPICS_EXTRACTION_PATH.

7. ***LIMITED_RESOURCE***: A flag to configure where to run the system in low-resource mode. By default, this is set to False. To run in low resource mode, please switch to True.
        
8. ***BATCH_SIZE***: The batch size used when running the sentence modelling (i.e. to obtain embedding representations). By default, this is set to 100. If the system struggles to perform the task, you can reduce the batch size. 1 is the minimum value.

9. ***SNA_DATA_DIR***: The directory where the social network analysis data should be stored to. The default value is ***SNA_DATA_DIR='./data'***. The folder does not need to be created manually, as the system will generate it. However, the user must have write access to the disk.

10. ***SNA_DATA_FILE***: The file name where the social network analysis data should be stored to. The default value is ***SNA_DATA_FILE='df_data'***. The file and parent folder do not need to be created manually, as the system will create them. However, the user must have write access to the disk.

11. ***SNA_TIMER***: The number of minutes during which to run the Force Atlas 2 algorithm, which positions social media users spatially based on their interactions (replies/retweets) with other users. By default, this is ***SNA_TIMER=5***. If your dataset is large, ***please consider increasing the SNA_TIMER***, for instance to 60.

12. ***SNA_THRESHOLD***: minimum number of interactions (replies/retweets) that a social media account needs to have to be included in the dataset. This can be set to 0 to include all accounts, or any positive integer value. By default, this is set to 1. If you have a small network, consider setting it to 0 to include all the data. If your network is very large, you can increase the SNA_THRESHOLD to reduce the amount of computation required. Careful with setting it too high: If the value is too high for your network, you will have no data in the network. The system will show relevant messages in this case. Note: the SNA threshold should be identical at all steps as this affects the name of the output file. 


## Credits:

* ### [Gephi](https://gephi.org) 
    Bastian M., Heymann S., Jacomy M. (2009). Gephi: an open source software for exploring and manipulating networks. International AAAI Conference on Weblogs and Social Media.


## 📚 Citation

If you use this work, please cite:

```bibtex
@misc{your2025arxiv,
  author       = {Sandrine Chausson and Youssef Al Hariri and Walid Magdy and Bjorn Ross},
  title        = {SocioXplorer: An Interactive Tool for Topic and Network Analysis in Social Data},
  howpublished = {\url{https://arxiv.org/abs/xxxx.xxxxx}},
  year         = {2025},
  eprint       = {xxxx.xxxxx},
  archivePrefix = {arXiv},
  primaryClass = {cs.YY}
}