# -*- coding: utf-8 -*-

import datetime as dt
import time
import sys
from os.path import abspath, join
try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *
from utils import get_location, create_logger
logger = create_logger(f"3_update_locations", file=f"data_updater")

    
if __name__== "__main__":
    run = True
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="please specify core", default=None)
    parser.add_argument('-qs', '--queryString', help="The query string that the system uses to identify updating limit (update all records or new records only).", default=None)
 
    args = parser.parse_args()
    core = args.core
    queryString = args.queryString
 
    print_this(f"queryString for location : {queryString}")
    solr = SolrClass({})
    if core != None:
    
        tweets_all, max_row = solr.get_no_location_items(solr_core=core, queryString=queryString)

        tweets_list = []
        while len(tweets_all) > 0:
            tweets = tweets_all[0:10000]
            tweets_all = tweets_all[10000:]
            loc_dict = dict()
            for tweet in tweets:
                loc_dict[tweet['id']] = {'id': tweet['id'],
                'user': {'location': tweet['userLocationOriginal'] if 'userLocationOriginal' in tweet.keys() else 'not_available'},
                'place': {'country': tweet['placeCountry'] if 'placeCountry' in tweet.keys() else 'not_available',
                'placeFullName': tweet['placeFullName'] if 'placeFullName' in tweet.keys() else 'not_available'}}
            locations = get_location(loc_dict)

            # only update if the location api running and accessible.
            if locations != None:
                for k in locations.keys():
                    tweets_list.append({'id': k, 'userLocation': locations[k]['user'], 'locationGps': locations[k]['tweet']})

            if len(tweets_all) == 0:
                tweets_list = solr.add_items_to_solr(core, tweets_list)
                logger.info(f"[update_locations]: adding items call done ... currently {len(tweets_all)} to be processed")
                time.sleep(5) # wait Solr's soft commit
                tweets_all, max_row = solr.get_no_location_items(solr_core=core, queryString=queryString)
        if max_row == 0:
            logger.info(f"[update_locations]: Updating locations finished.")
        if len(tweets_list) >= 0:
            tweets_list = solr.add_items_to_solr(core, tweets_list)
            logger.info(f"[update_locations]: adding items call done ... currently {len(tweets_all)} to be processed")
    else:
        logger.info('[update_locations]: Please make sure that command contains the core instance name.')
