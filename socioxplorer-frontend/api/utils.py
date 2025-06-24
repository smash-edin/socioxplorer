import time
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import re
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig_DATABASE, ApplicationConfig

LOG_FOLDER = ApplicationConfig.LOG_FOLDER
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


def print_this(message):
    """
    An auxiliary function that prints a message within a square of (hash)s.
    
    Args:
        :message: (obj) The message to be printed, preferably a string.
    """
    len_message = min(80, len(f"## {message} ##"))
    print('#'*len_message + f'\n## {message} ##\n' + '#'*len_message)

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
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if file:
        file_handler = TimedRotatingFileHandler(filename=f"{LOG_FOLDER}/{file}.log", when='midnight', interval=1, backupCount=0)#when midnight, s (seconds), M (minutes)... etc
        file_handler.setFormatter(logging_formatter)
        logger.addHandler(file_handler)
    return logger

MAX_VOL = 500
def initialize_database():
    """Function to initialise the database if it does not yet exist.

    Args:
        :req: (dict) Query header sent to API endpoint

    Returns:
        :source: (str) Name of dataset/Solr core
        :keywords_list: (list[str]) List of keywords to filter data by
        :filters: (dict) Dictionary containing the date_start, date_end, language, sentiment, location, randomSeed \
            and location_type filters to filter down the data.
        :operator: (str) Whether the filtered data needs to contain all keywords together ("AND") or only one of the \
            keywords at least ("OR")
        :limit: (int) Maximum number of results to return
    """
    print_this("Initializing the system database")
    username = ""
    password = ""
    while username == "":
        username = input(f"Please enter the admin username: [{ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH}-{ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH} letters and numbers (no special chars and no spaces.)]: ")
        pattern = r"^(?!.*(.)\1{3,})[A-Za-z][A-Za-z0-9_-]{" + str(ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH-1) + "," + str(ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH-1) + "}$"
        if not re.match(pattern , username):
            logger.warning(f"ERROR: \nPlease re-enter the admin username with the following conditions:\n\tEnglish letters, Numbers, and the special chars ('-' or '_'),\n\tIt must start with a letter,\n\tIt must be {ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH} to {ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH} chars.")
            username = ""

    while password == "":
        import getpass
        password = getpass.getpass(prompt = f"Please enter the admin password [{ApplicationConfig_DATABASE.PASSWORD_MIN_LENGTH}-{ApplicationConfig_DATABASE.PASSWORD_MAX_LENGTH} chars, with special characters and no spaces.]: ")
        pattern = r"^(?!.*(.)\1{3,})[A-Za-z0-9_-]{" + str(ApplicationConfig_DATABASE.PASSWORD_MIN_LENGTH) + "," + str(ApplicationConfig_DATABASE.PASSWORD_MAX_LENGTH) + "}$"
        if not re.match(pattern , password):
            logger.warning("ERROR: \nPlease re-enter the admin password with the following conditions:\n\tEnglish letters, Numbers, and the special chars ('-' or '_'),\n\tIt must be 6 to 12 chars.")
            password = ""
    return username, password

def get_tf_idf(df, text_column, label_column, labels_list=None, n=40):
    """Function that return the N most frequent words for each topic.

    Args:
        :df: (pandas.DataFrame) Dataframe containing texts and their labels
        :text_column: (str) name of column containing the text from which to generate TF-IDF (i.e. "processed_text" or \
            "description")
        :label_column: (str) name of column containing the label of each text from which to generate TF-IDF (i.e. \
            "Topic" or "Community")
        :n: (int) Number of top words to return per topic.

    Returns:
        :dict: Dictionary with, as an entry for each topic, a list of dictionaries with the keys "text" (the word) and \
            "value" (the TF-IDF value for this word).
    """
    if len(df) == 0:
        return None
    start = time.time()
    df = df[df[text_column].apply(lambda x: isinstance(x, str) and len(x) > 0)]

    if not labels_list is None:
        print("THIS IS THE LABELS LIST IN TF-IDF FUNCTION", labels_list)
        df = df[df[label_column].isin(labels_list)]

    # Give unique IDs to texts
    m=len(df)
    df['Doc_ID'] = range(m)

    # Aggregate texts per group
    docs_per_group = df.groupby([label_column], as_index = False).agg({text_column: ' '.join})
    documents = docs_per_group[text_column].values

    if (len(documents)>0):
        # Get the frequency of each word per group
        count = CountVectorizer(ngram_range=(1, 1), stop_words="english").fit(documents)
        t = count.transform(documents).toarray()

        #print("--> COUNTS:", t)
        epsilon = 0# 1e-8
        w = t.sum(axis=1) + epsilon
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        # Extract top N words per group
        words = count.get_feature_names_out()
        labels = list(docs_per_group[label_column])
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -n:]
        top_n_words = {str(label): [{"text": words[j], "value": tf_idf_transposed[i][j]} for j in indices[i] if tf_idf_transposed[i][j] == tf_idf_transposed[i][j]][::-1] for i, label in enumerate(labels)}

        # Print total time for this function to execute
        end = time.time()
        #print("\t\t...time = %.1f" % (end - start))
        return top_n_words
    return {}


def get_request_components(req):
    """Helper function to parse the data from the query header sent to API endpoint.

    Args:
        :req: (dict) Query header sent to API endpoint

    Returns:
        :source: (str) Name of dataset/Solr core
        :keywords_list: (list[str]) List of keywords to filter data by
        :filters: (dict) Dictionary containing the date_start, date_end, language, sentiment, location, randomSeed \
            and location_type filters to filter down the data.
        :operator: (str) Whether the filtered data needs to contain all keywords together ("AND") or only one of the \
            keywords at least ("OR")
        :limit: (int) Maximum number of results to return
    """
    print_this("Getting the request components")
    print_this(f"req.keys(): {req.keys()}")
    source = req['dataSource'] if 'dataSource' in req.keys() else req['source'] if 'source' in req.keys() else None
    keywords_list = req['keywords'] if ('keywords' in req.keys()) else []
    keywords_list = [x.strip() for x in keywords_list.strip().split(',')] if type(keywords_list) == str else keywords_list
    keywords_list = list(set(keywords_list))
    filters = dict()
    filters["date_start"] = req['date_start'] if 'date_start' in req.keys() else None
    filters["date_end"] = req['date_end'] if 'date_end' in req.keys() else None
    filters["language"] = req['language'] if 'language' in req.keys() else None
    filters["sentiment"] = req['sentiment'] if 'sentiment' in req.keys() else None
    filters["location"] = req['location'] if 'location' in req.keys() else None
    filters["randomSeed"] = req['random_seed'] if 'random_seed' in req.keys() else 555 #TODO change it to random.randint(0,9999)
    filters["location_type"] = req['location_type'] if 'location_type' in req.keys() else None
    operator = req['operator'] if 'operator' in req.keys() else 'AND'
    limit = req['limit'] if 'limit' in req.keys() else MAX_VOL
    return source, keywords_list, filters, operator, limit