#!/usr/bin/env python3
from configs import ApplicationConfig
import numpy as np
import pandas as pd
import json
import re
import urllib
from urllib.parse import quote
import urllib.parse
import time
import random
from datetime import datetime, timedelta
import pysolr
import textwrap
import sys
from collections import defaultdict
import traceback
from utils import create_logger, print_this
logger = create_logger(f"Solr Class", file=f"solr_class")

groupsLimit = 500
queryLimit = 10000
rowsLimit = 100000

from os.path import join, isfile
from os import getcwd
stopwords = []

try:
    file_name = '.stopwords.txt'
    for i in range(3):
        potential_path = join(*(['..'] * i), file_name)
        if isfile(potential_path):
            with open(potential_path, 'r', encoding='utf-8') as fin:
                stopwords += [x.strip() for x in fin.readlines()]
                break        
    if len(stopwords) == 0:
        logger.warning(f"Stopwords not loaded as file not found!\n")
    else:
        logger.info(f"Stopwords loaded successfully.\n")
except Exception as exp:
    logger.warning(f"Stopwords not loaded.\n: {exp}")
    pass

def get_mapping_dict_to_count(name, target='count'):
    """An auxiliary function that returns a dictionary that holds the passed name of the feature and the title count. \
    This is used in the report generation so we can map each feature to its own counts.

    Args:
        :name: (str) The name of the object that will be used as a key in the dictionary.

    Returns:
        :dict: A dictionary with keys (first and second) in which the first key holds the name of the feature and the \
            second holds the string "count".
    """
    return {'first': name, 'second': target}



import heapq

def sort_dict_with_names(my_dict, top_n, keys, reverse=True, mutliply_by=1):
    """To sort the dictionary based on the values and return the top n values.

    Args:
        :my_dict: (dict) A dictionary with keys and values to be sorted.
        :top_n: (int) The number of top values to be returned.
        :keys: (dict) A dictionary that holds information about my_dict contents.

    Returns:
        :dict: The sorted dictionary version from the input @my_dict by considering the top n values.
    """
    n = min(len(my_dict), top_n)

    top_items = heapq.nlargest(n, my_dict.items(), key=lambda x: x[1]) if reverse else heapq.nsmallest(n, my_dict.items(), key=lambda x: x[1])

    result = [{keys['first']: key, keys['second']: mutliply_by * value} for key, value in top_items]
    return result

class SolrClass:
    """ Class containing the code that interfaces with the Solr cores in order to retrieve relevant data.
    """
    solrs = {}
    query = '*:*'
    solr_networks = {}
    
    def __init__(self, filters):
        """ Initialises SolrClass with relevant filters

        Args:
            :filters (dict): dictionary containing the filters to apply on the data retrieval (date_start, date_end, \
                language, sentiment, location, location_type). Dates are expected in the YYYY-MM-DD format.

        """

        solr_cores = ApplicationConfig.SOLR_CORES
        solr_url = ApplicationConfig.SOLR_URL
        solr_port = ApplicationConfig.SOLR_PORT
        self.solr_networks = ApplicationConfig.SOLR_NETWORKS
        self.solr_communities = ApplicationConfig.SOLR_COMMUNITIES
        for core in solr_cores:
            self.solrs[core] = f"{solr_url}:{solr_port}/solr/{core}/"
        self.random_seed =  filters["randomSeed"] if "randomSeed" in filters else 666
        self.date_range = self.stringify_date_range(filters["date_start"] if "date_start" in filters else "", filters["date_end"] if "date_end" in filters else "")
        self.language_filter = self.stringify_filter(filters["language"] if "language" in filters else "", "language")
        self.sentiment_filter = self.stringify_filter(filters["sentiment"] if "sentiment" in filters else "", "sentiment")
        self.country_filter = ""
        if "location_type" in filters:
            if filters["location_type"] == "author":
                self.country_filter = self.stringify_filter(filters["location"], "userLocation")
            elif filters["location_type"] == "tweet":
                self.country_filter = self.stringify_filter(filters["location"], "locationGps")
        #self.solr_query_builder(filters, keywords, operator, limit)

    def get_solr_networks(self):
        """an auxiliary function that returns the solr networks.

        Returns:
            dict: a dictionary that holds the solr networks as configured in the system.
        """
        return dict(self.solr_networks)
        
    def create_facet(self, limit):
        """ An auxiliary function that creates the facet json for the query.

        Args:
            :limit: (int) Maximum size of the retrieved data from Solr.

        Returns:
            :dict: Dictionary with the required fields per facet to query the Solr core.
        """
        facet_json_timelines = {
            'traffic': {
                'limit':limit,'type':'terms','field':'createdAtDays'
            },
            'Sentiments':{
                'limit':limit,'type':'terms','field':'sentiment', 'facet': {
                    'Sentiments_Distributions':{'limit':limit,'type':'terms','field':'createdAtDays'},
                    'tweets_locations_by_sentiments':{'limit':limit,'type':'terms','field':'locationGps'},
                    'users_locations_by_sentiments':{'limit':limit,'type':'terms','field':'userLocation'},
                    'retweeted': {'limit':limit,'type':'terms','field':'userScreenName', 'facet': {'retweeted':{'limit':limit,'type':'func','func':"'countvals(retweeters)'"}}},
                    'Sentiment_per_Language':{'limit':limit,'type':'terms','field':'language'},
                }
            },
            'Languages': {'limit':limit,'type':'terms','field':'language', 'facet': {
                    'tweets_languages_by_sentiments': {'limit':limit,'type':'terms','field':'sentiment', 'facet': {'createdAtDays':{'limit':limit,'type':'terms','field':'createdAtDays'}}},
                    'tweets_locations_by_languages':{'limit':limit,'type':'terms','field':'locationGps'},
                    'users_locations_by_languages':{'limit':limit,'type':'terms','field':'userLocation'}
                }
            }
        }
        
        features = ['urls', 'mentions', 'retweeters', 'hashtags', 'userScreenName', 'media', 'emojis', 'processedTokens', 'processedDescTokens']
        for feature in features:
            facet_json_timelines['Sentiments']['facet'][feature] = {'limit':limit,'type':'terms','field':feature}
        
        return facet_json_timelines
    
    def get_term_list_from_keywords(self, keywords):
        """ A function that takes the keywords and returns a list of the keywords/phrases after removing the special \
        characters and replacing the spaces with the character %20.

        Args:
            :keywords: (str) The set of words that the user wants to query separated by comma (,). For the combined \
                words we expect the query to be separated with a space.
            
        Returns:
            :list: The list of unique tokens/phrases.
        """
        if type(keywords) == list:
            return list(set([re.sub("[ \t\n]+", '%20', re.sub("[?!=.$\/%]+", '', x.strip()).strip()) for x in keywords if len(x.strip()) > 0 and x != '']))
        return list(set([re.sub("[ \t\n]+", '%20', re.sub("[?!=.$\/%]+", '', x.strip()).strip()) for x in keywords.strip().split(',') if len(x.strip()) > 0 and x != '']))
    
    def check_date_entry(self, date_text, time_pattern="T00:00:00Z"):
        """ An auxiliary function that checks if the date is valid or not.

        Args:
            :date_text: (str) The date to be formatted.

        Returns:
            :str: The String of the date formatted with the required pattren.
        """
        try:
            return datetime.strptime(date_text, '%Y-%m-%d').strftime('%Y-%m-%d'+time_pattern)
        except Exception:
            return ""
        
    def stringify_date_range(self, date_start, date_end):
        """ An auxiliary function that handles the date range in the query. It creates the required string for the date \
        range in Solr query.

        Args:
            :date_start: (str) The start of the time period of interest (None if no date_start is specified)
            :date_end: (str) The end of the time period of interest (None is no date_end is specified)

        Returns:
            str: The string that is used in the query to filter the date range.
        """
        date_range = ''

        #print("This is DATE_START:", date_start)
        #print("This is DATE_END:", date_end)
        
        if(date_start != None  and date_start != ''):
            date_start = self.check_date_entry(date_start, time_pattern="T00:00:00Z")
            date_range = '%20AND%20createdAt:[' + str(date_start + '%20TO%20') if len(date_start) > 1 else '*%20TO%20'
            #print("DATE BUILDER 1:", date_range)
