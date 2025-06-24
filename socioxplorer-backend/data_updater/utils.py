## -*- coding: utf-8 -*-

import requests
import time
import json
from ftlangdetect import detect
import re
import sys
import nltk
from os import makedirs, mkdir, remove
from os.path import split, join, exists, isfile, abspath, splitext
import datetime
import logging
import emoji
import pandas as pd
from dateutil import parser
import time

def parse_date(date_str):
    """Parse date dynamically from different formats."""
    try:
        return parser.parse(date_str)  
    except ValueError:
        return None
    
def format_date(parsed_date, fmt):
    """Format parsed date into the desired format."""
    return parsed_date.strftime(fmt) if parsed_date else None

try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler
import html2text
import traceback
import glob
import string
from nltk.tokenize import TweetTokenizer
import subprocess
tweet_tokenizer = TweetTokenizer()

LOG_FOLDER = ApplicationConfig.LOG_FOLDER
LANGUAGE_DICT = ApplicationConfig.LANGUAGE_DICT
LANGUAGE_DICT_INV = ApplicationConfig.LANGUAGE_DICT_INV

def print_this(message):
    """
    An auxiliary function that prints a message within a square of (hash)s.
    
    Args:
        :message: (obj) The message to be printed, preferably a string.
    """
    len_message = min(80, len(f"## {message} ##"))
    print('#'*len_message + f'\n## {message} ##\n' + '#'*len_message)


class TimedRotatingFileHandler(_TimedRotatingFileHandler):
    """
    A class to manage the backup compression.
    Args:
        _TimedRotatingFileHandler ([type]): The TimedRotatingFileHandler from loggin.handlers library.
    """
    def __init__(self, filename="", when="midnight", interval=1, backupCount=0):
        super(TimedRotatingFileHandler, self).__init__(
            filename=filename,
            when=when,
            interval=int(interval),
            backupCount=int(backupCount))
    
    def doRollover(self):
        super(TimedRotatingFileHandler, self).doRollover()


