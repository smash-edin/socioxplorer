from dotenv import load_dotenv
import os
import secrets
load_dotenv()


class ApplicationConfig_DATABASE:
    USERNAME_MIN_LENGTH = 5
    USERNAME_MAX_LENGTH = 12
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_MAX_LENGTH = 12


class ApplicationConfig:
    CONDA_VENV = 'venv'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./db.db'
    SECRET_KEY = os.environ['SECRET_KEY']
    SOLR_URL = 'http://127.0.0.1'
    SOLR_PORT = 10196
    SOLR_PATH = '../../../solr-9.3.0/'
    SOLR_CORES = []
    SOLR_NETWORKS = {'reply': {'field': 'repliesTimes', 'time': True},
        'retweet': {'field': 'retweetTimes', 'time': True}}
    SOLR_COMMUNITIES = {'reply': {'interactionCommunity': 'replyCommunity',
        'interactionCount': 'replyCount'}, 'retweet': {
        'interactionCommunity': 'retweetCommunity', 'interactionCount':
        'retweetCount'}}
    ANALYSIS_SERVICES = ['sentiment', 'location']
    SENTIMENT_API_PORT = 10077
    SA_URL = f'http://127.0.0.1:{SENTIMENT_API_PORT}/api/predict'
    LOCATION_API_PORT = 10066
    LOCATION_URL = f'http://127.0.0.1:{LOCATION_API_PORT}/api/get_locations'
    LOG_FOLDER = '../.log/'
    LANGUAGE_DICT = {'Non_text': 'NonText', 'af': 'afrikaans', 'sq':
        'albanian', 'am': 'amharic', 'ar': 'arabic', 'arz': 'arabic', 'an':
        'aragonese', 'hy': 'armenian', 'as': 'assamese', 'av': 'avaric',
        'az': 'azerbaijani', 'ba': 'bashkir', 'eu': 'basque', 'be':
        'belarusian', 'bn': 'bengali', 'bh': 'bihari', 'bs': 'bosnian',
        'br': 'breton', 'bg': 'bulgarian', 'my': 'burmese', 'ca': 'catalan',
        'ce': 'chechen', 'zh': 'chinese', 'cv': 'chuvash', 'kw': 'cornish',
        'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
        'dv': 'divehi', 'nl': 'dutch', 'en': 'english', 'eo': 'esperanto',
        'et': 'estonian', 'fi': 'finnish', 'fr': 'french', 'gl': 'galician',
        'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gn': 'guarani',
        'gu': 'gujarati', 'ht': 'haitian', 'he': 'hebrew', 'hi': 'hindi',
        'hu': 'hungarian', 'ia': 'interlingua', 'id': 'indonesian', 'ie':
        'interlingue', 'ga': 'irish', 'io': 'ido', 'is': 'icelandic', 'it':
        'italian', 'ja': 'japanese', 'jv': 'javanese', 'kn': 'kannada',
        'kk': 'kazakh', 'km': 'khmer', 'ky': 'kirghiz', 'kv': 'komi', 'ko':
        'korean', 'ku': 'kurdish', 'la': 'latin', 'lb': 'luxembourgish',
        'li': 'limburgan', 'lo': 'lao', 'lt': 'lithuanian', 'lv': 'latvian',
        'gv': 'manx', 'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay',
        'ml': 'malayalam', 'mt': 'maltese', 'mr': 'marathi', 'mn':
        'mongolian', 'ne': 'nepali', 'nn': 'norwegian', 'no': 'norwegian',
        'oc': 'occitan', 'or': 'oriya', 'os': 'ossetian', 'pa': 'punjabi',
        'fa': 'persian', 'pl': 'polish', 'ps': 'pashto', 'pt': 'portuguese',
        'qu': 'quechua', 'rm': 'romansh', 'ro': 'romanian', 'ru': 'russian',
        'sa': 'sanskrit', 'sc': 'sardinian', 'sd': 'sindhi', 'sr':
        'serbian', 'gd': 'gaelic', 'si': 'sinhala', 'sk': 'slovak', 'sl':
        'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
        'sw': 'swahili', 'sv': 'swedish', 'ta': 'tamil', 'te': 'telugu',
        'tg': 'tajik', 'th': 'thai', 'bo': 'tibetan', 'tk': 'turkmen', 'tl':
        'tagalog', 'tr': 'turkish', 'tt': 'tatar', 'ug': 'uyghur', 'uk':
        'ukrainian', 'ur': 'urdu', 'uz': 'uzbek', 'vi': 'vietnamese', 'wa':
        'walloon', 'cy': 'welsh', 'fy': 'frisian', 'yi': 'yiddish', 'yo':
        'yoruba', 'lang': 'english'}
    LANGUAGE_DICT_INV = {v: k for k, v in LANGUAGE_DICT.items() if k not in
        ['arz', 'no', 'lang']}
    REPORTS_FOLDER = '../../.reportsData'
    SNA_TIMER = 5
    SNA_THRESHOLD = 1
    LIMITED_RESOURCE = False
    BATCH_SIZE = 100


class ApplicationPaths:
    DATA_EXTRACTION_SERVICE_PATH = '1_extract_data.py'
    YOUTUBE_DATA_EXTRACTION_SERVICE_PATH = '1_extract_youtube_data.py'
    IMPORT_DATA_TO_SOLR_SERVICE_PATH = '2_import_data_to_solr.py'
    IMPORT_YOUTUBE_DATA_TO_SOLR_SERVICE_PATH = (
        '2_import_YouTube_data_to_solr.py')
    LOCATION_CLIENT_PATH = '3_update_locations.py'
    SENTIMENT_CLIENT_PATH = '4_update_sentiments.py'
    SENTIMENT_API_CODE = 'analyser_main'
    LOCATION_API_CODE = 'location_api'
    TOPICS_EXTRACTION_PATH = '../sentence_embeddings'
    NETWORK_INTERACTION_PATH = '../network_interaction'
    SNA_DATA_DIR = f'{NETWORK_INTERACTION_PATH}/data'
    SNA_DATA_FILE = f'{SNA_DATA_DIR}/df_data'
    EMBEDDINGS_DATA_DIR = f'{TOPICS_EXTRACTION_PATH}/data'
    EMBEDDINGS_DATA_FILE = f'{EMBEDDINGS_DATA_DIR}/df_data'
    EMBEDDINGS_MODEL_PATH = 'all-mpnet-base-v2'
    SENTIMENT_ANALYSIS_MODEL_PATH = (
        'cardiffnlp/twitter-xlm-roberta-base-sentiment')
