# -*- coding: utf-8 -*-
import time
import sys
import os
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *

from utils import get_sentiments, get_language, create_logger
logger = create_logger(f"4_update_sentiments", file=f"data_updater")

SLEEP_TIME = 3
SUPPORTED_LANGUAGES = {'arabic': 'ar', 'english': 'en', 'french': 'fr', 'german':'de', 'hindi':'hi', 'italian': 'it', 'spanish': 'sp', 'portuguese': 'pt'}
SUPPORTED_LANGUAGES_REVERSE = {v: k for k, v in SUPPORTED_LANGUAGES.items()}

        
if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="please specify core", default=None)
    parser.add_argument('-qs', '--queryString', help="The query string that the system uses to identify updating limit (update all records or new records only).", default=None)
    
    args = parser.parse_args()
    core = args.core
    queryString = args.queryString
    
    print_this(f"queryString for sentiment: {queryString}")
    
    solr = SolrClass({})

    if core != None:

        tweets_all, max_row = solr.get_no_sentiment_items(solr_core=core, queryString=queryString)

        tweets_list = []
        sentiments_list = dict()

        while len(tweets_all)> 0:
            logger.info(f'[update_sentiments]: Solr query results gotten ... {max_row}')
            logger.info(f'[update_sentiments]: Total tweets to analyze: {len(sentiments_list)}')
            logger.info(f'[update_sentiments]: Total tweets ready to send back to Solr: {len(tweets_list)}')

            for tweet in tweets_all:
                try:
                    if 'fullText' in tweet.keys():
                        if 'languagePlatform' not in tweet.keys():
                            language_ = get_language(tweet['fullText'])
                        else:
                            if 'language' in tweet.keys():
                                language_ = get_language(tweet['fullText']) if tweet['language'] != tweet['languagePlatform'] else tweet['language']
                            else:
                                language_ = get_language(tweet['fullText'])
                    else:
                        language_ = "NonText"

                    if language_ in SUPPORTED_LANGUAGES.keys():
                        sentiments_list[tweet["id"]] = {'id': tweet['id'], "fullText": tweet['fullText'], "language":SUPPORTED_LANGUAGES[language_]}
                    elif language_ in SUPPORTED_LANGUAGES_REVERSE.keys():
                        sentiments_list[tweet["id"]] = {'id': tweet['id'], "fullText": tweet['fullText'], "language":language_}
                    else:
                        tweets_list.append({'id': tweet['id'], 'sentiment': 'NonText' if language_ == 'NonText' else 'OtherLanguages', 'language':language_, 'sentiment_s':'Done'})
                except Exception as exp:
                    logger.info(f'[update_sentiments]: [Exception] at Loading data! {exp}')
                threshold = min(4000, max_row)
                if len(sentiments_list) >= threshold:
                    logger.info(f'[update_sentiments]: Sentiment loaded with {threshold} tweets')
                    extracted_sentiments = None
                    try:
                        logger.info("[update_sentiments]: Getting sentiments started")
                        extracted_sentiments = get_sentiments(sentiments_list)
                        logger.info("[update_sentiments]: Getting sentiments done!")
                    except Exception as exp:
                        logger.warning(f'[update_sentiments]: [Exception] at calling getting_sentiments. {exp}')
                        time.sleep(1)
                        pass
                    if extracted_sentiments != None:
                        for k in extracted_sentiments.keys():
                            tweets_list.append({'id': k, 'sentiment': extracted_sentiments[k], 'language':SUPPORTED_LANGUAGES_REVERSE[sentiments_list[k]['language']], 'sentiment_s':'Done'})
                        sentiments_list = dict()
                threshold = min(8000, max_row)

                if len(tweets_list) >= threshold:
                    logger.info(f"[update_sentiments]: sample tweets: {[s['id'] for s in tweets_list[-3:]]}")
                    tweets_list =  solr.add_items_to_solr(core, tweets_list)
                    logger.info(f'[update_sentiments]: {threshold} tweets written to solr')
                    time.sleep(2) #Wait for the Solr's soft commit.

            tweets_all, max_row = solr.get_no_sentiment_items(solr_core=core, queryString=queryString)

        if len(sentiments_list) > 0:
            extracted_sentiments = None
            try:
                extracted_sentiments = get_sentiments(sentiments_list)
                if extracted_sentiments != None:
                    for k in extracted_sentiments.keys():
                        tweets_list.append({'id': k, 'sentiment': extracted_sentiments[k], 'language':SUPPORTED_LANGUAGES_REVERSE[sentiments_list[k]['language']], 'sentiment_s':'Done'})
            except Exception as exp:
                logger.warning(f'[update_sentiments]: [Exception] at calling getting_sentiments 2. {exp}')
                pass
            finally:
                sentiments_list = dict()

        if len(tweets_list) > 0:
            logger.info(f"[update_sentiments]: sample tweets: {tweets_list[0:3]}")
            tweets_list =  solr.add_items_to_solr(core, tweets_list)
            logger.info('[update_sentiments]: written to solr')
        logger.info('[update_sentiments]: Done!')
    else:
        logger.warning('[update_sentiments]: Please enter core name. You can use the flag (c) to pass its name as following: \n\tpython update_sentiments.py\n')