def create_logger(name, level=logging.INFO, file=None):
    '''
    A function to log the events. Mainly used to manage writing to log file and to manage the files compression through TimedRotatingFileHandler class.
    
    Parameters
    ----------
    name : String
        Logger name.
    level : optional.
        level of logging (info, warning). The default is logging.INFO.
    file : String, optional
        File name, the name of the logging file. The default is None where no compression will be set in file is None.

    Returns
    -------
    logger after creation.
    '''
    name = name.replace('__','')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logging_formatter = logging.Formatter(
        '[%(asctime)s - %(name)s - %(levelname)s] '
        '%(message)s',
        '%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging_formatter)
    logger.addHandler(ch)
    
    
    # Check whether the specified path exists or not
    if not exists(LOG_FOLDER):
        makedirs(LOG_FOLDER)
    if file:
        file_handler = TimedRotatingFileHandler(filename=f"../.log/{file}.log", when='midnight', interval=1, backupCount=0)#when midnight, s (seconds), M (minutes)... etc
        file_handler.setFormatter(logging_formatter)
        logger.addHandler(file_handler)
    return logger

def write_data_to_file(tweets, file_name, folder = None):
    """A function to write data into a file

    Args:
        tweets (Dict or List): the dictionary of the tweets with their extracted information.
        file_name (str): the file name in which the data will be writen to.
        folder (str): the folder in which the file will be written to.
    """
    if folder != None:
        if not exists(f'../{folder}'):
            mkdir(f'../{folder}')
        with open(f'../{folder}/{file_name}','a+',encoding='utf-8') as fout:
            if type(tweets) == dict:
                for k in tweets.keys():
                    fout.write('%s\n'%json.dumps(tweets[k], ensure_ascii=False))
            elif type (tweet) == list:
                for tweet in tweets:
                    fout.write('%s\n'%json.dumps(tweet, ensure_ascii=False))
    else:
        with open(file_name,'a+',encoding='utf-8') as fout:
            if type(tweets) == dict:
                for k in tweets.keys():
                    fout.write('%s\n'%json.dumps(tweets[k], ensure_ascii=False))
            elif type (tweets) == list:
                for tweet in tweets:
                    fout.write('%s\n'%json.dumps(tweet, ensure_ascii=False)) 

def get_sentiments(tweets):
    """A function to access sentiment analysis service.

    'id': tweet['id'], "fullText": item["fullText"], "language"

    Args:
        tweets (dict): A dictionary of the tweets object. It should have the following keys:
        1) 'id': tweet id, 
        2) 'fullText': the fullText of the tweet,
        3) 'language': the detected language of the tweet.

    Returns:
        dict: A dictionary that hold the sentiment information as retrived from its service. The keys are the tweets ids and values are dicts that contain:
        'sentiment' : the sentiment information as being analysed from the text, (positive, nuetral or negative)
        'sentimentDistribution' : a list that has the distribution of the three sentiments (the highest would be at the index of the selected sentiment)
    """
    headers = {'content-type': 'application/json; charset=utf-8'}
    url_sent = ApplicationConfig.SA_URL
    data = json.dumps(tweets, ensure_ascii=False)
    rs = -1
    try:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('Send to SA; Current Time =', current_time)
        response = requests.post(url=url_sent, headers = headers , data=data.encode('utf-8'))
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('SA finished; Current Time =', current_time)
        rs = response.status_code
    except Exception:
        pass
        
    if rs != 200:
        print('Sentiment analyzer not working!.. Error code: ' + str(rs))
        logger.warning(f'[get_sentiments]: Sentiment analyzer not working!.. Error code: {str(rs)}')
        time.sleep(3)
        # only update if the sentiment api running and accessible.
        return None
    return json.loads(response.content)
    
    
def get_language(tweet_text):
    """function to extract the language of the passed string.
    It is based on fasttext language identification and uses the libraries (fasttext, re) in python.
    Proceudre:
        1- remove urls and mentions
        2- remove the numbers
        3- predict the language
        4- in case of errors, return english with 0 confidence.
    Args:
        tweet_text (str): The string that you need to find its language.

    Returns:
        language (str): The string that contains the identified language. examples: 'english' or 'spanish'
    """
    try:
        tweet_text = re.sub('http[s]:[^\b \n\t]+',' ',tweet_text)
        tweet_text = re.sub('@[^\b \n\t]+',' ',tweet_text)
        tweet_text = re.sub('[0-9]+',' ',tweet_text)
        tweet_text = re.sub('[\n\t ]+',' ',tweet_text).strip()
        if len(tweet_text.split(' ')) >= 1 and len(tweet_text) > 1:
            lang = detect(text=tweet_text, low_memory=False)
            if len(lang) >= 1:
                language = str(lang['lang'])
                return LANGUAGE_DICT[language] if language in LANGUAGE_DICT.keys() else language
            else:
                return 'NonText'
        else:
            return 'NonText'
    except Exception as exp:
        print(exp)
        time.sleep(1)
        return 'lang' #if exception occurred, set language to lang. (traceable for future works)

def get_urls_from_object(tweet_obj):
    """Extract urls from a tweet object

    Args:
        tweet_obj (dict): A dictionary that is the tweet object, extended_entities or extended_tweet

    Returns:
        list: list of urls that are extracted from the tweet.
    """
    url_list = []
    if "entities" in tweet_obj.keys():
        if "urls" in tweet_obj["entities"].keys():
            for x in tweet_obj["entities"]["urls"]:
                try:
                    url_list.append(x["expanded_url"]  if "expanded_url" in x.keys() else x["url"])
                except Exception:
                    pass
    return url_list


def extractMediaContentsFromDict(items=None, media_dict=dict()):
    """Extract media objects from a file
    Args:
        file (str): The path of the file.
        media_dict (dict): A dictionary that is the media objects.
    Returns:
        media_dict (dict): The updated dictionary that is the media objects.
    """
    if items:
        for item in items:
            try:
                if item['media_key'] not in media_dict.keys():
                    if 'url' in item.keys():
                        media_dict[item['media_key']] = item
            except Exception as exp:
                handleException(exp,item,__name__)
    return media_dict

def getMediaFromObject(media_dict, media_keys):
    """Extract urls from a tweet object
    Args:
        media_keys (dict): A dictionary that holds the media_keys
    Returns:
        list: list of the media urls that are extracted from the tweet.
    """
    media_list = []
    try:
        for item in media_keys:
            if item in media_dict.keys():
                item_ = media_dict[item]
                if "url" in item_.keys():
                    media_list.append(item_['url'])
    except Exception as exp:
        pass
    return media_list

def getPlatform(source = '<PLT_1>'):
    """A function to extract the platform from a source string.
    Args:
        source (str, optional): source string that is usually contains the platform that is used to post the tweet. Defaults to '<PLT_1>'.
    Returns:
        str: the platform if found, otherwise the stamp PLT_1. This stamp is used for any further updates.
    """
    platform = ''
    try:
        platform = re.sub('[<>]', '\t', source).split('\t')[2]
        platform = platform.replace('Twitter for','').replace('Twitter','')
    except:
        platform = ''
    return platform.strip()


        

def get_location(tweets):
    """A function to access location service.

    Args:
        tweets (dict): A dictionary of the tweets object. It should have the following keys:
        1) 'id': tweet id, 
        2) 'user': the user object as exists in the tweet object,
        3) 'geo': the geo field from the tweet,
        4) 'coordinates': the coordinates field from the tweet, 
        5) 'place': the place field from the tweet, 
        6) 'language': the detected language of the tweet.

    Returns:
        dict: A dictionary that hold the location information as retrived from location service. The keys are the tweets ids and values are dicts that contain
        'user' : the location information from user object
        'tweet' : the location information from the tweet object (locationGps)
        'language' (optional): the location as extracted from the tweets' language
    """
    url1 = ApplicationConfig.LOCATION_URL
    data = json.dumps(tweets,ensure_ascii=False)
    headers = {'content-type': 'application/json; charset=utf-8'}
    # sending get request and saving the response as response object
    rs = -1
    trials = 1
    while (rs != 200 and trials <= 3):
        try:
            response = requests.post(url=url1, data=data.encode('utf-8'), headers=headers)
            rs = response.status_code
        except Exception as exp:
            print(exp)
            rs = -1
        finally:
            trials += 1
    if rs != 200:
        logger.warning(f'[get_location]: Location service not found. Error code: ' + str(rs))
        # return None, to only update if the location api running and accessible.
        return None
    return json.loads(response.content)

def extract_raw_responses(json_response, filename = None, OUTPUT_FOLDER=None):
    try:
        tweets = None
        users = None
        includes = None
        places = None
        media = None
        poll = None
        matching_rules = None

        if 'matching_rules' in json_response.keys():
            matching_rules = [x['tag'] for x in json_response['matching_rules']]

        tweets = json_response['data'] if 'data' in json_response.keys() else None
        if tweets:
            if matching_rules:
                tweets['matching_rules'] = list(set(tweets['matching_rules'] + matching_rules)) if 'matching_rules' in tweets.keys() else list(set(matching_rules))

        if 'includes' in json_response.keys():
            users = json_response['includes']['users'] if 'users' in json_response['includes'].keys() else None
            includes = json_response['includes']['tweets'] if 'tweets' in json_response['includes'].keys() else None
            if includes:
                for item in includes:
                    if matching_rules:
                        item['matching_rules'] = list(set(item['matching_rules'] + matching_rules)) if 'matching_rules' in item.keys() else list(set(matching_rules))

            places = json_response['includes']['places'] if 'places' in json_response['includes'].keys() else None
            media = json_response['includes']['media'] if 'media' in json_response['includes'].keys() else None
            poll = json_response['includes']['poll'] if 'poll' in json_response['includes'].keys() else None


        if OUTPUT_FOLDER and filename:

            writeDataToFile(tweets, 'tweets_'+filename, OUTPUT_FOLDER)
            writeDataToFile(users, 'users_'+filename, OUTPUT_FOLDER)
            writeDataToFile(includes, 'includes_'+filename, OUTPUT_FOLDER)
            writeDataToFile(places, 'places_'+filename, OUTPUT_FOLDER)
            writeDataToFile(media, 'media_'+filename, OUTPUT_FOLDER)
            writeDataToFile(poll, 'poll_'+filename, OUTPUT_FOLDER)
        else:
            return tweets, users, includes, places, media, poll

    except Exception as exp:
        handleException(exp, object_=json_response, func_=f'\n{__name__}')

def getEmotion(text = ''):
    """
    -- Not implemented yet --
    A function to extract the emotion from a text string.
    Args:
        text (str, optional): text string of the tweet. Defaults to ''.
    Returns:
        str: the emotion.
    """
    return ''

def extractResponseContentsFromDict(items=None, objects_dict=dict()):
    if items:
        for item in items:
            try:
                if 'id' in item.keys():
                    if item['id'] not in objects_dict.keys():
                        objects_dict[item['id']] = item
            except Exception as exp:
                handleException(exp,item,__name__)
    return objects_dict

def getEmojis(text):
    try:
        emojis = emoji.distinct_emoji_list(text.encode('utf-16', 'surrogatepass').decode('utf-16'))
    except Exception as exp:
        emojis = emoji.distinct_emoji_list(text)
    finally:
        return emojis

def getCleanedText(text, lower = False):
    """ a function to clean the text from special characters and preserve the punctuation. It uses the TweetTokenizer from nltk.
    The case of the text is preserved. The special characters are replaced with space unless they are punctuation.

    Args:
        text (str): The text that you need to clean. 

    Returns:
        str: The cleaned version of the text. We use the TweetTokenizer from nltk to tokenize the text. The selected option is to keep the puctuation of the text (i.e. preserve the punctuation in terms such as item's and you're).
    """
    text = text.replace('’', "'").replace('‘', "'").replace('“','"').replace('”','"') #replace special characters to preserve the punctuation.
    if lower:
        text = text.lower()
    t = ' '.join([x for x in tweet_tokenizer.tokenize(text) if not x.startswith('@') and not x.startswith('#') and not x.startswith('http') and x not in string.punctuation])
    return re.sub("[•!?;,/’‘&%\"\t\n.....； ]+"," ", t)

def getCleanedTextList(text, alpha_numeric_only = False, lower = False):
    """ a function to clean the text from special characters while preserving the punctuation.
    The case of the text is preserved. The special characters are replaced with space unless they are punctuation.
    The mentions, hashtags and urls are removed from the text. The text is tokenized by calling the function :func:`getCleanedText` and the tokens are cleaned from special characters.
    The function returns a list of the cleaned words/tokens.

    Args:
        text (str): The text that you need to clean. 
        alpha_numeric_only (bool, optional): A flag to keep only the alpha numeric characters (i.e. remove the special characters). Defaults to False.
        lower (bool, optional): A flag to convert the text to lower case. Defaults to False.

    Returns:
        str: The cleaned version of the text. We use the TweetTokenizer from nltk to tokenize the text. The selected option is to keep the puctuation of the text (i.e. preserve the punctuation in terms such as item's and you're).
    """
    try:
        if alpha_numeric_only:
            return [x for x in set(getCleanedText(text, lower).split(' ')) if x.isalnum()]
        return getCleanedText(text, lower).split(' ')
    except Exception as exp:
        return ""

def handleException(exp, object_='Unknown', func_= 'Unknown'):
    print(f'Error {exp}\n')
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    
    print(f"------------------------------------------------\nException type: {exception_type}\n \
        Line number: {line_number}.\nexception_object: {exception_object}\n \
            Exception message : {exp}\nObject: {object_}\nFunction: {func_}.\
                \n================================================")
                
def getTweetContent(object_, original, users_dict, places_dict, media_dict):
    tweet_ = dict()

    author_id = object_['author_id']
    public_metrics = object_['public_metrics'] if 'public_metrics' in object_.keys() else {}
    author_location = 'not_available'
    verified = ''
    protected = ''
    userName = ''
    userScreenName = ''
    usersDescription = ''
    usersFollowersCount = None
    usersFriendsCount = None
    placeCountry = ''
    placeFullName = ''
    locationGps = None
    if 'geo' in object_.keys():
        if 'place_id' in object_['geo'].keys():
            place_id = object_['geo']['place_id']
            if place_id in places_dict.keys():
                if 'full_name' in places_dict[place_id].keys():
                    placeFullName = places_dict[place_id]['full_name']
                if 'country' in places_dict[place_id].keys():
                    placeCountry = places_dict[place_id]['country']

    if placeFullName == "" and placeCountry == "":
        locationGps = 'not_available'

    if  author_id in users_dict.keys():
        user_obj =  users_dict[author_id]
        if 'location' in user_obj.keys():
            author_location = user_obj['location']
        if 'verified' in user_obj.keys():
            verified = user_obj['verified']
        if 'protected' in user_obj.keys():
            protected = user_obj['protected']
        if 'screen_name' in user_obj.keys():
            userScreenName = user_obj['screen_name']
        elif 'username' in user_obj.keys():
            userScreenName = user_obj['username']
        if 'name' in user_obj.keys():
            userName = user_obj['name']
        if 'description' in user_obj.keys():
            usersDescription = user_obj['description']
        if 'public_metrics' in user_obj.keys():
            if 'followers_count' in user_obj['public_metrics'].keys():
                usersFollowersCount = user_obj['public_metrics']['followers_count']
        if 'public_metrics' in user_obj.keys():
            if 'following_count' in user_obj['public_metrics'].keys():
                usersFriendsCount = user_obj['public_metrics']['following_count']

    media_keys = []
    if "attachments" in object_.keys():
        if "media_keys" in object_["attachments"].keys():
            media_keys = getMediaFromObject(media_dict,object_["attachments"]["media_keys"])

    urls = get_urls_from_object(object_)
    fullText = object_['text'] if 'text' in object_.keys() else object_['fullText'] if 'fullText' in object_.keys() else object_['full_text'] if 'full_text' in object_.keys() else ''

    date_str = object_.get("createdAt") or object_.get("created_at")
    parsed_date = parse_date(date_str)

    tweet_ = {'id':object_['id'],
              'createdAt':format_date(parsed_date, "%Y-%m-%dT%H:%M:%SZ"),
              'createdAtDays':format_date(parsed_date, "%Y-%m-%d"),
              'createdAtMonths':format_date(parsed_date, "%Y-%m"),
              'createdAtYears':format_date(parsed_date, "%Y"),
              'emotion': getEmotion(fullText),
              'favoriteCount': public_metrics['like_count'] if 'like_count' in public_metrics.keys() else public_metrics['likeCount'] if 'likeCount' in public_metrics.keys() else None,
              'fullText': fullText,
              'hashtags':[x.replace('#','') for x in tweet_tokenizer.tokenize(fullText) if x.startswith('#')],
              'mentions':[x.replace('@','') for x in tweet_tokenizer.tokenize(fullText) if x.startswith('@')],
              'languagePlatform': LANGUAGE_DICT[object_['lang']] if object_['lang'] in LANGUAGE_DICT.keys() else object_['lang'],
              'language': get_language(fullText),
              'possiblySensitive': object_['possiblySensitive'] if 'possiblySensitive' in object_.keys() else object_['possibly_sensitive'] if 'possibly_sensitive' in object_.keys() else None,
              'placeCountry': placeCountry,
              'placeFullName': placeFullName,
              'userId':author_id,
              'locationGps': locationGps,
              'userLocationOriginal': author_location,
              'media': media_keys,
              'platform': getPlatform(object_['source']) if 'source' in object_.keys() else getPlatform(),
              'original':original,
              'quoteCount': public_metrics['quoteCount'] if 'quoteCount' in public_metrics.keys() else public_metrics['quote_count'] if 'quote_count' in public_metrics.keys() else None,
              'retweetCount': public_metrics['retweetCount'] if 'retweetCount' in public_metrics.keys() else public_metrics['retweet_count'] if 'retweet_count' in public_metrics.keys() else None,
              'replyCount': public_metrics['replyCount'] if 'replyCount' in public_metrics.keys() else public_metrics['reply_count'] if 'reply_count' in public_metrics.keys() else None,
              'urls': urls,
              'verified': verified,
              'protected': protected,
              'conversationId': object_['conversationId'] if 'conversationId' in object_.keys() else object_['conversation_id'] if 'conversation_id' in object_.keys() else None,
              'userScreenName': userScreenName,
              'userName': userName,
              'usersDescription': usersDescription,
              'usersFollowersCount': usersFollowersCount,
              'usersFriendsCount': usersFriendsCount,
              'matchingRule': object_['matching_rules'] if 'matching_rules' in object_.keys() else None,
              'emojis': getEmojis(fullText),
              'text' : getCleanedText(fullText),
              'processedTokens':  getCleanedTextList(fullText, alpha_numeric_only=True, lower=False),
              'processedDescTokens': getCleanedTextList(usersDescription, alpha_numeric_only=True, lower=False),
             }

    return tweet_


def extractTweetsFromDict(object_, tweets_dict = dict(), original = False, users_dict = dict(), places_dict = dict(), retweets_dict = dict(), replies_dict = dict(), quotes_dict = dict(), media_dict = dict()):
    if object_:
        if type(object_) == list:
            if len(object_) == 1:
                object_ = object_[0]
            else:
                try:
                    items = object_.copy()
                    for object_ in items:
                        date_str = object_.get("createdAt") or object_.get("created_at")
                        parsed_date = parse_date(date_str)
                        formatted_date = format_date(parsed_date, "%Y-%m-%d")
                        if 'referenced_tweets' in object_.keys():
                            for referenced_tweet in object_['referenced_tweets']:
                                if referenced_tweet['type'] == 'retweeted':
                                    author_id = object_['author_id']
                                    if referenced_tweet['id'] in retweets_dict.keys():
                                        if object_['id'] not in retweets_dict[referenced_tweet['id']].keys():
                                            if author_id in users_dict.keys():
                                                user_obj = users_dict[author_id]
                                                if 'screen_name' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': user_obj['screen_name'], 'userName': user_obj['name'], 'createdAt':formatted_date}
                                                else:
                                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': user_obj['username'], 'userName': user_obj['name'], 'createdAt':formatted_date}
                                                if 'location' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                            else:
                                                retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': None, 'createdAt':formatted_date}
                                    else:
                                        if author_id in users_dict.keys():
                                            user_obj = users_dict[author_id]
                                            try:
                                                if 'screen_name' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': user_obj['screen_name'], 'userName': user_obj['name'], 'createdAt':formatted_date}}
                                                else:
                                                    retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': user_obj['username'], 'userName': user_obj['name'], 'createdAt':formatted_date}}
                                                if 'location' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                            except Exception as exp:
                                                handleException(exp,object_,f'{__name__} 4')
                                        else:
                                            retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': None}}

                                if referenced_tweet['type'] == 'replied_to':
                                    if referenced_tweet['id'] in replies_dict.keys():
                                        if object_['id'] not in replies_dict[referenced_tweet['id']].keys():
                                            replies_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                                    else:
                                        replies_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                                    replies_dict[referenced_tweet['id']][object_['id']]['inReplyToId'] = referenced_tweet['id']

                                if referenced_tweet['type'] == 'quoted':
                                    if referenced_tweet['id'] in quotes_dict.keys():
                                        if object_['id'] not in quotes_dict[referenced_tweet['id']].keys():
                                            quotes_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                                    else:
                                        quotes_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                                    quotes_dict[referenced_tweet['id']][object_['id']]['quotationId'] = referenced_tweet['id']
                        else:
                            if object_['id'] not in tweets_dict.keys():
                                tweets_dict[object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                            else:
                                try:
                                    if 'retweetCount' in tweets_dict[object_['id']].keys() and 'retweetCount' in object_:
                                        tweets_dict[object_['id']]['retweetCount']= max(tweets_dict[object_['id']]['retweetCount'], object_['retweetCount'])
                                    if 'replyCount' in tweets_dict[object_['id']].keys() and 'replyCount' in object_:
                                        tweets_dict[object_['id']]['replyCount']= max(tweets_dict[object_['id']]['replyCount'], object_['replyCount'])
                                    if 'favoriteCount' in tweets_dict[object_['id']].keys() and 'like_count' in object_:
                                        tweets_dict[object_['id']]['favoriteCount']= max(tweets_dict[object_['id']]['like_count'], object_['like_count'])
                                    if 'quoteCount' in tweets_dict[object_['id']].keys() and 'quoteCount' in object_:
                                        tweets_dict[object_['id']]['quoteCount']= max(tweets_dict[object_['id']]['quoteCount'], object_['quoteCount'])
                                except Exception as exp:
                                    handleException(exp,tweets_dict[object_['id']],f'{__name__} 5')
                except Exception as exp3:
                    handleException(exp3,object_,func_=f'{__name__}')
                return tweets_dict, retweets_dict, replies_dict, quotes_dict
        try:
            date_str = object_.get("createdAt") or object_.get("created_at")
            parsed_date = parse_date(date_str)
            formatted_date = format_date(parsed_date, "%Y-%m-%d")            
            if 'referenced_tweets' in object_.keys():
                for referenced_tweet in object_['referenced_tweets']:
                    if referenced_tweet['type'] == 'retweeted':
                        author_id = object_['author_id']
                        if referenced_tweet['id'] in retweets_dict.keys():
                            if object_['id'] not in retweets_dict[referenced_tweet['id']].keys():
                                if author_id in users_dict.keys():
                                    user_obj = users_dict[author_id]
                                    if 'screen_name' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': user_obj['screen_name'], 'userName': user_obj['name'], 'createdAt':formatted_date}
                                    else:
                                        retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': user_obj['username'], 'userName': user_obj['name'], 'createdAt':formatted_date}
                                    if 'location' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                else:
                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'userId' : author_id, 'userScreenName': None, 'createdAt':formatted_date}
                        else:
                            if author_id in users_dict.keys():
                                user_obj = users_dict[author_id]
                                try:
                                    if 'screen_name' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': user_obj['screen_name'], 'userName': user_obj['name'], 'createdAt':formatted_date}}
                                    else:
                                        retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': user_obj['username'], 'userName': user_obj['name'], 'createdAt':formatted_date}}
                                    if 'location' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                except Exception as exp:
                                    handleException(exp,object_,f'{__name__} 4')
                            else:
                                retweets_dict[referenced_tweet['id']] = {object_['id']: {'userId' : author_id, 'userScreenName': None}}

                    if referenced_tweet['type'] == 'replied_to':
                        if referenced_tweet['id'] in replies_dict.keys():
                            if object_['id'] not in replies_dict[referenced_tweet['id']].keys():
                                replies_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                        else:
                            replies_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                        replies_dict[referenced_tweet['id']][object_['id']]['inReplyToId'] = referenced_tweet['id']

                    if referenced_tweet['type'] == 'quoted':
                        if referenced_tweet['id'] in quotes_dict.keys():
                            if object_['id'] not in quotes_dict[referenced_tweet['id']].keys():
                                quotes_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                        else:
                            quotes_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                        quotes_dict[referenced_tweet['id']][object_['id']]['quotationId'] = referenced_tweet['id']
            else:
                if object_['id'] not in tweets_dict.keys():
                    tweets_dict[object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                else:
                    try:
                        if 'retweetCount' in tweets_dict[object_['id']].keys() and 'retweetCount' in object_:
                            tweets_dict[object_['id']]['retweetCount']= max(tweets_dict[object_['id']]['retweetCount'], object_['retweetCount'])
                        if 'replyCount' in tweets_dict[object_['id']].keys() and 'replyCount' in object_:
                            tweets_dict[object_['id']]['replyCount']= max(tweets_dict[object_['id']]['replyCount'], object_['replyCount'])
                        if 'favoriteCount' in tweets_dict[object_['id']].keys() and 'like_count' in object_:
                            tweets_dict[object_['id']]['favoriteCount']= max(tweets_dict[object_['id']]['like_count'], object_['like_count'])
                        if 'quoteCount' in tweets_dict[object_['id']].keys() and 'quoteCount' in object_:
                            tweets_dict[object_['id']]['quoteCount']= max(tweets_dict[object_['id']]['quoteCount'], object_['quoteCount'])
                    except Exception as exp:
                        handleException(exp,tweets_dict[object_['id']],f'{__name__} 5')
        except Exception as exp3:
            handleException(exp3,object_,func_=f'{__name__}')
    return tweets_dict, retweets_dict, replies_dict, quotes_dict

def clear_text(text):
    """ A function to clear the text from html tags and convert it to plain text. It utilizes the library html2text to convert the html to text. It is needed 

    Args:
        text (str): The text that you need to clear from html tags.

    Returns:
        str: the text that is cleared from html tags.
    """
    text = re.sub('<a href="about:[^>]+></a>', '', text)
    text = html2text.html2text(text)
    return text

def process_youtube_objects(objects):
    try:
        objects_df = pd.DataFrame.from_records(objects)
        logger.info(f"Loading data done!")
        objects_df.fillna('', inplace=True)
        if len(objects_df) > 0:
            if 'viewerRating' in objects_df.keys():
                objects_df['viewerRating'] = objects_df['viewerRating'].apply(lambda val: "" if val == 'none' else val)
            if 'authorChannelId' in objects_df.keys():
                objects_df['authorChannelId'] = objects_df['authorChannelId'].apply(lambda val: val['value'] if type(val) == dict and 'value' in val else val)
            if 'textDisplay' in objects_df.keys():
                objects_df['textDisplayCleared'] = objects_df['textDisplay'].apply(lambda x: clear_text(x))
            if 'liveBroadcastContent' in objects_df.keys():
                objects_df['liveBroadcastContent'] = objects_df['liveBroadcastContent'].apply(lambda x: "" if x=="none" else x)
            if 'localized' in objects_df.keys():
                objects_df['localized_title'] = objects_df['localized'].apply(lambda x: x['title'] if type(x) == dict and 'title' in x else "")
                objects_df['localized_description'] = objects_df['localized'].apply(lambda x: x['description'] if type(x) == dict and 'description' in x else "")
            if 'thumbnails' in objects_df.keys():
                objects_df['videoThumbnails'] = objects_df['thumbnails'].apply(lambda x:  x['maxres']['url'] if type(x) == dict and 'maxres' in x else x['high']['url'] if type(x) == dict and 'high' in x else x['medium']['url'] if type(x) == dict and 'medium' in x else x['standard']['url'] if type(x) == dict and 'standard' in x else x['default']['url'] if type(x) == dict and 'default' in x else "")
            if 'status' in objects_df.keys():
                objects_df['videoMadeForKids'] = objects_df['status'].apply(lambda x: x['madeForKids'] if type(x) == dict and 'madeForKids' in x else "")
                objects_df['videoPrivacyStatus'] = objects_df['status'].apply(lambda x: x['privacyStatus'] if type(x) == dict and 'privacyStatus' in x else "")
            if 'statistics' in objects_df.keys():
                objects_df['likeCount'] = objects_df['statistics'].apply(lambda x: x['likeCount'] if type(x) == dict and 'likeCount' in x else 0)
                objects_df['favoriteCount'] = objects_df['statistics'].apply(lambda x: x['favoriteCount'] if type(x) == dict and 'favoriteCount' in x else 0)
                objects_df['viewCount'] = objects_df['statistics'].apply(lambda x: x['viewCount'] if type(x) == dict and 'viewCount' in x else 0)
            if 'topicDetails' in objects_df.keys():
                objects_df['videoTopicDetails'] = objects_df['topicDetails'].apply(lambda x: x['topicCategories'] if type(x) == dict and 'topicCategories' in x else "")
            
            if 'authorDisplayName' in objects_df.keys():
                objects_df['authorDisplayName'] = objects_df['authorDisplayName'].apply(lambda x: x.replace('@', ''))
            
            if "textDisplayCleared" in objects_df.columns:
                objects_df = objects_df.rename(columns={"textDisplayCleared":"fullText",
                    "textOriginal":"originalText",
                    "authorDisplayName":"userScreenName",
                    "authorProfileImageUrl":"authorImageUrl",
                    "publishedAt":"createdAt",
                    "parentId":"inReplyToId",
                    "defaultLanguage":"languagePlatform"
                    })
                objects_df['placeCountry'] = ""
                objects_df['placeFullName'] = ""
                objects_df['locationGps'] = "not_available"
                objects_df['userLocationOriginal'] = "not_available"
            elif "title" in objects_df.columns:
                objects_df = objects_df.rename(columns={"title":"videoTitle",
                    "description":"videoDescription",
                    "channelId": "videoChannelId",
                    "channelTitle":"videoChannelTitle",
                    "categoryId":"videoCategoryId",
                    "tags":"videoTags",
                    "defaultAudioLanguage":"videoDefaultAudioLanguage",
                    "liveBroadcastContent":"videoLiveBroadcastContent",
                    "likeCount":"videoFavoriteCount",
                    "viewCount":"videoViewCount",
                    "publishedAt":"videoCreatedAt",
                    "videoDefaultLanguage":"videoLanguagePlatform",
                    "localized_title": "videoLocalizedTitle",
                    "localized_description": "videoLocalizedDescription",
                    })
                            
            logger.info(f"Cleaning data done!...")
            
            if 'fullText' in objects_df.columns:
                logger.info(f"Starting language identification...")
                objects_df['language'] = objects_df['fullText'].apply(lambda val: get_language(val))
                objects_df['hashtags'] = objects_df['fullText'].apply(lambda val: [x.replace('#','') for x in tweet_tokenizer.tokenize(val) if x.startswith('#')])
                objects_df['mentions'] = objects_df['fullText'].apply(lambda val: [x.replace('@','') for x in tweet_tokenizer.tokenize(val) if x.startswith('@')])
                objects_df['emojis'] = objects_df['fullText'].apply(lambda val: getEmojis(val))
                objects_df['text'] = objects_df['fullText'].apply(lambda val: getCleanedText(val))
                objects_df['processedTokens'] = objects_df['fullText'].apply(lambda val: getCleanedTextList(val, alpha_numeric_only=True, lower=False))
            
            if 'title' in objects_df.columns:
                logger.info(f"Starting language identification...")
                objects_df['videoLanguage'] = objects_df['title'].apply(lambda val: get_language(val))
                objects_df['videoHashtags'] = objects_df['title'].apply(lambda val: [x.replace('#','') for x in tweet_tokenizer.tokenize(val) if x.startswith('#')])
                objects_df['videoMentions'] = objects_df['title'].apply(lambda val: [x.replace('@','') for x in tweet_tokenizer.tokenize(val) if x.startswith('@')])
                objects_df['videoEmojis'] = objects_df['title'].apply(lambda val: getEmojis(val))
                objects_df['videoText'] = objects_df['title'].apply(lambda val: getCleanedText(val))
                objects_df['videoProcessedTokens'] = objects_df['title'].apply(lambda val: getCleanedTextList(val, alpha_numeric_only=True, lower=False))
                
            if 'createdAt' in objects_df.columns:
                objects_df['createdAtDays'] = objects_df['createdAt'].apply(lambda val: val[0:10])
                objects_df['createdAtMonths'] = objects_df['createdAt'].apply(lambda val: val[0:7])
                objects_df['createdAtYears'] = objects_df['createdAt'].apply(lambda val: val[0:4])
            if 'videoCreatedAt' in objects_df.columns:
                objects_df['videoCreatedAtDays'] = objects_df['videoCreatedAt'].apply(lambda val: val[0:10])
                objects_df['videoCreatedAtMonths'] = objects_df['videoCreatedAt'].apply(lambda val: val[0:7])
                objects_df['videoCreatedAtYears'] = objects_df['videoCreatedAt'].apply(lambda val: val[0:4])
        objects_df.drop(columns=['defaultLanguage','videoDefaultLanguage','status','statistics','localized','thumbnails','topicCategories','topicDetails','textDisplay'], axis=1, inplace=True, errors='ignore')
        logger.info(f"Extracting information done!... Writing data to file...")
        return objects_df.to_dict(orient="index")
    except Exception as exp:
        logger.warning(f"process_youtube_objects: {traceback.format_exc()}")
        handleException(exp, 'Unknown', func_=f'{__name__}' )

import gzip
import shutil

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

def combineCommentsWithVideos(OUTPUT_FOLDER):
    """ A function to combine YouTube comments with their corresponding videos objects.
    It creates a new file called 'combined' in the OUTPUT_FOLDER. 
    
    Args:
        OUTPUT_FOLDER (str): A path to the output folder which the files comments and videos are located in. The resulted combined objects will be written into the same folder..
    """

    try:
        workfiles = list(set([f for f in glob.glob(f"{OUTPUT_FOLDER}/**/*", recursive=True) if isfile(f) and not f.endswith('.gz') and not f.endswith('.bz2')]))
        videoFiles = [file_ for file_ in workfiles if "videos" in file_]
        commentsFiles = [file_ for file_ in workfiles if "comments" in file_]
        videosDict = dict()
        combinedDict = dict()
        
        for videoFile in videoFiles:
            with open(videoFile, 'r', encoding='utf-8') as videosFin:
                for line in videosFin.readlines():
                    obj_ = json.loads(line)
                    videosDict[obj_['videoId']] = obj_
        print(f"Loaded {len(videosDict)} videos objects...")
        for commentsFile in commentsFiles:
            print(f"Processing {commentsFile}...")
            with open(commentsFile, 'r', encoding='utf-8') as commentsFin:
                print(f"Processing {len(commentsFin.readlines())} comments...")
            with open(commentsFile, 'r', encoding='utf-8') as commentsFin:
                for line in commentsFin.readlines():
                    obj_ = json.loads(line)
                    if 'videoId' in obj_.keys():
                        combinedDict[obj_['id']] = obj_
                        if obj_['videoId'] in videosDict.keys():
                            for k in videosDict[obj_['videoId']].keys():
                                combinedDict[obj_['id']][k] = videosDict[obj_['videoId']][k]
                        
                    if len(combinedDict) >= 100000:
                        print(f"Writing {len(combinedDict)} combined objects to file...")
                        with open(join(OUTPUT_FOLDER,"combined"),'a+', encoding="utf-8") as fout:
                            for k in combinedDict.keys():
                                fout.write(f"{json.dumps(combinedDict[k], ensure_ascii=False)}\n") 
                        combinedDict = dict()
            print(f"\n\tDone with {len(combinedDict)} combined objects to file...\n")
        if len(combinedDict) > 0:
            print(f"Writing {len(combinedDict)} combined objects to file...")
            with open(join(OUTPUT_FOLDER,"combined"),'a+', encoding="utf-8") as fout:
                for k in combinedDict.keys():
                    fout.write(f"{json.dumps(combinedDict[k], ensure_ascii=False)}\n") 
            combinedDict = dict()
        for workfile in workfiles:
            if exists(workfile):
                compress_file(workfile, f"{workfile}.gz")
    except Exception as exp:
        logger.warning(f"combineCommentsWithVideos: {exp}")
    
def write_comments_to_file(comments_dict, OUTPUT_FOLDER):
    try:
        if comments_dict != None and len(comments_dict)>0:
            with open(join(OUTPUT_FOLDER, "comments"), 'a+', encoding='utf-8') as fout:
                for k in comments_dict.keys():
                    fout.write(f"{json.dumps(comments_dict[k], ensure_ascii=False)}\n")
    except Exception as exp:
        logger.warning(f"write_comments_to_file: {exp}")

def write_videos_to_file(videos_dict, OUTPUT_FOLDER):
    try:
        if videos_dict != None and len(videos_dict) > 0:
            with open(join(OUTPUT_FOLDER, "videos"), 'a+', encoding='utf-8') as fout:
                for k in videos_dict.keys():
                    fout.write(f"{json.dumps(videos_dict[k], ensure_ascii=False)}\n")
    except Exception as exp:
        logger.warning(f"write_videos_to_file: {exp}")
        
def extract_youtube_data(workFile, OUTPUT_FOLDER):
    logger = create_logger(f'utils', file='utils')

    print(workFile)
    comments = []
    videos = []    
    if exists(workFile):
        with open(workFile, 'r' , encoding='utf-8') as fin:
            for line in fin:
                try:
                    items = json.loads(line)
                    if items and 'items' in items:
                        for item in items['items']:
                            topLevelComment = None
                            if 'snippet' in item:
                                if 'topLevelComment' in item['snippet']:
                                    topLevelComment = {k: item['snippet']['topLevelComment']['snippet'][k] for k in item['snippet']['topLevelComment']['snippet']}
                                    topLevelComment['id'] = item['snippet']['topLevelComment']['id']
                                    topLevelComment['repliesTimes'] = []
                                if item['kind'] == 'youtube#video':
                                    if 'publishedAt' in item['snippet']:
                                        youtubeVideo = {k: item['snippet'][k] for k in item['snippet'] if k not in ['player', 'kind']}
                                        youtubeVideo['videoId'] = item['id']
                                        youtubeVideo['status'] = item['status']
                                        youtubeVideo['statistics'] = item['statistics']
                                        youtubeVideo['topicDetails'] = item['topicDetails'] if 'topicDetails' in item else ""
                                        videos.append(youtubeVideo)
                            if 'replies' in item:
                                replies_queue = dict()
                                for reply in sorted(item['replies']['comments'], key=lambda x: x['snippet']['publishedAt'], reverse=True):
                                    id_ = reply['id']
                                    reply = {k: reply['snippet'][k] for k in reply['snippet']}
                                    reply['id'] = id_
                                    authorDisplayName = reply['authorDisplayName'].strip().replace('@','')
                                    if authorDisplayName in replies_queue.keys():
                                        reply['repliesTimes'] = replies_queue.pop(authorDisplayName)
                                    
                                    repliedToAccount = reply['textOriginal'].split(' ')[0].strip().replace('@','') if reply['textOriginal'].startswith('@') \
                                        else reply['textDisplay'].split(' ')[0].strip().replace('@','') if reply['textDisplay'].startswith('@') \
                                                else None
                                    
                                    if repliedToAccount:
                                        replies_queue[repliedToAccount] = f"{authorDisplayName} {reply['publishedAt']}"
                                    elif topLevelComment:
                                        topLevelComment['repliesTimes'].append(f"{authorDisplayName} {reply['publishedAt']}")
                                    
                                    if reply:
                                        comments.append(reply)
                                    
                            if topLevelComment:
                                comments.append(topLevelComment)
                            if len(comments) >= 100000:
                                comments_dict = process_youtube_objects(comments)
                                if comments_dict:
                                    if len(comments_dict) > 0:
                                        write_comments_to_file(comments_dict, OUTPUT_FOLDER)
                                comments = []
                            if len(videos) >= 100000:
                                videos_dict = process_youtube_objects(videos)
                                if len(videos_dict) > 0:
                                    write_videos_to_file(videos_dict, OUTPUT_FOLDER)
                                videos = []
                except Exception as exp:
                    logger.warning(f"extract_youtube_data: {exp}")
    if len(comments) > 0:
        comments_dict = process_youtube_objects(comments)
        if comments_dict!=None:
            print(f"Number of comments: {len(comments_dict)}")
            if len(comments_dict) > 0:
                print(f"Number of comments: {len(comments_dict)}")
                write_comments_to_file(comments_dict, OUTPUT_FOLDER)
            else:
                print(f"!Number of comments: {len(comments_dict)}")
        comments = []
    if len(videos) > 0:
        videos_dict = process_youtube_objects(videos)
        if len(videos_dict) > 0:
            write_videos_to_file(videos_dict, OUTPUT_FOLDER)
        videos = []

# Creating the logger object
logger = create_logger(f'utils', file='utils')

