#!/usr/bin/env python3
"""
Python script for importing tweets from a stored file into Apache Solr.

This script reads tweets from a file and imports them into an Apache Solr instance.
It assumes that the tweets are stored in a specific format within the file.

Usage:
    python 2_import_data_to_solr.py -c core_name -s source_file

Requirements:
    - Apache Solr instance running and accessible
    - Python library 'pysolr' installed (install via 'pip install pysolr')
"""

import sys
import json
from os import listdir
from os.path import isfile, join, abspath
import argparse
from utils import compress_file, create_logger
logger = create_logger(f"2_import_data_to_solr", file=f"import_data_to_solr")
try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    logger.warning("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    logger.warning("exiting...")
    sys.exit(-1)
from solr_class import *

dataSource = SolrClass(filters={})

if __name__== "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help="The tweets source file, each tweet in a separate line.", default=None)
    parser.add_argument('-c', '--core', help="The Solr core to write the data to.", default=None)

    args = parser.parse_args()
    core = args.core
    source = args.source

    if core != None and source != None:
        try:
            workfiles = [source]
            if not isfile(source):
                workfiles = list(set([join(source,f) for f in listdir(source) if isfile(join(source, f)) and not f.endswith('.gz') and not f.endswith('.bz2')]))
            logger.info(f"[{__name__}]: {workfiles}")
            for source in  workfiles:
                logger.info(f"[{__name__}]: {source}")
                tweets = dict()
                with open(source, "r", encoding="utf-8") as fin:
                    for t in fin:
                        t = json.loads(t)
                        if 'defaultLanguage' in t.keys():
                            t['languagePlatform'] = t.pop('defaultLanguage')
                        if 'textOriginal' in t.keys():
                            t['originalText'] = t.pop('textOriginal')
                        if 'authorDisplayName' in t.keys():
                            t['userScreenName'] = t.pop('authorDisplayName')
                        if 'authorProfileImageUrl' in t.keys():
                            t['authorImageUrl'] = t.pop('authorProfileImageUrl')
                        
                        if 'textDisplayCleared' in t.keys():
                            t['fullText'] = t.pop('textDisplayCleared')
                        if 'likeCount' in t.keys():
                            t['favoriteCount'] = t.pop('likeCount')
                        if 'publishedAt' in t.keys():
                            t['createdAt'] = t.pop('publishedAt')
                        if 'parentId' in t.keys():
                            t['inReplyToId'] = t.pop('parentId')
                        #just consider tweets with id and author screen name.
                        if 'userScreenName' in t.keys() and t['userScreenName'] != "" and 'id' in t.keys():
                            tweets[t['id']] = t
                        
                        if len(tweets) >= 100000:
                            if len(dataSource.add_items_to_solr(core, list(tweets.values()))) == 0:
                                tweets = dict()
                if len(dataSource.add_items_to_solr(core, list(tweets.values()))) == 0:
                    tweets = dict()
                compress_file(source, f"{source}.tar.gz")

        except Exception as exp:
            logger.warning(f"[{__name__}]: ERR: reading from file failed, please check Solr path and the data file!\n{exp}")
    elif core == None:
        logger.warning(f"[{__name__}]: ERR: Please specify the Solr core!\nSomthing similar to: python 2_import_data_to_solr.py -c core_name -s path_to_file ")
    else:
        logger.warning(f"[{__name__}]: ERR: Please specify the source file!\nSomething similar to:  python 2_import_data_to_solr.py -c core_name -s path_to_file")
