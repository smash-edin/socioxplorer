# SocioXplorer Dashboard

Welcome to the SocioXplorer Dashboard! This folder is composed of the following sub-folders: 


* **api**: Contains the code for the Flask API, which handles interactions with the Solr cores that contain the data. 
* **src**: contains the code for the React front-end.

The **docs** sub-folder inside **api** contains the HTML documentation for this API. You can download the docs folder and then open the file _build/html/index.html in your browser to navigate the documentation.


## Prerequisites Tools and Services

Before start with the interface, please check that your system has the following requirements:

1. **`yarn`**

    To check if you have `yarn` installed, run the following command:

    ```shell
    yarn --version
    ```
    The output should be similar to `1.22.22`

    To install yarn follow these two commands:
        
    ```shell
    nvm install 20.5.0
    npm install --global yarn
    ```


3. **Solr instance and core**: 
The present code assumes you already have a Solr core set up which indexes your pre-processed data. In the `socioxplorer/socioxplorer-backend`, we provided the code to perform the pre-processing and to control Solr instance. For more information about preparing the Solr instance and Solr cores, please refer to the Solr README.md in the `socioxplorer/socioxplorer-backend` folder. 


4. **Data from Social Media Platforms (Twitter or YouTube)**
The system handles data from either Twitter or YouTube, here are the fields that are expected to be indexed in Solr by the current project. Notice that not all fields are mandatory, as some are relevant to Twitter and others are for YouTube. However, the column Required in the following table shows the required fields that are expected so all functionalities are working properly: 


|   **Field name**  |**Type** |                               **Description**                              | **Required**  |**Twitter**|**YouTube**|
|:-----------------:|:-------:|:--------------------------------------------------------------------------:|:-------------:|:---:|:---:|
| id	            | String  | The tweet’s/comment’s id                                                   | 	   Y	   |  Y  |  Y  |
| createdAt         | Date    | The date-time of tweets creation. It is in the format: YYYY-MM-DDTHH:mm:ssZ| 	   Y	   |  Y  |  Y  |
| createdAtDays     | String  | The date of tweets creation in the format: YYYY-MM-DD                      | 	   Y	   |  Y  |  Y  |
| embedding_2d      | List of Float   | 2D Embeddings data                                                         | 	   Y	   |  Y  |  Y  |
| embedding_5d      | List of Float   | 5D Embeddings data                                                         | 	   Y	   |  Y  |  Y  |
| emojis            | List of Strings  | The emojis in the tweet                                                    | 	   Y	   |  Y  |  Y  |
| favoriteCount     | Integer | The favorite counts (likes) the tweet has.                                | 	   Y	   |  Y  |  Y  |
| fullText          | String    | The tweet’s text as received from Twitter                                  | 	   Y	   |  Y  |  Y  |
| hashtags          | List of Strings  | The hashtags in the tweets.                                                | 	   Y	   |  Y  |  Y  |
| inReplyToId       | String  | The original tweet/comment id, if this document is a reply to that original tweet/comment/video.||Y| Y |
| language          | String  | The identified language of the tweet.                                      | 	   Y	   |  Y  |  Y  |
| media             | List of Strings  | The links to media contents in the tweet.                                  | 	   Y	   |  Y  |     |
| mentions          | List of Strings  | The accounts mentioned in the tweet.                                       | 	   Y	   |  Y  |  Y  |
| placeCountry      | String  | The original geo location information of the tweet.                        | 	   Y	   |  Y  |     |
| placeFullName     | String  | The original geo location information of the tweet, which includes the full name.| Y       |  Y  |     |
| processedDescTokens| List of Strings | The processed words from the author’s description.                         | 	   Y	   |  Y  |  Y  |
| processedTokens   | List of Strings  | The processed words from the tweet. Which is a list of words after removing the URLs, mentions, hashtags and stopwords.|Y|Y|Y|
| repliesTimes      | List of Strings  | The usernames and time stamp for the accounts replied to this tweet.       | 	   Y	   |  Y  |  Y  |
| repliesTweets     | List of Strings  | The list of tweets’ ids of the tweets replied to this tweet.               | 	   Y	   |  Y  |     |
| replyCommunity    | Integer | The community label of the reply interaction as extracted from the communities clustering module.|Y|Y|Y |
| replyCount        | Long    | The number of tweets as replies the tweet received.                        |       Y       |  Y  |     |
| replyNetworkNodes | List of Strings  | The reply nodes extracted from the repliesTimes filed.                     | 	   Y	   |  Y  |  Y  |
| retweetCommunity  | Integer | The community label of the retweet interaction as extracted from the communities clustering module.|Y|Y|Y|
| retweetCount      | Integer | The re-posting times (retweet) the tweet has.                               | 	   Y	   |  Y  |     |
| retweetNetworkNodes| List of Strings | The retweet nodes as listed in the retweetTimes and retweeters.            | 	   Y	   |  Y  |     |
| retweetTimes      | List of Strings  | The accounts retweeted this tweet including the date of retweeting.        | 	   Y	   |  Y  |     |
| retweeters        | List of Strings  | The accounts retweeted this tweet.                                         | 	   Y	   |  Y  |     |
| sentiment         | String  | The sentiment label                                                        | 	   Y	   |  Y  |  Y  |
| text              | String    | A copy of full_text field with hashtags, mentions and URL removed.         | 	   Y	   |  Y  |  Y  |
| urls              | List of Strings  | The URLs included in the tweet.                                            |       Y       |  Y  |  Y  |
| userId            | String  | The author’s unique identification number. It is unique and non-changeable.| 	   Y	   |  Y  |  Y  |
| userLocation      | String| The original location information in the account’s metadata.               | 	   Y	   |  Y  |     |
| userScreenName    | String  | The author’s screen name -the URL of X to the account and login username. It is unique but changeable.|Y|Y|Y|
| usersDescription  | String   | The author’s description as included in the account’s metadata.            | 	   Y	   |  Y  |  Y  |
| usersLocation     | String  | The extracted location of the account as described in the account’s metadata.|    Y       |  Y  |     |
| locationGps       | String  | The extracted location of the account as described in the tweet’s metadata.|    Y         |  Y  |     |
| videoId           | String  | The id of the video.                                                       | 	   Y	   |     |  Y  |
| videoCreatedAt    | Date    | The date and time of creating the Video. It is in the format: YYYY-MM-DDTHH:mm:ssZ|   Y    |     |  Y  |