#           #  del date_start

        if not date_range or date_range=="":
            date_range = '%20AND%20createdAt:[*%20TO%20'
            #print("DATE BUILDER 2:", date_range)

        if(date_end != None and date_end != ''):
            date_end = self.check_date_entry(date_end, time_pattern="T23:59:59Z")
            date_range += (str(date_end) +']') if (len(date_end) > 1) else '*]'
            #print("DATE BUILDER 3:", date_range)
        else:
            date_range += '*]'
            #print("DATE BUILDER 4:", date_range)
#             del date_end
        
        if "* TO *" in date_range or '*%20TO%20*'  in date_range:
            date_range = ''
            #print("DATE BUILDER 5:", date_range)
        return date_range.replace(" ","%20").replace("\"","").replace("'","")

    def stringify_filter(self, filter, filter_name):
        """ An auxiliary function that formats filters for the Solr query.

        Args:
            :filter: (str) The value of the filter of interest.
            :filter_name: (str) The name of the filter of interest.

        Returns:
            str: The string that is used in the Solr query to filter.
        """
        filter_str = ''

        if filter != "All" and filter != None:
            if filter_name == "language":
                filter_str = '%20AND%20' + filter_name + ':%22' + filter.lower().replace(" ", "%20") + '%22'
            elif "community" in filter_name.lower():
                filter_str = str('%20AND%20' + filter_name + ':%28' + "%20OR%20".join(filter) + '%29') if len(filter) > 0 else ''
            elif "Times" in filter_name:
                filter_str = '%20AND%20' + filter_name + ':*'
            else:
                filter_str = '%20AND%20' + filter_name + ':%22' + filter.replace(" ", "%20") + '%22'
        return filter_str.replace(" ","%20").replace("\"","").replace("'","")
                    
                    
    def solr_query_builder(self, keywords, operator='AND', limit=queryLimit, caller = ""):
        """A function that handles the query with relevant filters and keywords. It generates a dictionary of the \
        keywords and the corresponding JSON query. The dict of queries is added it to the class attribute @query.

        Args:
            :keywords: (str) The set of words that the user wants to query separated by comma (,). For the combined \
                words we expect the query to be separated with a space.
            :operator: (str, optional) The search operator (OR) and (AND) to be used among the keywords. Defaults \
                to 'AND'.
            :limit: (int, optional) Maximum size (in count) of the retrieved data from Solr.
            :caller: (str, optional) The name of the function that called this function. Defaults to "".
            
        """
        term_list = self.get_term_list_from_keywords(keywords)
        logger.info(f"{caller}: term_list: {term_list}")
        hashtags = [x for x in term_list if x.startswith('#')]
        users = [x for x in term_list if x.startswith('@')]
        terms = [x for x in term_list if  x not in hashtags and  x not in users]
        query = dict()

        # stop condition to stop creating wrong query
        if (len(term_list) == 0):
            query['All'] = 'sentiment:(Neutral%20OR%20Negative%20OR%20Positive)'#'*:*'
        elif (len(term_list) > 1):
            try:
                query_str = "sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20"
                if len(terms) > 0:
                    query_str += "fullText:(%22" + f'%22%20{operator}%20%22'.join(terms).replace('#','').replace('@','') + "%22)"
                    if len(terms)<len(term_list):
                        query_str += f"%20{operator}%20"
                    logger.info(f"(SOLR): {query_str}")
                if len(users) > 0:
                    query_str += str("(userScreenName:(%22" + f'%22%20{operator}%20%22'.join(users) + "%22)").replace('@', '')
                    query_str += str(f"%20OR%20" + " usersDescription:(%22" + f'%22%20{operator}%20%22'.join(users) + "%22))").replace('@', '')
                    logger.info(f"(SOLR): {query_str}")
                    if len(hashtags) > 0:
                        query_str += f"%20{operator}%20"
                if len(hashtags) > 0:
                    query_str += str("hashtags:(%22" + f'%22%20{operator}%20%22'.join(hashtags) + "%22)").replace('#', '')

                query['All'] = query_str
                logger.info(f"(SOLR): {query_str}")
                for term in term_list:
                    if term.startswith('#'):
                        query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20hashtags:%22{term.replace('#','')}%22"
                    elif term.startswith('@'):
                        query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20(userScreenName:%22{term.replace('@','')}%22%20OR%20usersDescription:%22{term.replace('@','')}%22)"
                    else:
                        query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20fullText:%22{term}%22"



            except Exception as exp:
                logger.warning(exp)
        else:
            term = term_list[0]
            if term.startswith('#'):
                query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20hashtags:%22{term.replace('#','')}%22"
            elif term.startswith('@'):
                query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20(userScreenName:%22{term.replace('@','')}%22%20OR%20usersDescription:%22{term.replace('@','')}%22)"
            else:
                query[term] = f"sentiment:(Neutral%20OR%20Negative%20OR%20Positive)%20AND%20fullText:%22{term}%22"

        for k in query.keys():
            query[k] = query[k] + self.language_filter + self.sentiment_filter + self.country_filter + self.date_range

        return query


    def normalize_sentiments(self, sub_value, total_value):
        """A function that normalizes the sentiments to be between -1 and 1. \
        The normalisation is done based on the equation:  \
        ( -1 * COUNT(NEG) + 0 * COUNT(NEUT) + 1 * COUNT(POS)) / (COUNT(NEG) + COUNT(NEUT) + COUNT(POS))\
        However, to invest the already computed values, the equation is simplified to: sub_value / total_value ... in \
        which, the sub_value is the sum of the positive and negative sentiments and the total_value is the sum of all \
        sentiments.

        Args:
            :sub_value: (int) Total counts for both the positive and negative sentiments.
            :total_value: (int) Total counts for all sentiments.

        Returns:
            :long: Normalized value in range [-1;1] inclusive.
        """
        if total_value != 0:
            return (sub_value) / (total_value)
        
    
    def get_maximum(self, report_obj, item_field, sentiment):
        """ An auxiliary function that gets the maximum value of the retweet count for the top field type (which would \
        be users or tweets).

        Args:
            :report_obj: (dict) Dictionary containing the reported tweets and users.
            :item_field: (str) Field's type ("users" or "tweets").
            :sentiment: (str) Sentiment (positive, negative, or neutral).
        """
        try:
            if item_field not in report_obj['All Sentiments']:
                report_obj['All Sentiments'][item_field] = report_obj[sentiment][item_field]
            #elif report_obj['All Sentiments'][item_field]['retweetCount'] < report_obj[sentiment][item_field]['retweetCount']:
            #    report_obj['All Sentiments'][item_field] = report_obj[sentiment][item_field]
            else:
                if 'retweetCount' in report_obj['All Sentiments'][item_field]:
                    if report_obj['All Sentiments'][item_field]['retweetCount'] < report_obj[sentiment][item_field]['retweetCount']:
                        report_obj['All Sentiments'][item_field] = report_obj[sentiment][item_field]
                elif 'favoriteCount' in report_obj['All Sentiments'][item_field]:
                    if report_obj['All Sentiments'][item_field]['favoriteCount'] < report_obj[sentiment][item_field]['favoriteCount']:
                        report_obj['All Sentiments'][item_field] = report_obj[sentiment][item_field]
        except Exception as exp:
            logger.warning(f"Error at get_maximum {exp}")
        
    def combine_all_sentiments(self, report_groups):
        """An auxiliary function that combines all sentiments into one group. It is used to compute the top users and \
        top tweets for all sentiments.

        Args:
            :report_groups: (dict) Dictionary of the sentiments and the corresponding users and tweets.

        Returns:
            :tuple[dict]: Reports of the top users and top tweets for all sentiments combined.
        """
        report_groups_users = {'All Sentiments': {}}
        report_groups_tweets = {'All Sentiments': {}}
        
        for sentiment in  report_groups.keys():
            if sentiment not in report_groups_users:
                report_groups_users[sentiment] = {}
            if sentiment not in report_groups_tweets:
                report_groups_tweets[sentiment] = {}
            
            for item in report_groups[sentiment]:
                if 'userScreenName' not in item:
                    item['userScreenName'] = "_NoNameFound_"
                if item['userScreenName'] not in report_groups_users[sentiment]:
                    report_groups_users[sentiment][item['userScreenName']] = {
                        'userScreenName': item['userScreenName'],
                        'user_description': item['usersDescription'] if 'usersDescription' in item else "", 
                        'retweetCount': item['retweetCount'] if 'retweetCount' in item else 0, 
                        'language': item['language'] if 'language' in item else "",
                        'community': item['retweetCommunity'] if 'retweetCommunity' in item else item['replyCommunity'] if 'replyCommunity' in item else "",
                        'nb_followers': item['usersFollowersCount'] if 'usersFollowersCount' in item else "",
                        'userLocation': item['userLocation'] if ('userLocation' in item and item['userLocation'] != "not_available") else ""
                    }
                    if 'videoId' in item:
                        report_groups_users[sentiment][item['userScreenName']]['videoId'] = item['videoId']
                    self.get_maximum(report_groups_users, item['userScreenName'], sentiment)
                    
                if item['id'] not in report_groups_tweets[sentiment]:
                    report_groups_tweets[sentiment][item['id']] =  {
                        'id':item['id'] , 
                        'fullText': item['fullText'] if 'fullText' in item else "",
                        'date': item['createdAtDays'], 
                        'retweetCount': item['retweetCount'] if 'retweetCount' in item.keys() else 0,
                        'favoriteCount': item['favoriteCount'] if 'favoriteCount' in item.keys() else 0,
                        'language': item['language'], 
                        'location': "" if 'locationGps' not in item else item['locationGps'] if item['locationGps'] != "not_available" else "",
                        'interactionCommunity': item['interactionCommunity'] if 'interactionCommunity' in item else "",
                    }
                    if 'videoId' in item:
                        report_groups_tweets[sentiment][item['id']]['videoId'] = item['videoId']
                    self.get_maximum(report_groups_tweets, item['id'], sentiment)
                    
            report_groups_tweets[sentiment] = list(report_groups_tweets[sentiment].values())
            report_groups_users[sentiment] = list(report_groups_users[sentiment].values())
        report_groups_tweets['All Sentiments'] = list(report_groups_tweets['All Sentiments'].values())
        report_groups_users['All Sentiments'] = list(report_groups_users['All Sentiments'].values())
        return report_groups_users, report_groups_tweets
    
    def compute_positive_negative(self, report_object, feature, top_n):
        """ A function that computes the positive and negative sentiments for a given feature. It then sorts the \
        resulted dicts with their mapped names based on the top_n by calling the function sort_dict_with_names.
        It computes the relative positive to negative tweets by using the following function:
        pos_neg = (v(pos) - v(neg)) / ((v(pos) + v(neu) + v(neg)))

        Args:
            :report_object: (dict[dict]) Part of the report object that holds the sentiments for each feature.
            :feature: (str) Feature name, used to determine the type of the feature and the corresponding \
                computation for the Negative_Positive component.
            :top_n: (int) Length of the returned list of each sorted items.
        """
        report_object['All Sentiments'] = dict()
        report_object['Positive_Negative'] = dict()
        for sentiment in [s for s in report_object if len(report_object[s])>0]:
            try:
                my_dict = map(lambda i: (report_object[sentiment][i]['val'], report_object[sentiment][i]['count']) , range(len(report_object[sentiment])))
                my_dict = dict(my_dict)

                for k in my_dict.keys():
                    report_object['All Sentiments'][k] = report_object['All Sentiments'].get(k, 0) + my_dict[k]
                    if sentiment == "Positive":
                        report_object['Positive_Negative'][k] = report_object['Positive_Negative'].get(k, 0) + my_dict[k]

                    elif sentiment == "Negative":
                        report_object['Positive_Negative'][k] = report_object['Positive_Negative'].get(k, 0) - my_dict[k]
            except Exception as exp:
                logger.warning(f"Error ... {exp}")
                logger.warning(traceback.print_exc())
                pass
        
        for k in report_object['Positive_Negative'].keys():
            if k in report_object['All Sentiments']:
                report_object['Positive_Negative'][k] = self.normalize_sentiments(report_object['Positive_Negative'][k], report_object['All Sentiments'][k])
            else:
                report_object['Positive_Negative'].pop(k)

        report_object['All Sentiments'] = sort_dict_with_names(report_object['All Sentiments'], top_n, keys=get_mapping_dict_to_count('val'))

        if feature not in ['users_locations_by_sentiments', 'tweets_locations_by_sentiments', 'users_languages_by_sentiments', 'tweets_languages_by_sentiments']:
            logger.info(f"Feature: {feature} --> len(+-) : {len(report_object['Positive_Negative'])}")
            report_object['Negative_Positive'] = sort_dict_with_names(dict(report_object['Positive_Negative']), top_n, keys=get_mapping_dict_to_count('val'), reverse=False, mutliply_by=-1)
            logger.info(f"Feature: {feature} --> len(-+) : {len(report_object['Negative_Positive'])}")
            for item in report_object['Negative_Positive']:
                if 'Negative' in report_object:
                    for item2 in report_object['Negative']:
                        if item['val'] == item2['val']:
                            item['count'] = item2['count']
                            break


        report_object['Positive_Negative'] = sort_dict_with_names(report_object['Positive_Negative'], top_n, keys=get_mapping_dict_to_count('val'))


        if feature in ['processedTokens']:
            for item in report_object['Positive_Negative']:
                if 'Positive' in report_object:
                    for item2 in report_object['Positive']:
                        if item['val'] == item2['val']:
                            item['count'] = item2['count']
                            break


    def get_all_languages(self, report_object, top_n):
        """ A function that computes the languages for all sentiments. It then sorts the resulted dicts with their mapped names based on the top_n by calling the function sort_dict_with_names.

        Args:
            :report_object: (dict[dict]) Part of the report that holds the languages for each sentiment.
            :top_n: (int) Length of the returned list of each sorted items.
        """
        report_object['All Languages'] = dict()
        for language in [s for s in report_object if len(s)>0 and s != 'All Languages']:
            try:
                my_dict = map(lambda i: (report_object[language][i]['val'], report_object[language][i]['count']) , range(len(report_object[language])))
                my_dict = dict(my_dict)
                for k in my_dict.keys():
                    report_object['All Languages'][k] = report_object['All Languages'].get(k, 0) + my_dict[k]

            except Exception as exp:
                logger.warning(f"ERROR @ get_all_languages {exp}!!")
                pass
        report_object['All Languages'] = sort_dict_with_names(report_object['All Languages'], top_n, keys=get_mapping_dict_to_count('val'))
        
        
    def optimised_json_query_handler(self, solr_core, keywords, operator, limit=queryLimit, top_n=groupsLimit):
        """ It is the optimised function that is based on JSON query requests. It needs the query, solr object and top_n
        as input. It also uses the query built by calling @solr_query_builder. This query is a dictionary
        of the keywords and the corresponding JSON query. The outcomes are limited to top 150 for performance reasons.

        Args:
            :solr_core: (str) Name of the Solr core to query from.
            :keywords: (str) Comma-separated list of keywords to be queried.
            :limit: (int, optional) Maximum number of datapoints to be returned for the query. Defaults to 10000 as hardcoded varialbe queryLimit.
            :top_n: (int, optional) Maximum number of results to return for the top content fields. Defaults to 500 as hardcoded variable groupsLimit.

        Returns:
            :tuple: Contains a dictionary with the report that corresponds to the query, and the total number of \
                tweets found for the query.
        """
        report = dict()
        error_message = ""
        hits = 0
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)

        query = self.solr_query_builder(keywords, operator=operator, limit=limit, caller = "(SOLR)")

        facet_json_timelines = self.create_facet(limit=limit)
        for query_k in query.keys():
            facet_json_query = {'query': f"'{query[query_k]}'", 'limit':limit , 'facet': facet_json_timelines}
            query[query_k] = facet_json_query

        logger.info(f"query --> {query}")
        for query_term in query:
            facet_url = str(self.solrs[solr_core]) + f"select?random_{random_number}" + "&fl=id%2C%20fullText%2C%20videoId%2C%20createdAtDays%2C%20userScreenName%2C%20usersDescription%2C%20locationGps%2C%20userLocation%2C%20usersFollowersCount%2C%20retweetCommunity%2C%20replyCommunity%2C%20embedding_5d%2C%20processedTokens%2C%20retweetCount%2C%20replyCount%2Clanguage%2Ctopics&group.field=sentiment&group.limit=" + str(limit) + "&group.sort=retweetCount%20desc%2CuserLocation%20asc%2ClocationGps%20asc&group=true&indent=true&q.op=OR&q=sentiment%3A(Neutral%20OR%20Negative%20OR%20Positive)&rows=0&sort=retweetCount%20desc"
            facet_url = facet_url.replace(" ","%20").replace("\"","").replace("'","")+"&json="+json.dumps(query[query_term]).replace(" ","").replace("\"","")
            query_term = query_term.replace('%22', '').replace('%20', ' ')

            print("SEARCH QUERY:", facet_url)
            
            try:
                #logger.info( f"<>{facet_url}<>")
                report[query_term] = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
                report_groups = {items['groupValue']: items['doclist']['docs'] for items in report[query_term]['grouped']['sentiment']['groups']}
                report_groups_users, report_groups_tweets = self.combine_all_sentiments(report_groups)
                report[query_term] = report[query_term]['facets']
                logger.info(f"Report Len: {len(report[query_term])}")
                for mainFeature in list(report[query_term].keys()):
                    if type(report[query_term][mainFeature]) == dict:
                        if 'buckets' in report[query_term][mainFeature].keys():
                            report[query_term][mainFeature] =  report[query_term][mainFeature]['buckets']
                            
                        if mainFeature == 'traffic':
                            report[query_term][mainFeature] = list({'Date': item['val'], 'Count': item['count']} for item in report[query_term][mainFeature])
                            report[query_term][mainFeature] = sorted(report[query_term][mainFeature], key=lambda x: x['Date'], reverse=False)
                        
                        elif mainFeature in ['Sentiments', 'Languages']:
                            
                            for item in report[query_term][mainFeature]:
                                val = item['val']
                                for feature in item.keys():
                                    if feature not in ['val', 'count']:
                                        if feature not in report[query_term].keys():
                                            report[query_term][feature] = dict()
                                        report[query_term][feature][val] = item[feature]['buckets']
                            if mainFeature == "Languages":
                                report[query_term]['Languages_Distributions'] = list({'Language': item['val'][0].upper() + item['val'][1:].lower(), 'Count': item['count']} for item in report[query_term][mainFeature])
                                report[query_term]['Languages_Distributions'] = sorted(report[query_term]['Languages_Distributions'], key=lambda x: x['Count'], reverse=True)
                            report[query_term].pop(mainFeature, None)
                
                for feature in list(report[query_term].keys()) :
                    if feature in ['tweets_languages_by_sentiments']:
                        for language in report[query_term][feature].keys():
                            if type(report[query_term][feature][language]) == list:
                                report[query_term][feature][language] =  {object_['val']: object_['createdAtDays']['buckets'] for object_ in report[query_term][feature][language]} 
                    
                    if feature in ['users_locations_by_sentiments', 'tweets_locations_by_sentiments', 'userScreenName', 'urls', 'retweeters', 'retweeted', 'processedTokens', 'processedDescTokens', 'mentions', 'hashtags', 'media', 'emojis']:
                        self.compute_positive_negative(report[query_term][feature], feature, top_n)
                            
                    if feature in ['tweets_locations_by_languages', 'users_locations_by_languages']:
                        self.get_all_languages(report[query_term][feature], top_n)
                    
                    if feature in ['hashtags', 'processedDescTokens', 'processedTokens', 'emojis']:
                        for item in report[query_term][feature].keys():
                            logger.warning(f"report[query_term][feature][item][0:5]: {report[query_term][feature][item][0:5]}")
                            try:
                                report[query_term][feature][item] = [{'text': object_['val'], 'value': object_['count']} for object_ in report[query_term][feature][item]]
                            except Exception as exp:
                                logger.warning(f"ERROR: {exp}")
                                

                    if feature in ['processedDescTokens', 'processedTokens']:
                        if f"{feature}Stopped" not in report[query_term].keys():
                            report[query_term][f"{feature}Stopped"] = dict()
                        for item in report[query_term][feature].keys():
                            report[query_term][f"{feature}Stopped"][item] = [{'text': object_['text'], 'value': object_['value']} for object_ in report[query_term][feature][item] if object_['text'].lower() not in stopwords and len(object_['text']) > 1]


                    # terminate at top 150 items...
                    if feature in ['hashtags', 'emojis', 'media', 'mentions', 'urls', 'processedTokens', 'processedDescTokens', 'userScreenName', 'retweeters', 'retweeted']:
                        for sentiment in report[query_term][feature].keys():
                            report[query_term][feature][sentiment] = report[query_term][feature][sentiment][0:150]

                
                report[query_term]['top_tweets'] = report_groups_tweets
                report[query_term]['top_users'] = report_groups_users
                
                hits = max(hits, report[query_term]['count'])
                if len(report_groups_tweets['All Sentiments']) > 0:
                    datasetOrigin = 'Comment' if 'videoId' in report_groups_tweets['All Sentiments'][0].keys() and report_groups_tweets['All Sentiments'][0]['videoId'] != None else 'Tweets'
                else:
                    datasetOrigin = 'Tweets'
            except Exception as exp:
                logger.warning(f"ERROR: {exp}")
                if 'HTTP Error 404' in str(exp):
                    error_message = f'Data collection {solr_core} is not avaiable. Please check that Solr is running and the core {solr_core} is available.'
                else:
                    error_message = 'An error occured while fetching the data.'
                datasetOrigin = 'Tweets'
                if query_term in report:
                    report.pop(query_term)

        return report, hits, datasetOrigin, error_message
    
    
    def optimised_json_query_handler_topics(self, solr_core, keyword, rows=5000, interactionCommunity=None, communitiesList = None):
        """ It is the optimised function that is based on JSON query requests for Topics. It nees the query, solr \
        object and rows to be returned. The query is a dictionary of the keywords and the corresponding JSON \
        query, and in our system is built be @solr_query_builder.

        Args:
            :solr_core (str):  Name of the Solr core to query from.
            :keyword (str): Comma-separated list of keywords to query.
            :rows: (int, optional) Maximum number of datapoints to be returned for the topics query. Defaults to 5000.
            :random_seed: (int, optional) Random seed to control the random selection of data when number of results \
                exceeds the maximum number of rows. Defaults to 42.

        Returns:
            :tuple: Contains a dictionary with the report that corresponds to the query, and the total number of \
                tweets found for the query.
        """

        logger.info(f"THESE ARE THE COMMUNITIES --> {communitiesList}")
        # getting a random number from 0 to 10000, the seed is loaded form the interface.
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)

        report = dict()

        if keyword == None:
            keyword = "*"
        elif keyword.strip() == "" or keyword.strip() == "()":
            keyword = "*"
        
        hits = 0
        term_q = json.dumps(keyword)
        term_q = f'{str(term_q if term_q.isascii() else urllib.parse.quote(term_q))}'.replace("\"", "")

        facet_url = str(self.solrs[solr_core]) +  \
            f"select?random_{random_number}" + \
            f"&sort={interactionCommunity}%20desc%2CretweetCount%20desc%2CreplyCount%20desc&fl=id%2C%20videoId%2C%20fullText%2C%20embedding_5d%2C%20embedding_2d%2C%20sentiment%2C%20replyCommunity%2C%20retweetCommunity%2C%20" + \
            "&q.op=OR&q=" + term_q + \
            (f"%20AND%20{interactionCommunity}:(" + "%20OR%20".join(communitiesList) + ")" if communitiesList != None and len(communitiesList)>0 and type(communitiesList) == list and interactionCommunity != None and interactionCommunity in ["retweetCommunity","replyCommunity"] else "") + \
            "&rows=" + str(int(1.1*rows)) + "&indent=true"

        logger.info(f" THIS IS THE TOPIC MOD QUERY <=-=> \n{facet_url}\n <=-=>")
        start = time.time()
        response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))

        end = time.time()
        if keyword == "*":
            keyword = "All"
        logger.info(f"time taken: {end - start}")
        
        hits = response['response']['numFound']
        report = list(response['response']['docs'])
        return report, hits
    
    def get_network_of_users(self, solr_core, keyword, interaction):
        """A function that returns the network of users based on the interaction (retweet or reply) and the keyword.

        Args:
            :solr_core: (str) Solr core to be used.
            :keyword: (str) the search term.
            :interaction: (str) the network interaction (either retweet or reply).

        Returns:
            :dataFrame: (pandas.DataFrame) Two Pandas DataFrame, the first is network interaction df that has source, \
                target and weight. The second, nodes_df, has node (label), x and y (position in the graph), community \
                (int, the community number), degree (int, the noumber of edges), and desc (accounts' descriptions).
        """
        # retweet ( retweetTimes ), reply ( repliesTimes )?
        interaction_maps = {'retweet': 'retweetNetworkNodes', 'reply': 'replyNetworkNodes'}
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)

        if keyword == None:
            keyword = "*"
        elif keyword.strip() == "" or keyword.strip() == "()":
            keyword = "*"

        try:
            term_q = json.dumps(keyword)
            term_q = f'{str(term_q if term_q.isascii() else urllib.parse.quote(term_q))}'.replace("\"", "")
            facet_url = f'{str(self.solrs[solr_core])}select?random_{random_number}&sort=retweetCount%20desc&fl=userScreenName%2C%20usersDescription%2C%20{str(interaction_maps[interaction])}&rows={rowsLimit}&indent=true&q.op=OR&q={str(interaction_maps[interaction])}:*%20AND%20{term_q}'
            response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))



        except Exception as exp:
            logger.warning(f"Error: {exp}")
            facet_url = f'{str(self.solrs[solr_core])}select?random_{random_number}&sort=retweetCount%20desc&fl=userScreenName%2C%20usersDescription%2C%20{str(interaction_maps[interaction])}&rows={rowsLimit}&indent=true&q.op=OR&q={str(interaction_maps[interaction])}:*%20AND%20({quote(keyword)}){str(self.date_range)}{self.language_filter}{self.sentiment_filter}{self.country_filter}'
            response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
        
        keyword = "All" if keyword == "*" else keyword

        logger.info(f"len(response['response']['docs']) : {len(response['response']['docs'])}")
        if len(response['response']['docs']) > 0:
            network = list(response['response']['docs'])
            network_df = pd.DataFrame.from_records(network)
            network_df = network_df.explode(interaction_maps[interaction])
            
            network_df['target'] = network_df['userScreenName']
            if 'usersDescription' not in network_df:
                network_df['usersDescription'] = "" # to avoid the error of missing column in the YouTube data.
            desc = network_df[network_df['usersDescription']!=""][['target', 'usersDescription']].drop_duplicates(subset=["target"])
            desc.index = desc['target']
            desc = desc.to_dict(orient='index')
            network_df['source'] = network_df[interaction_maps[interaction]].apply(lambda x : x.split(" ")[0])
            network_df['node_community'] = network_df[interaction_maps[interaction]].apply(lambda x : int(x.split(" ")[1]))
            network_df['node_degree'] = network_df[interaction_maps[interaction]].apply(lambda x : int(x.split(" ")[2]))
            
            network_df['source_pos'] = network_df[interaction_maps[interaction]].apply(lambda x : x.replace(")","").split("(")[1] if len(x.split("(")) > 1 else "")
            network_df['x'] = network_df.source_pos.apply(lambda x : float(x.split(',')[0]) if len(x.split(',')) > 1 else "")
            network_df['y'] = network_df.source_pos.apply(lambda x : float(x.split(',')[1]) if len(x.split(',')) > 1 else "")
                            
            nodes_df = network_df[['source', 'node_community', 'node_degree', 'x', 'y']].copy().rename(columns={'source': 'node', 'node_community': 'community', 'node_degree': 'degree'})    
            nodes_df['desc'] = nodes_df.node.apply(lambda x: '<br>'.join(textwrap.wrap(str(desc[x]['usersDescription']), 64)) if x in desc else "")
            nodes_df = nodes_df.fillna("")
            network_df.drop(columns=[interaction_maps[interaction], 'userScreenName', 'source_pos'], inplace=True)
            network_df = network_df[network_df['target']!=network_df['source']].groupby(['target','source']).size().reset_index(name="weight")
            
            return network_df, nodes_df
        return None, None
    
    #This function will be used by the backend processing...
    def get_network_interactions(self, solr_core, interaction='retweet', interaction_options={'retweet': 'retweetTimes', 'reply': 'repliesTimes'}):
        """A function that returns the network of users based on the interaction (retweet or reply) and the keyword.
        It is used by backend processes to get the network of users for a given interaction and to perform community detection and graph representation.

        Args:
            solr_core (str): the Solr core to be used.
            interaction (str): the interaction type as specified in Solr (interaction field).

        Returns:
            json: A dictionary that holds the network of users (tweets authors) and the corresponding interactions.
        """
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)
        
        interactionMap = {'reply': 'userScreenName:*%20AND%20repliesTimes:*', 'retweet':'userScreenName:*%20AND%20(retweetTimes:*%20OR%20retweeters:*)' }
        communityMap = {'reply': 'userScreenName:*%20AND%20repliesTimes:*', 'retweet':'userScreenName:*%20AND%20(retweetTimes:*%20OR%20retweeters:*)' }
        facet_url = f'{str(self.solrs[solr_core])}select?random_{random_number}&sort=retweetCount%20desc&fl=id%2C%20userScreenName%2C%20createdAtDays%2C%20usersDescription%2C%20{str(interaction_options[interaction])}%2C%20retweeters%2C%20sentiment&rows={rowsLimit}&indent=true&q.op=OR&q={str(interactionMap[interaction])}'
        #print_this("---------")
        #logger.info(f"<=-=> {facet_url}")
        #print_this("=========")


        try:
            response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
        except Exception as exp:
            response = {"msg" : f"Error: {exp}"}
        finally:
            return response

    def get_network_stats(self, solr_core, keyword, interaction='retweet', limit=queryLimit):
        """A function that retrieves the network stats for a given interaction (retweet or reply).
        It is used by the interface backend to get the network stats.
        Args:
            :solr_core: (str) the name of the solr core to be used to search data from.
            :keyword: (str)
            :interaction: (str) the interaction name, either retweet or reply, to be mapped with the corresponding field in Solr.

        Returns:
            :dict: dict of data that holds both sentiments and communities_traffic.
        """
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)
        
        if keyword == None:
            keyword = "*"
        elif keyword.strip() == "" or keyword.strip() == "()":
            keyword = "*"
        
        interactionCommunity = self.solr_communities[interaction]['interactionCommunity']
        interactionCount = self.solr_communities[interaction]['interactionCount']
        
        func_ = "%27sum(" + interactionCount + ")%27"
        stats_json = {
            'limit':limit,
            'type':'terms',
            'sort':{'nb_accounts':'desc'},
            'field':interactionCommunity,
            'facet': {
                'retweeted': {
                    'type':'func',
                    'func':func_
                }, 'nb_accounts': {
                    'type':'func',
                    'func':'%27countvals(userScreenName)%27'
                },'most_ret_accounts': {
                    'limit':limit,
                    'type':'terms',
                    'field':'userScreenName',
                    'facet': {
                        'retweeters': {
                            'sort':{'func':'desc'},
                            'type':'func',
                            'func':func_
                        }
                    }
                }
            }
        }
        
        communities_traffic_json = {
            'sort':{'count':'desc'},
            'limit':-1,
            'type':'terms',
            'field':interactionCommunity,
            'facet': {
                'communities_traffic': {
                    'limit':-1,
                    'type':'terms',
                    'field':'createdAtDays'
                }
            }
        }
        
        try:
            try:
                term_q = json.dumps(keyword)
                term_q = f'{str(term_q if term_q.isascii() else urllib.parse.quote(term_q)).replace("%22", "").replace(" ", "%20")}'.replace("\"", "")
                query = term_q + self.language_filter + self.sentiment_filter + self.date_range + self.country_filter
                facet_url = str(self.solrs[solr_core]) + "select?json={query:'" + str(query) + "',limit:" + str(0) + ",facet:{stats:" + json.dumps(stats_json).replace('"', '').replace(' ', '') + ",communities_traffic:" + json.dumps(communities_traffic_json).replace('"', '').replace(' ', '') + "}}"

                #logger.info( f"<11>{facet_url}<11>")
                response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
            except Exception as exp:
                query = str(quote(keyword)) + self.language_filter + self.sentiment_filter + self.date_range + self.country_filter
                facet_url = str(self.solrs[solr_core]) + "select?json={query:'" + str(query) + "',limit:" + str(rowsLimit) + ",facet:{stats:" + json.dumps(stats_json).replace('"', '').replace(' ', '') + ",communities_traffic:" + json.dumps(communities_traffic_json).replace('"', '').replace(' ', '') + "}}"
                logger.info( f"<22>{facet_url}<22>")
                response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
            stats_facet = response['facets']['stats']['buckets'] if 'buckets' in response['facets']['stats'] else None if 'stats' in response['facets'] else [] if 'facets' in response else []
            communities_traffic_facet = response['facets']['communities_traffic']['buckets'] if 'buckets' in response['facets']['communities_traffic'] else None  if 'communities_traffic' in response['facets'] else [] if 'facets' in response else []
        except Exception as exp:
            logger.warning(f"Error: {exp}")
            stats_facet = None
            communities_traffic_facet = None
        response_dict = {'sentiments': dict(), 'communities_traffic': dict()}
        
        if stats_facet != None:
            response_dict['sentiments'] = [{
                'id': item['val'],
                'Community' : item['val'],
                'Nb active accounts' : item['nb_accounts'],
                'Nb tweets per account': item['count'] / item['nb_accounts'],
                'Nb retweets per tweet': item['retweeted'] / item['count'],
                'Top 20 most retweeted accounts': [x['val'] for x in item['most_ret_accounts']['buckets']],
                } for item in stats_facet if not item['val'] == 0]
            
        if communities_traffic_facet != None:
            response_dict['communities_traffic'] = {
                item['val'] : sorted([{'Date': x['val'], 'Count': x['count']} for x in item['communities_traffic'].get('buckets', [])], key=lambda a: a['Date'], reverse=False)
            for item in communities_traffic_facet if not item['val'] in [-1, 0]}
        return response_dict


    def get_network_map_info(self, solr_core, keyword, interaction, communities):
        """A function that retrieves the map information for a given interaction (retweet or reply).
        Args:
            :solr_core: (str) the name of the solr core to be used to search data from.
            :keyword: (str)
            :interaction: (str) the interaction name, either retweet or reply, to be mapped with the corresponding field in Solr.

        Returns:
            :dict: dict of data that holds the geolocation information per community
        """
        interaction_maps = {'retweet': 'retweetCommunity', 'reply': 'replyCommunity'}
        random.seed(self.random_seed)
        random_number = random.randint(0,9999)

        if keyword == None:
            keyword = "*"
        elif keyword.strip() == "" or keyword.strip() == "()":
            keyword = "*"

        comm = interaction_maps[interaction]

        logger.info(f"COMMUNITIES FILTER -->{comm}")
        logger.info(communities)

        communities_filter = self.stringify_filter(communities, comm)

        stats_json = {
            'type':'terms',
            'field': comm,
            'facet': {
                'tweets_locations_by_communities': {
                    'limit':-1,
                    'type':'terms',
                    'field':'locationGps'
                }, 'users_locations_by_communities': {
                    'limit':-1,
                    'type':'terms',
                    'field':'userLocation'
                }, 'Languages_per_community': {
                    'limit':-1,
                    'type':'terms',
                    'field':'language'
                }
            }
        }
        try:
            term_q = json.dumps(keyword)
            term_q = f'{str(term_q if term_q.isascii() else urllib.parse.quote(term_q)).replace("%22", "").replace(" ", "%20")}'.replace("\"", "")
            query = term_q + self.language_filter + self.sentiment_filter + self.date_range + self.country_filter + communities_filter
            facet_url = str(self.solrs[solr_core]) + "select?json={query:'" + str(query) + "',limit:" + str(0) + ",facet:{stats:" + json.dumps(stats_json).replace('"', '').replace(' ', '') + "}}"

            #logger.info( f"<11>{facet_url}<11>")
            response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
        except Exception as exp:
            query = str(quote(keyword)) + self.language_filter + self.sentiment_filter + self.date_range + self.country_filter + communities_filter
            facet_url = str(self.solrs[solr_core]) + "select?json={query:'" + str(query) + "',limit:" + str(rowsLimit) + ",facet:{stats:" + json.dumps(stats_json).replace('"', '').replace(' ', '') + "}}"
            logger.info( f"<22>{facet_url}<22>")
            response = json.loads(urllib.request.urlopen(urllib.request.Request(facet_url)).read().decode('utf-8'))
        
        
        stats_facet = response['facets']['stats']['buckets'] if 'facets' in response and 'stats' in response['facets'] and 'buckets' in response['facets']['stats']  else []

        results = {
            "tweets_locations_by_communities": {},
            "users_locations_by_communities": {},
            "Languages_per_community": {}
            }
        if len(stats_facet) >0:
            for item in stats_facet:
                val = str(item['val'])
                if val == 0:
                    continue
                results["tweets_locations_by_communities"][val] = item["tweets_locations_by_communities"]['buckets']
                results["users_locations_by_communities"][val] = item["users_locations_by_communities"]['buckets']
                results["Languages_per_community"][val] = [
                    {
                        "Language": b["val"][0].upper() + b["val"][1:],
                        "Count": b["count"]
                    } for b in item["Languages_per_community"]['buckets']]

            for feature in ["tweets_locations_by_communities", "users_locations_by_communities"]:
                all_communities = defaultdict(int)
                for community in results[feature]:
                    for count_dict in results[feature][community]:
                        all_communities[count_dict["val"]] = count_dict["count"]

                results[feature]["All Communities"] = [{"val": key, "count": value} for key, value in all_communities.items()]
            return results
        return []



    def get_date(self, solr, query = "*:*",reverse = False):
        """ A function to convert the timestamps of tweets as returned by the Twitter API into a date in the \
            YYYY-MM-DD format. It is used during the pre-processing of the data (i.e. when onboarding a new dataset).

        Args:
            :solr: (pysolr.Solr) the solr object used to search data from.
            :reverse: (bool) If true, will get the dates in descending order when retrieving them from Solr.

        Returns:
            :list[str]: The list of dates in YYYY-MM-DD format.
        """
        try:
            resp = solr.search(q=query, fl="createdAtDays", sort="createdAtDays desc" if reverse else "createdAtDays asc", rows=1)
            logger.info(resp.docs[0])
            tmp = datetime.strptime(resp.docs[0]['createdAtDays'],  '%Y-%m-%d') + timedelta(days=1 if reverse else 0)
            logger.info(f"tmp : {tmp}")
            return datetime.strftime(tmp, '%Y-%m-%dT00:00:00Z')
        except Exception as exp:
            logger.warning(exp)
            return ""

    def get_no_sentiment_items(self, solr_core, queryString = None):
        """ A function to count the number of datapoints in the Solr that do not have a sentiment label. This is used \
        to identify the data that still needs to be preprocessed.

        Args:
            :solr_core: (str) the Solr core to search data from.
            :queryString: (str) Solr query used to exclude data to take into account from Solr core

        Returns:
            :tuple(list(dict), int): A tuple containing the list of results and their count.
        """
        start = 0
        rows = 20000
        if solr_core not in self.solrs:
            logger.warning("Selected core is not registered in the system!")
            return [], 0
        url = self.solrs[solr_core]
        solr = pysolr.Solr(url, timeout=120)
        start_time = self.get_date (solr, query="*:*")
        q = f"NOT sentiment_s:{queryString}" if queryString else "NOT sentiment_s:Done"
        end_time = self.get_date (solr, query="*:*", reverse=True)

        logger.info('Get tweets with no processed sentiments from Solr ...')
        if start_time != "" and end_time != "":
            q = f'{q} AND createdAt:[{str(start_time)} TO {str(end_time)}]'
        
        logger.info(f"start_time: {start_time}")
        result = solr.search(q=q, **{'fl':'id, fullText, language, languagePlatform','start':start , 'rows':rows})
        max_row = result.hits
        logger.info(f'Number of hits : {max_row}')
        return list(result.docs), max_row

    def get_no_location_items(self, solr_core, queryString=None):
        """ A function to count the number of datapoints in the Solr that do not have a location label. This is used \
        to identify the data that still needs to be preprocessed.

        Args:
            :solr_core: (str) the Solr core to search data from.
            :queryString: (str) Solr query used to exclude data to take into account from Solr core

        Returns:
            :tuple(list(dict), int): A tuple containing the list of results and their count.
        """
        start = 0
        rows = 20000
        if solr_core not in self.solrs:
            logger.warning("Selected core is not registered in the system!")
            return [], 0
        url = self.solrs[solr_core]
        solr = pysolr.Solr(url, timeout=120)
        start_time = self.get_date (solr)
        q = f"NOT location_s:{queryString}" if queryString else "NOT (locationGps:* AND userLocation:*)"

        end_time = self.get_date (solr, reverse=True)

        logger.info('Getting documents with no processed location from Solr ...')
        if start_time != "" and end_time != "":
            q = f'{q} AND createdAt:[{str(start_time)} TO {str(end_time)}]'
        result = solr.search(q=q, **{'fl':'id, placeCountry, placeFullName, userLocationOriginal','start':start , 'rows':rows})
        max_row = result.hits
        logger.info(f'Number of hits : {max_row}')
        return list(result.docs), max_row
        
    def get_network_interaction(self, solr_core, interaction='retweet'):
        """ A function to extract the edges information from Solr (i.e. retweets between individual accounts).

        Args:
            :solr_core: (str) the Solr core to search data from.
            :interaction: (str) the type network to get the data from (either "retweet" or "reply").

        Returns:
            :tuple(list(dict), int): A tuple containing the list of results and their count.
        """
        start = 0
        rows = 20000
        if solr_core not in self.solrs:
            logger.warning("Selected core is not registered in the system!")
            return {}, 0
        url = self.solrs[solr_core]
        solr = pysolr.Solr(url, timeout=120)
        if interaction == 'reply':
            q = 'repliesTimes:*'
            fl_ = 'id,userScreenName,repliesTimes'
        else:
            interaction = 'retweet'
            q = 'retweeters:* OR retweetTimes:*'
            fl_ = 'id,userScreenName,retweeters,retweetTimes'
        interaction_maps = {'retweet': 'retweetTimes', 'reply': 'repliesTimes'}

        result = solr.search(q=q, **{'start':start , 'rows':0})
        hits = result.hits
        logger.info('Get network interaction from Solr ...')
        users_edges = dict()
        while start < hits:
            results = solr.search(q=q, **{'fl':fl_,'start':start , 'rows':rows})
            for item in results.docs:
                if 'userScreenName' in item and item['userScreenName'] not in users_edges:
                    users_edges[item['userScreenName']] = dict()

                accounts_ = []
                if interaction_maps[interaction] in item:
                    for interactionTime in item[interaction_maps[interaction]]:
                        accounts_.append(interactionTime.split(' ')[0])

                if interaction == 'retweet':
                    accounts_ = set(accounts_ + item['retweeters'])
                else:
                    accounts_ = set(accounts_)
                for account_ in accounts_:
                    if 'userScreenName' in item:
                        if account_ not in users_edges[item['userScreenName']]:
                            users_edges[item['userScreenName']][account_] = 1
                        else:
                            users_edges[item['userScreenName']][account_] += 1

            start+= rows

        logger.info(f"Number of hits : {hits}")
        return users_edges, hits

    def get_text_data(self, solr_core, considerAll=False):
        """ A function to extracts text information from a given Solr core.

        Args:
            :solr_core: (str) the Solr core to search data from.
            :considerAll: (bool) Whether or not to return data for which 5D and 2D embeddings already exist in Solr (i.e. \
                data that already has been pre-processed in the past)

        Returns:
            :tuple(list(str), int): A tuple containing the list of results and their count.
        """
        start = 0

        rows = 20000
        if solr_core not in self.solrs:
            logger.warning("Selected core is not registered in the system!")
            return [], 0
        url = self.solrs[solr_core]
        solr = pysolr.Solr(url, timeout=120)
        q = '*:*' if considerAll else 'NOT embedding_2d:* OR NOT embedding_5d:*'
        
        result = solr.search(q='*:*', **{'start':start , 'rows':0})
        hits = result.hits
        logger.info('Get documents from Solr ...')
        documents = []
        while start < hits:
            results = solr.search(q='*:*', **{'fl':'id,fullText','start':start , 'rows':rows})
            #for item in results.docs:
            documents += list(results.docs)
            logger.info(f"Getting documents from Solr {len(documents)} done out of {hits}")
            start+= rows

        logger.info(f"Number of hits : {hits}")
        return documents, hits

    def write_location_to_solr(self, documents_list, solr_core, max_row):
        """ updated the location of the tweets in the solr core. The function recieves the tweets list and the solr core name and update the location of the tweets in the solr core. The tweets list includes the id and the location details.
        
            Args:
                documents_list (list): List of dicts that includes the id and the location details of the tweets (userLocation and locationGps).
                solr_core (str): the name of the collection in the solr.
                max_row (int): The maximim number of rows to be updated, to print out the updating information.
        
            Returns:
                boolean: the status of the update operation, True if the operation is done successfully, False otherwise.
        """
        try:
            if solr_core not in self.solrs:
                logger.warning("Selected core is not registered in the system!")
                return False
            url = self.solrs[solr_core]
            solr = pysolr.Solr(url, timeout=120)
            status = ''
            i = 0
            logger.info(f"write data to solr, {len(documents_list)}")
            while ('"status">0<' not in status and i < 3):
                status = solr.add(documents_list, softCommit=False , fieldUpdates={'userLocation':'set', 'locationGps':'set'})
                i+=1
            if '"status">0<' not in status:
                logger.warning(f'[write_location_to_solr]: Error occurred, server response: {status}')
                return False
            else:
                logger.info(f"[write_location_to_solr]: Location update Done for {str(len(documents_list))} out of {str(max_row)}")
                sys.stdout.flush()
                return True
        except Exception as exp:
            logger.warning('[write_location_to_solr]: Exception ', str(exp), ' occurred, try later')
            return False

    def add_objects_to_solr(self, solr_object, objects, fieldUpdates, threshold=1000):
        """ A function to add data to Solr once it has been pre-processed

        Args:
            :solr_object: (pysolr.Solr) Solr object
            :objects: (list(dict)) list of data objects to be added to Solr.
            :fieldUpdates: (dict) Define whether to replace or amend fields in Solr
            :threshold: (int) Limit on the number of objects to add to Solr in one time.

        Returns:
            :list(dict): The same "objects" provided as input into the function
        """
        try:
            logger.info(f'[add_objects_to_solr]: Adding {len(objects)} items to Solr ...')
            while len(objects) > 0:
                res = solr_object.add(objects[0:threshold], softCommit=True,fieldUpdates=fieldUpdates)
                if '"status">0<' not in res:
                    logger.warning('[add_objects_to_solr]: Something went wrong. Please check the Solr core and values.')
                    return objects
                else:
                    objects = objects[threshold:]
                    logger.info(f'[add_objects_to_solr]: Adding items to Solr done. {len(objects)} waiting to be added. ')
                    threshold = 1000
        except Exception as exp:
            logger.warning('[add_objects_to_solr]: Exception (', str(exp), ') occurred, try later')
            logger.warning(f"{len(objects)} still needed to be added to solr.")
        return objects
        
    def add_videos_to_solr(self, solr_core, videos, reduced=1):
        """Add list of videos to solr core (for YouTube data). Update fields of the items if they already exist in Solr.

        Args:
            solr_core (str): the name of the solr core to be used to add the items.
            items (List): A list of dicts that holds the items to be added to Solr. It should have the same fields as the Solr core.
        """
        threshold = 1000 if reduced < 2 else int(1000 / (reduced))        
        if len(videos) > 0:
            try:
                if solr_core in self.solrs:
                    url = self.solrs[solr_core]
                    solr = pysolr.Solr(url, timeout=300)
                    distinct_items = ["domains", "emoji", "emojis", "emotion_distribution", "features", "hashtags", "mentions", "retweeters", "retweetTimes", "matchingRule", "media", "processedDescTokens", "processedTokens", "quoteTimes", "quoteTweets", "quoters", "repliesTimes", "repliesTweets", "replyNetworkNodes", "retweetNetworkNodes", "sentiment_distribution", "topic", "urls"]
                    fieldUpdates = {k: 'set' if k not in distinct_items else 'add-distinct' for k in list(videos[0].keys()) if k != 'id'}
                    documents = []
                    for item in videos:
                        if '_version_' in item.keys():
                            item.pop('_version_')
                        
                        resp = solr.search(q=f'videoId:"{item["videoId"]}" AND NOT videoCreatedAt:*', fl="id, videoId", rows=1000)
                        documents = list(resp.docs)
                        while len(documents) > 0:
                            for document in documents:
                                if '_version_' in document.keys():
                                    document.pop('_version_')
                                if 'videoId' in document.keys() and document['videoId'] == item['videoId']:
                                    for k in item.keys():
                                        document[k] = item[k]
                            
                            if len(documents) > 0:
                                documents = self.add_objects_to_solr(solr_object = solr, objects=documents, fieldUpdates=fieldUpdates, threshold=threshold)
                            resp = solr.search(q=f'videoId:"{item["videoId"]}" AND NOT videoCreatedAt:*', rows=1000)
                            documents += list(resp.docs)
                        if len(documents) > 0:
                            documents = self.add_objects_to_solr(solr_object = solr, objects=documents, fieldUpdates=fieldUpdates, threshold=threshold)
                    solr.commit()
                    return documents
                else:
                    logger.warning('[add_videos_to_solr]: Error (', str(solr_core), ') core is not registered in the system!')
            except Exception as exp:
                logger.warning('[add_videos_to_solr]: Exception (', str(exp), ') occurred, try later')
                logger.warning(f"{len(documents)} still needed to be added to solr.")
                return documents
        
        
    def add_items_to_solr(self, solr_core, items, reduced=1):
        """Add list of items to solr core. Update fields of the items if they already exist in Solr.

        Args:
            solr_core (str): the name of the solr core to be used to add the items.
            items (List): A list of dicts that holds the items to be added to Solr. It should have the same fields as the Solr core.
        """
        if len(items) > 0:
            threshold = 1000 if reduced < 2 else int(1000 / (reduced))
            try:
                if solr_core in self.solrs:
                    url = self.solrs[solr_core]
                    solr = pysolr.Solr(url, timeout=300)
                    distinct_items = ["domains", "emoji", "emojis", "emotion_distribution", "features", "hashtags", "mentions", "retweeters", "retweetTimes", "matchingRule", "media", "processedDescTokens", "processedTokens", "quoteTimes", "quoteTweets", "quoters", "repliesTimes", "repliesTweets", "replyNetworkNodes", "retweetNetworkNodes", "sentiment_distribution", "topic", "urls"]
                    fieldUpdates = {k: 'set' if k not in distinct_items else 'add-distinct' for k in list(items[0].keys()) if k != 'id'}

                    for item in items:
                        if '_version_' in item.keys():
                            item.pop('_version_')
                    while len(items) > 0:
                        res = solr.add(items[0:threshold], softCommit=True, fieldUpdates=fieldUpdates)
                        if '"status">0<' not in res:
                            logger.warning('Something went wrong. Please check the Solr core and values.')
                            return items
                        else:
                            logger.info(f'[add_items_to_solr]: Adding items to Solr done. {len(items[threshold:])} waiting to be added. ')
                            items = items[threshold:]
                            threshold = 1000
                    solr.commit()
                    return items
                else:
                    logger.warning('[add_items_to_solr]: Error (', str(solr_core), ') core is not registered in the system!')
            except Exception as exp:
                logger.warning(f'[add_items_to_solr]: Exception ({str(exp)}) occurred, try later')
                logger.warning(f"{len(items)} still needed to be added to solr.")
        return items