Some of these fields are directly extracted from the documents (i.e. tweets or YouTube comments), while others are processed by the socioxplorer-backend. The Main processed fields are:
1) **language** field is obtained by the FastText language detection model applied on the data during the processing, 
2) **sentiment** by running the sentiment analysis classifier, 
3) Communities fields are extracted by running the network_interaction to extract:
    1. **replyCommunity** and **retweetCommunity** by the louvain community detection model, 
    2. **retweetNetworkNodes** and **replyNetworkNodes** by the [ForceAtlas2](https://gephi.wordpress.com/2011/06/06/forceatlas2-the-new-version-of-our-home-brew-layout/) implemented by [Gephi](https://gephi.org/), 
4) **embedding_5d** and **embedding_2d** by running first the [SBERT](https://sbert.net/) language model to obtain a large embedding representation and then running the UMAP algorithm to reduce the dimensions of these embeddings to 5 and then 2 dimensions.
5) **userLocation** and **locationGps** which are extracted from the location details from the documents' metadata.



Once the Solr cores are set up with the correct fields indexed, you can follow the following steps to run the dashboard on your local machine.

## Setting up project on local machine for development

To set up the project after cloning the repository:

1) Confirm that *SOLR_URL*, *SOLR_PORT* and *SOLR_CORES* fields in configs.py file in the root folder of this repo to point to your own Solr set up.

2) Install Javascript dependencies (only first time you install the system) so, from the root folder of the `socioxplorer`, type the following:
```
cd socioxplorer-frontend
yarn install
```

if you face issue with the version, you can check with yarn version 20.5.0
```
nvm install 20.5.0
```

Note: You may need to uninstall the previous versions of the nvm by the command `nvm uninstall 20` several times, which depends on the number of times these versions were installed.

Then make sure to install node:

```
npm install -g n
```

3) Create Python virtual environment and install dependencies (only first time you install the system):
```
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

In this example we use venv as virtual environment. If you want to change this name, please update the line with the value (`"start-api": "cd api && venv/bin/flask run --no-debugger"`) from the file ***`package.json`*** by replacing the ***venv*** with the name of your selected virtual environment name. For example you can name it my_env: (python3 -m venv my_env) or fanotm (python3 -m venv fanotm). However, you need to update  the commands we used here with venv to use your virtual environment.

If there is an error related to the Python 3.8 version, you can try the following solution, assuming that the `socioxplorer/socioxplorer-backend` installation steps have already been performed in the system and the conda environment `venv` is already created (internet access required) - (only first time you create the virtual environment in the system):

```
cd api
conda activate venv
pip install virtualenv
virtualenv -p $(which python3.8) venv
conda deactivate
source venv/bin/activate
pip install -r requirements.txt
```

Again, in this example we use `venv` as the name of our virtual environment. If you want to change this name, please update the line with the value (`"start-api": "cd api && venv/bin/flask run --no-debugger"`) in the file ***`package.json`*** in the folder ***`/socioxplorer/socioxplorer-frontend/`*** by replacing ***venv*** with the name of your virtual environment.


4) Launch React app:


From the folder `socioxplorer/socioxplorer-frontend/`, run the following command:
```
yarn start # you should be at the folder socioxplorer/socioxplorer-frontend once again
```

Note: Your system may have access restrictions, so you might need to run the commands with sudo as shown below:
```
sudo yarn start
```

Warning messages about the React hooks is expected and it should not affect the system. Please note that you need to make sure the virtual environment is loaded before running this command.

5) Launching Flask back-end (in a new terminal):

From the root folder `socioxplorer/`, run the following command:
```
cd socioxplorer-frontend
cd api
source venv/bin/activate
cd ..
yarn start-api
```

Please note that you need to make sure that the virtual environment is loaded before running the command (***yarn start-api***) (as it is shown in the code snippet). After running this command and before using the interface, you should see the message `System is ready`.

Note: Your system may have access restrictions, so you might need to run the commands with sudo, as shown below:

```
cd socioxplorer-frontend
cd api
source venv/bin/activate
cd ..
sudo yarn start-api
```


6) Access the app from http://localhost:3000/ in your browser

The system should be up and running.



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