import sys
from os.path import abspath, join
try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig
from solr_class import *
import datetime as dt
from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
import flask_praetorian
from model.models import db, User, Search, SNAUsersCommunitiesMap
from datetime import datetime, timedelta
from bokeh.embed import json_item
import time
import json
import gzip
import copy
import pandas as pd
from topic_modelling_utils import *
from sna_utils import *
import traceback
import re
from utils import create_logger, print_this, get_tf_idf, get_request_components, initialize_database
logger = create_logger(f"API UI-Backend", file=f"api")

reportFolder = ApplicationConfig.REPORTS_FOLDER

with open(f'{os.path.abspath("../config")}/allowedOrigins.js') as dataFile:
    data = dataFile.read()
    obj = data[data.find('[') : data.rfind(']')+1]
    allowedOrigins = eval(obj)
    
"""This is the main Flask API file containing all API endpoints. This API is used to retrieve data from the Solr core,
in which the data is indexed, and process it into a format expected by the React UI.
"""

CURRENT_PATH = os.path.dirname(__file__)

app = Flask(__name__, template_folder='html')
app.config.from_object(ApplicationConfig)
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6  # 0 (no compression) to 9 (max compression)
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress if response is larger than this size in bytes

CORS(app, supports_credentials=True, origins=allowedOrigins,  resources={r"/*": {"origins": allowedOrigins}})
bcrypt = Bcrypt(app)

db.init_app(app)
with app.app_context():
    db.create_all()

    if len(User.query.all()) == 0:
        username, password = initialize_database()
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, roles="admin")
        db.session.add(new_user)
        db.session.commit()


top_n = 500


guard = flask_praetorian.Praetorian()
cors = CORS()

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User) # Initializes CORS

cached_tweets_folder = '../cached_tweets/'

if os.path.exists(cached_tweets_folder) == False:
    os.mkdir(cached_tweets_folder)

logger.info(f"System is ready!")
# ================== AUTHENTICATION FUNCTIONS ==================

@app.route("/api/register_user", methods=["POST"])
@flask_praetorian.auth_required
def register_user():
    """API endpoint to register a new user.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    logger.info(f"Register user called!")
    try:
        if 'admin' in flask_praetorian.current_user().roles:
            req = request.get_json(force=True)
            username = request.json['username']
            password = request.json['password']

            hashed_password = bcrypt.generate_password_hash(password)
            user_exists = User.query.filter_by(username=username).first() is not None

            if user_exists:
                return jsonify({"error": "User already exists"}), 409

            new_user = User(username=username, password=hashed_password, roles="user")
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                "id": new_user.id,
                "username": new_user.username
            }), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"error": "An error occurred"}), 500
    return jsonify({"error": "Unauthorized!"}), 401


@app.route("/api/delete_user", methods=["POST"])
@flask_praetorian.auth_required
def delete_user():
    """API endpoint to delete a user.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    try:
        logger.info(f"Deleting users called!")
        if 'admin' in flask_praetorian.current_user().roles:
            user_exists = None
            req = request.get_json(force=True)
            userIds = req.get('users', None)
            for userId in userIds:
                user_exists = User.query.filter_by(id=userId).first() is not None
                db.session.delete(User.query.filter_by(id=userId).first())
                db.session.commit()

            users = [{"id": user_item.id, "username": user_item.username, "roles": user_item.roles} for user_item in User.query.all()]
            response = {"users": users}

            if user_exists:
                return jsonify(response), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
    return jsonify({"error": "Unauthorized!"}), 401

@app.route("/api/get_users", methods=["POST"])
@flask_praetorian.auth_required
def get_users():
    """API endpoint to get the users.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    
    logger.info(f"Getting users called!")
    if 'admin' in flask_praetorian.current_user().roles:
        if User.query.all() is not None:
            response = {"users": [{"id": user_item.id, "username": user_item.username, "roles": user_item.roles} for user_item in User.query.all() if "admin" not in user_item.roles]}
            return jsonify(response), 200
        return jsonify({"users": [{}]}), 200
    return jsonify({"error": "Unauthorized!"}), 401

processing_requests_path = 'processing_requests.json'

def add_request(dataSource, dataSourceText, rePreProcessData, reProcessTopics,reProcessSNA):
    requestDate = f'{dt.datetime.now().strftime("%m%d%H%M%S")}'
    if dataSource in ApplicationConfig.SOLR_CORES:
        try:
            objects = dict()
            try:
                with open(processing_requests_path,'r',encoding='utf-8') as fin:
                    objects = json.load(fin)
            except Exception as exp1:
                print_this(f"ERR::at loading JSON::{exp1}")
            if type(objects) == dict:
                objects[dataSource] = {'rePreProcessData': requestDate if rePreProcessData else objects[dataSource].get('rePreProcessData','') if dataSource in objects else '',
                                       'reProcessTopics': reProcessTopics,
                                       'reProcessSNA': reProcessSNA}
                with open(processing_requests_path,'w',encoding='utf-8') as fout:
                    json.dump(objects, fout, indent=4,ensure_ascii=False)
            return re.sub('[ ]+', ' ', f"{'Requesting' if rePreProcessData or reProcessTopics or reProcessSNA else 'Removing all '}\
                {' re-process all data' if rePreProcessData else ''}\
                {' and ' if (rePreProcessData and reProcessTopics) and not reProcessSNA else ', ' if rePreProcessData and reProcessTopics else ''}\
                {' re-process Topics' if reProcessTopics else ''}\
                {' and ' if (rePreProcessData or reProcessTopics) and reProcessSNA else ''}\
                {' re-process SNA' if reProcessSNA else ''} for core {dataSourceText} recorded.").replace(' ,', ',')
        except Exception as exp:
            print_this(f"ERR::{exp}")
    else:
        return f"Error : Updating the requests failed!, {dataSourceText} not found in the system!"
    return f"Error : Data not recorded."

@app.route("/api/re_process_data", methods=["POST"])
@flask_praetorian.auth_required
def re_process_data():
    """API endpoint to request preprocessings for a core.

    Query fields

        :dataSource: (str) the Solr core that holds the data to be requested.
        :rePreProcessData: (boolean) flag to request pre processing all data (currently sentiment and location).
        :reProcessTopics: (boolean) flag to request pre processing topic analysis for the data.
        :reProcessSNA: (boolean) flag to request processing the Social Network Analysis for the data.

    Response
        :bool: a dictionary containing the status of recording the preprocessing request.
    """
    logger.info(f"Re-Processing the data called!")
    try:
        if 'admin' in flask_praetorian.current_user().roles:
            req = request.get_json(force=True)
            dataSource = request.json['dataSource']
            dataSourceText = request.json['dataSourceText']
            rePreProcessData = request.json['rePreProcessData']
            reProcessTopics = request.json['reProcessTopics']
            reProcessSNA = request.json['reProcessSNA']

            print_this(f"Processing {dataSource} with rePreProcessData: {rePreProcessData}, reProcessTopics: {reProcessTopics}, and reProcessSNA: {reProcessSNA}.")

            result = add_request(dataSource, dataSourceText, rePreProcessData, reProcessTopics,reProcessSNA)

            return jsonify({
                "result": result,
            }), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"error": "An error occurred"}), 500
    return jsonify({"error": "Unauthorized!"}), 401


@app.route("/api/delete_report", methods=["POST"])
@flask_praetorian.auth_required
def delete_report():
    """API endpoint to delete a user.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    logger.info(f"Deleting report called!")
    try:
        req = request.get_json(force=True)
        if flask_praetorian.current_user().is_valid:
            report_ids = req.get('reports', None)
            report_exists = False
            for report_id in report_ids:
                logger.info(f"Deleting report: {report_id}")
                report_exists |= Search.query.filter_by(id=report_id).first() is not None
                if report_exists:
                    reportPath = Search.query.filter_by(id=report_id).first().dataPath
                    print_this(f"Deleting report: {reportPath}")
                    if reportPath and os.path.exists(reportPath):
                        os.remove(reportPath)
                    db.session.delete(Search.query.filter_by(id=report_id).first())
                    db.session.commit()

            reports = [{"id": report.id, "reportName": report.reportName, "user_id": report.user_id, "creationTime": report.creationTime} for report in Search.query.all()]
            response = {"reports": reports}

            if report_exists:
                return jsonify(response), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
    return jsonify({"error": "Unauthorized!"}), 401

def saveReportToFile(userFolder, dataPath, dataPackage):
    """Function that saves the report in the user's personal folder.

    Args:
        :userFolder: (str) Path to user's personal folder.
        :dataPath: (str) Name under which report needs to be saved.
        :dataPackage: (dict) Dictionary containing report data and visualisations.

    Returns:
        :str: Full path under which the report has been saved.
    """
    try:
        if dataPackage != None:
            if not os.path.exists(userFolder):
                os.makedirs(userFolder)
            filePath = os.path.join(userFolder, f"{dataPath}.json.gz")
            with gzip.open(filePath, 'wt', encoding='utf-8') as fout:
                json.dump(dataPackage, fout, ensure_ascii=False)
            return filePath
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return ''
    
@app.route("/api/save_report", methods=["POST"])
@flask_praetorian.auth_required
def save_report():
    """API endpoint to save a report.

    Query fields
        :data: (str)

    Response
        a message to show the outcomes.
    """
    logger.info("saveReport called!")
    try:
        req = request.get_json(force=True)
        if flask_praetorian.current_user().is_valid:
            data = req.get('data', None)
            token= data.get('token','')
            reportName= data.get('name','')
            dataPackage= data.get('data','')
            
            tempReportName = reportName

            previous_search = Search.query.filter_by(user_id=flask_praetorian.current_user().id, reportName= tempReportName)
            i = 1

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            while len(previous_search.all()) > 0:
                tempReportName = f"{reportName}({i})"
                previous_search = Search.query.filter_by(user_id=flask_praetorian.current_user().id, reportName= tempReportName)
                logger.info(f"search item found, data will be updated from {reportName} to {tempReportName}")
                i += 1
                
            savedPath = saveReportToFile(userFolder=f"{reportFolder}/{flask_praetorian.current_user().username}", dataPath=tempReportName, dataPackage=dataPackage)
            new_search = Search(user_id=flask_praetorian.current_user().id, token=token, reportName=tempReportName, dataPath=savedPath, creationTime= timestamp)
            db.session.add(new_search)
            db.session.commit()

            resp = {"Message": f"Report saved with name {tempReportName}."}
            return jsonify(resp), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401


@app.route("/api/login", methods=["POST"])
def login():
    """API endpoint that enables the user to log into their personal session (e.g. to save and load reports).

    Query fields:
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response:
        :tuple: Contains a dictionary with a status message (under “error” field) and an error code.
    """
    try:
        req = request.get_json(force=True)
        username = req.get('username', None)
        password = req.get('password', None)
        user = guard.authenticate(username, password)
        ret = {'accessToken': guard.encode_jwt_token(user), 'userName': user.username, 'userType': user.roles}
        return ret, 200
    except Exception as exp:
        logger.warning(f"exception: {exp}")
        resp = jsonify({"error": "Unauthorized" + str(exp), "accessToken": ""})
        return resp, 401

@app.route("/api/refresh", methods=['POST'])
def refresh():
    """
    Refreshes an existing the accessToken JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    """
    logger.info("refresh request")
    old_token = request.get_json(force=True)
    new_token = old_token.copy()
    new_token['accessToken'] = guard.refresh_jwt_token(old_token['accessToken'])
    return new_token, 200


def readReportFromFile(dataPath):
    """Function that reads a saved report from a file.

    Args:
        :dataPath: (str)  Full path under which the report is saved.

    Returns:
        :dict: Dictionary containing report data and visualisations.
    """
    try:
        with gzip.open(dataPath, 'rt', encoding='utf-8') as fin:
            dataPackage = json.load(fin)
            return dataPackage
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return {}
    
@app.route("/api/load_report", methods=["POST"])
@flask_praetorian.auth_required
def update_reports():
    """API endpoint that enables access to the "Analysis" page in the dashboard from cached credentials

    Response:
        :dict: Contains the single field "error" with the error message.
        :int: Error code.
    """
    resp = None
    if flask_praetorian.current_user().is_valid:
        try:
            if 'admin' in flask_praetorian.current_user().roles:
                items = Search.query.all()
            elif 'user' in flask_praetorian.current_user().roles:
                items = Search.query.filter_by(user_id=flask_praetorian.current_user().id)
            else:
                items = []
            resp = [{"id": item.id, "username": item.user.username, "reportName": item.reportName ,"token": item.token, "creationTime": item.creationTime} for item in items]
            return jsonify({'data': resp}), 200
        except Exception as exp:
            logger.warning(f"Error {exp}")
            resp = None
    logger.warning("At load page, It went wrong! !")
    return jsonify({"error": "Unauthorized!"}), 401

# ================== MAIN REPORT FUNCTIONS ==================


languages_file_path = os.path.join(CURRENT_PATH, '.data/languages.csv')
countries_file_path = os.path.join(CURRENT_PATH, '.data/countries_codes_english.csv')

languages = list(pd.read_csv(languages_file_path, delimiter=";")['language'])
countries = list(pd.read_csv(countries_file_path)['name'])

@app.route("/api/get_countries_list", methods=["GET"])
@flask_praetorian.auth_required
def get_countries_list():
    """API endpoint that returns the list of valid countries (stored on file) for location graph.

    Response:
        :dict: Jsonified CSV file with list of countries with their codes.
    """
    try:
        resp = make_response(jsonify(countries))
        return resp, 200
    except Exception as exp:
        logger.warning(f"Error getting countries list! {exp}")
    return make_response(jsonify({"error": "Error getting countries list!"})), 401


@app.route("/api/get_languages_list", methods=["GET"])
@flask_praetorian.auth_required
def get_languages_list():
    """API endpoint that returns the list of valid languages (stored on file) for language graph.

    Response:
        :dict: Jsonified list of languages.
    """
    try:
        resp = make_response(jsonify(languages))
        return resp, 200
    except Exception as exp:
        logger.warning(f"Error getting languages list! {exp}")
    return make_response(jsonify({"error": "Error getting languages list!"})), 401


@app.route("/api/search", methods=["POST"])
@flask_praetorian.auth_required
def search():
    """API endpoint that returns the relevant data from Solr for the main report.

    Query fields:
        :source: (str) Dataset to query from in Solr.
        :date_start: (str) Start of the date range (format YYYY-MM-DD, by default "").
        :date_end: (str) End of the date range (format YYYY-MM-DD, by default "").
        :keywords: (str) Comma-separated list of keywords to match in text (e.g. "keyword1, keyword2", by default "").
        :operator: (str) Determines whether to retrieve data that matches all keywords ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :nb_topics: (int) Number of cluster to group data into in Topic Discovery module.
        :claim: (str) Claim to be projected into the data in Topic Discovery module.
        :random_seed: (int) Random seed to make random selection of data in Topic Discovery Module (i.e. when volume is \
            greater than 100K) deterministic.
        :language: (str) Language of data, by default "All".
        :sentiment: (str) Sentiment of data (choice between "All", "Positive", "Neutral", "Negative"). By default "All"
        :location: (str) Country of data, by default "All".
        :location_type: (str) Whether country corresponds to "author" or "tweet". By default "author"

    Response:
        :hits: (int) Total volume of tweets that matched the query.
        :show_report: (bool) Whether the query was successful (i.e. results were found), defines if report should be \
          shown in front-end.
        :dataSource: (str) Dataset queried from in Solr.
        :source_text: (str) Display name of dataset queried from in Solr.
        :operator: (str) Determines whether data retrieved matched all keywords at once ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :report: (dict) The report contains a different entry for each keyword from the query. This entry is itself a \
            dictionary with the following fields:

            * count: (int) Number of datapoints that match this keyword
            * mentions: (dict[list]) Number of mentions per user, faceted by sentiment (i.e. of the text)
            * retweeted: (dict[list]) Number of retweets by user, faceted by sentiment (i.e. of the text)
            * retweeters: (dict[list]) Number of retweets per user, faceted by sentiment (i.e. of the text)
            * Languages_Distributions: (list[dict]) Number of tweets per language. Each dictionary contains a "Count" \
              and "Language" field
            * tweets_languages_by_sentiments: (dict[list]) Number of tweets per day, faceted by sentiment and language
            * Sentiment_per_language: (dict[list]) Number of tweets per language, faceted by sentiment
            * Sentiments_Distributions: (dict[list]) Number of tweets per day, faceted by sentiment
            * emojis: (dict[list]) Count per emoji, faceted by sentiment
            * media: (dict[list]) Count per media URL, faceted by sentiment
            * top_tweets: (dict[list]) Top 10K most retweeted tweets in dataset per sentiment, with id, date of \
              publication, text, language, location and retweet count
            * top_users: (dict[list]) Top 10K most retweeted users in dataset per sentiment, with user ID, screenname, \
              description, language, location and retweet count
            * urls: (dict[list]) Count per URL, faceted by sentiment
            * userScreenName: (dict[list]) Count per user screenname, faceted by sentiment
            * hashtags: (dict[list]) Count per hashtag, faceted by sentiment
            * processedDescTokens: (dict[list]) Count per word from user descriptions, faceted by sentiment
            * processedTokens: (dict[list]) Count per word from text, faceted by sentiment
            * traffic: (list[dict]) Number of tweets per day. Each dictionary contains a "Count" and "Date" field
            * users_locations_by_languages: (dict[list]) Number of users per region, faceted by language
            * users_locations_by_sentiments: (dict[list]) Number of users per region, faceted by sentiment
            * tweets_locations_by_sentiments: (dict[list]) Number of tweets per region, faceted by sentiment
            * tweets_locations_by_languages: (dict[list]) Number of tweets per region, faceted by language
    """
    logger.info("Search API called!")
    if flask_praetorian.current_user().is_valid:
        try:
            req = request.get_json(force=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            logger.info(req)
            
            savedReport = req['data']['savedReport'] if 'data' in req.keys() and 'savedReport' in req['data'].keys() else False
            reportName = req['data']['reportName'] if 'data' in req.keys() and 'reportName' in req['data'].keys() else ''
            
            if savedReport and reportName != '':
                record = db.session.query(Search.dataPath, Search.creationTime).filter(
                    Search.user_id == flask_praetorian.current_user().id,
                    Search.reportName == reportName).all()
                print_this(f"record: {record}")
                dataPackage = readReportFromFile(record[0][0])
                reportDate = record[0][1]
                print_this(f"dataPackage: {dataPackage.keys()}")
                print_this(f"dataPackage: {dataPackage['inputInfo'].keys()} and reportDate: {reportDate}.")
                if dataPackage:
                    resp = {'reportDate' : reportDate, 'report':dataPackage,'hits':dataPackage['count'], 'keywords': dataPackage['inputInfo']['keywords'], 'show_report':True, 'dataSource':dataPackage['inputInfo']['dataSource'], 'operator':dataPackage['inputInfo']['operator'], 'source_text':dataPackage['inputInfo']['source_text']}
                    return jsonify({'data': resp}), 200
            
            source, keywords_list, filters, operator, limit = get_request_components(req['data'])
            source_text = req['data']['source_text'] if 'source_text' in req['data'].keys() else ''
            count = int(req['data']['count']) if 'count' in req['data'].keys() else 500
            num_of_rows = req['data']['num_of_rows'] if 'num_of_rows' in req['data'].keys() else 'use_all'

            if source==None:
                resp = make_response(jsonify({"Error": "No data source specified, or wrong data source provided!"}))
                return resp, 400

            dataSource = SolrClass(filters=filters)
            start = datetime.now()
            report,hits, datasetOrigin, error_message = dataSource.optimised_json_query_handler(solr_core=source, keywords=keywords_list, operator=operator, limit=limit, top_n=count)
            end = datetime.now()
            keywords = [x for x in report.keys() if x != "All"]
            for k in list(report.keys()):
                if report[k]['count'] == 0:
                    report.pop(k)
            logger.info(f"Time taken to get data from Solr: {end-start}")
            logger.info(f'Hits are : {hits}')
            resp = {'datasetOrigin': datasetOrigin, 'report':report,'hits':hits, 'keywords': keywords, 'show_report':True, 'dataSource':source, 'operator':operator, 'source_text':source_text}
            return jsonify({'data': resp, 'error': error_message}), 200
        except Exception as exp:
            logger.warning(f"Search {exp}")
            logger.warning(traceback.format_exc())
            resp = jsonify({"Message": "Something went wrong!"}), 405
            return resp, 401
    return jsonify({"Message": "Unauthorized!"}), 401

def get_existing_communities(user_id, interaction):
    """Function that retrieves community names (as saved by the user) from the database.

    Args:
        :user_id: (str)  identifier of user for whom community names need to be retrieved.
        :interaction: (str)  Network type for which the community names need to be retrieved. Must be one of "retweet" \
            or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)

    Returns:
        :dict: Dictionary containing mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end)
    """
    # Retrieve current step records for this user, interaction type, and step
    communities = dict()
    records = SNAUsersCommunitiesMap.query.filter(
        SNAUsersCommunitiesMap.user_id == user_id,
        SNAUsersCommunitiesMap.snaCommunityType == interaction
        ).all()
    for record in records:
        communities[record.snaCommunityKey] = record.snaCommunityValue
    return communities

def reset_communities_names(user_id, interaction):
    """Function that deletes community names saved by the user from the database.

    Args:
        :user_id: (str)  identifier of user for whom community names need to be deleted.
        :interaction: (str)  Network type for which the community names need to be deleted. Must be one of "retweet" \
            or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
    """
    # Retrieve records for the specified user and interaction
    records = SNAUsersCommunitiesMap.query.filter(
        SNAUsersCommunitiesMap.user_id == user_id,
        SNAUsersCommunitiesMap.snaCommunityType == interaction
    ).all()

    # Iterate over the records and update the snaCommunityValue to None
    for record in records:
        db.session.delete(record)

    # Commit the changes to the database
    db.session.commit()

def update_db(user_id, interaction, community_names, current_communities):
    """Function that saved community names as saved by the user into the database.

    Args:
        :user_id: (str)  identifier of user for whom community names need to be saved.
        :interaction: (str)  Network type for which the community names need to be saved. Must be one of "retweet" \
            or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
        :community_names: (dict) New mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end)
        :current_communities: (dict) Previous mapping between community numbers (as stored in Solr) and community \
            names (as saved by user in the front-end)
    """
    changed = False
    for k, v in community_names.items():
        if str(k) != str(v):
            if current_communities.get(k, None) != v:
                new_entry = SNAUsersCommunitiesMap(
                    user_id=user_id,
                    snaCommunityType=interaction,
                    snaCommunityKey=k,
                    snaCommunityValue=v
                )
                db.session.merge(new_entry)
                changed = True
        else:
            SNAUsersCommunitiesMap.query.filter_by(
                user_id=user_id,
                snaCommunityType=interaction,
                snaCommunityKey=k
            ).delete()
            changed = True
    if changed:
        db.session.commit()

@app.route("/api/social_network_analysis", methods=["POST"])
@flask_praetorian.auth_required
def social_network_analysis():
    """API endpoint to generate results for social network analysis.

    Query fields under "data" field:
        :keywords: (list[str]) Keywords as list
        :date_start: (str) Start date as YYYY-MM-DD (None if no start date is used)
        :date_end: (str) End date as YYYY-MM-DD (None if no end date is used)
        :limit: (int) Maximum number of results returned
        :source: (str) Name of Solr core to get data from
        :operator: (str) Whether keywords should appear in the same tweets ("AND") or not necessarily ("OR")
        :random_seed: (float) Random seed to make random parts of function deterministic
        :language: (str) Language to filter data by
        :sentiment: (str) Sentiment to filter data by
        :location: (str) Country to filter data by
        :location_type: (str) Whether the country used is that of the user or the tweet
        :nb_communities": (int) How many of the top communities to highlight on the visualisation
        :interaction: (str)  Network type for which the SNA visualisation needs to be generated. Must be one of
        "retweet" or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
        :community_names: (dict) Mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end)
        :datasetOrigin: (str) Indicates whether the dataset contains data from Twitter ("Tweets") or from YouTube ("Comment")
        :reset: (bool) Whether to delete existing mapping between community numbers (as stored in Solr) and community \
            names (as saved by user in the front-end)

    Response
        :dict or tuple: If user is correctly authenticated, returns a dictionary with the field "sna_figure" (which \
            contains the Bokeh plots for the social network analysis), "network_stats" (the values to populate the \
            "Communities Stats" component in the front-end) and "communities_traffic" (the values to populate the \
            "Communities tweeting" component in the front-end)

    """
    logger.info("SNA called!")
    try:
        if flask_praetorian.current_user().is_valid:
            # Get API request header
            req = request.get_json(force=True)
            req = req.get('data', None)

            max_label = req["nb_communities"]
            interaction = req['interaction'] if 'interaction' in req.keys() else 'retweet'
            community_names = req["community_names"] if 'community_names' in req.keys() else None
            dataset_origin = req["datasetOrigin"]
            reset = req["reset"] if "reset" in req else False

            #Getting user information from the session:
            user_id = flask_praetorian.current_user().id
            
            if reset:
                reset_communities_names(user_id, interaction)
                community_names = None
            #Getting current communities from the db:
            current_communities = get_existing_communities(user_id, interaction)

            #Getting SNA data:
            responses = get_sna_data(req, interaction)

            if responses!= None and len(responses) > 0:

                keywords = list(responses.keys())
                mapping = {
                        'All sentiments': 'All Sentiments',
                        'Positive': 'Positive',
                        'Negative': 'Negative',
                        'Neutral': 'Neutral'}
                plots_list = dict()
                colors_list = dict()
                top_words_list = dict()
                network_stats_all = dict()
                communities_traffic = dict()
                community_names_dict = dict()
                maps_list = dict()
                for keyword in keywords:
                    logger.info(f"==> {keyword} ==>")
                    resp = responses[keyword]

                    df_sub = resp['network_df']
                    nodes_all = resp['nodes_df']
                    
                    if nodes_all is not None and len(nodes_all) > 0:
                        nodes_all["community"] = nodes_all["community"].apply(str)
                        labels_all = nodes_all['community'].value_counts().index.to_list()

                        if community_names and type(community_names)==dict:
                            #We got a new community_name, add it to the db.
                            update_db(user_id, interaction, community_names, current_communities)

                        try:
                            #Getting existing communities from the db:
                            communities_naming = get_existing_communities(user_id, interaction)
                            nodes_all["community"] = nodes_all["community"].apply(lambda x: communities_naming[x] if x in communities_naming else x)
                            nodes_all = nodes_all.drop_duplicates(subset=['node'])
                            logger.info(f"NB NODES BEFORE FILTERING OUT 0: {len(nodes_all)}")
                            nodes_all = nodes_all[nodes_all["community"] != 0]
                            logger.info(f"NB NODES AFTER FILTERING OUT 0: {len(nodes_all)}")
                            network_stats_all[keyword] = resp['network_stats']['sentiments']

                            #comm_to_rank = {communities_naming[l] if l in communities_naming else l: idx for idx,l in enumerate(labels_all) if idx < max_label}
                            comm_to_rank = {l: idx for idx,l in enumerate(labels_all) if idx < max_label}
                            nb_labels = min(len(labels_all),max_label)
                            cmap = get_cmap('viridis')

                            labels = [l for l in labels_all[0:nb_labels]]
                            logger.info(f"labels: {labels}")
                            community_names = {l: communities_naming[l] if l in communities_naming else l for l in labels}
                            logger.info(f"community_names: {community_names}")
                            #logger.info(f"community_names2 : {community_names}")
                            communities_traffic[keyword] = {community_names[k]: resp['network_stats']['communities_traffic'][int(k)] for k in community_names if int(k) in resp['network_stats']['communities_traffic']}

                            community_names_dict[keyword] = community_names.copy()
                            for k in list(communities_traffic[keyword]):
                                if k in community_names:
                                    communities_traffic[keyword][community_names[k]] = communities_traffic[keyword].pop(k)

                            category_color_mapping = {x: get_color(comm_to_rank[x], cmap, max_label) if x in comm_to_rank else get_color(-1, cmap, max_label) for x in labels_all}
                            category_color_mapping = {communities_naming[k] if k in communities_naming else k: v for k,v in category_color_mapping.items()}
                            nodes_all['color'] = nodes_all['community'].apply(lambda x: category_color_mapping[x])
                            colors_list[keyword] = {str(c): category_color_mapping[c] for c in category_color_mapping}

                            if df_sub is not None and len(df_sub) > 0:
                                if len(df_sub) > 0 and len(nodes_all) > 0:
                                    if len(nodes_all) > 0:
                                        nodes = nodes_all
                                        logger.info(f"\tAfter filter 1: {len(nodes)}")
                                        nodes = nodes[nodes['x']!=""]
                                        logger.info(f"\tAfter filter 2: {len(nodes)}")
                                        bokeh_cmap = CategoricalColorMapper(factors=[community_names[l] if l in community_names else str(l) for l in labels], palette=[get_color(comm_to_rank[l if l in community_names else l], cmap, max_label) for l in labels])
                                        bokeh_cmap_cop = copy.deepcopy(bokeh_cmap)
                                        plot = json.dumps(json_item(get_network_plot(nodes, bokeh_cmap_cop, datasetOrigin=dataset_origin)))
                                        top_words = get_tf_idf(nodes, "desc", "community", labels_list=list(community_names_dict[keyword].values()))
                                    else:
                                        plot = None
                                    plots_list[keyword] = plot
                                    top_words_list[keyword] = top_words
                                else:
                                    plots_list[keyword] = None
                                    top_words_list[keyword] = []
                        except Exception as exp:
                            logger.warning(f"ERROR :: {exp}")
                            plots_list[keyword] = None
                            top_words_list[keyword] = []
                            community_names = {}
                            
                    else:
                        plots_list[keyword] = None
                        top_words_list[keyword] = []
                        community_names = {}

                com_loc_lang_responses = get_communities_location_and_language(req, interaction, community_names_dict)

                if com_loc_lang_responses!= None and len(com_loc_lang_responses) > 0:
                    keywords = list(com_loc_lang_responses.keys())
                    for keyword in keywords:
                        maps_list[keyword] = com_loc_lang_responses[keyword]


                return jsonify({'data':{
                    "sna_figure": plots_list,
                    "network_stats": network_stats_all,
                    "communities_traffic": communities_traffic,
                    "communities_colors": colors_list,
                    "top_words": top_words_list,
                    "communities_map": maps_list,
                    "community_names": community_names_dict,
                    }})
            return jsonify({'data':{"sna_figure": "", "network_stats": [], "communities_traffic": []}})
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"Message": "Unauthorized!"}), 401

@app.route("/api/topic_modelling", methods=["POST"])
@flask_praetorian.auth_required
def topic_modelling():
    """API endpoint that returns relevant information for the Topic Discovery scatter plots and topic wordclouds.

    Query fields under "data" field:
        :source: (str) Dataset to query from in Solr.
        :dataSource: (str) Dataset to query from in Solr (i.e. name of Solr core).
        :dataOrigin: (str) Dataset type ("Tweets" for Twitter and "Comment" for YouTube).
        :date_start: (str) Start of the date range (format YYYY-MM-DD, by default "").
        :date_end: (str) End of the date range (format YYYY-MM-DD, by default "").
        :keywords: (list[str]) List of keywords to match in text.
        :operator: (str) Determines whether to retrieve data that matches all keywords ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :nb_topics: (int) Number of cluster to group data into.
        :claim: (str) Claim to be projected into the same multi-dimensional space as the data.
        :random_seed: (int) Random seed to make random selection of data (i.e. when volume is greater than 100K) \
            deterministic.
        :language: (str) Language to filter data by.
        :sentiment: (str) Sentiment to filter data by.
        :communities_list: (dict) Mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end). If this field is different from None, for each community in \
            communities_list a filtered version of the Topic Discovery visualisation containing only posts from that \
            community is generated.
        :interactionCommunity: (str) Network type for which the community names (from communities_list) are for. Must \
            be one of "retweet" or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
        :focusOnMainCommunities: (bool) Whether to only sample data posted by the communities in communities_list when \
            generating the Topic Discovery visualisation

    Output:
        :figures: (dict[dict[bokeh.plotting.figure]]) Bokeh figures per keyword (outter dict) and sentiment \
            (inner dict).
        :top_words: (dict[dict[list]]) Words with the greatest TF-IDF per keyword (outter dict) and sentiment (inner \
            dict). Each element in the inner dict is a list of dictionaries, with a "text" (str, the word) and "value" \
            (float, TF-IDF value) field.
        :topic_names: (dict) List of topic numbers as automatically generated from the K-means clustering algorithm as
            mapping to themselves. This data structure is then modified in the front-end when the user renames the topics.
        :topics_per_community: (dict) For each community in communities_list, this dictionary contains a filtered version of the Topic \
            Discovery visualisation containing only posts from that community.
    """
    logger.info("Topic Modelling endpoint called!")
    try:
        if flask_praetorian.current_user().is_valid:
            # Get API request header
            req = request.get_json(force=True)
            req = req.get('data', None)
            communitiesList = req["communities_list"] if "communities_list" in req else None
            interactionCommunity = req["interactionCommunity"] if "interactionCommunity" in req else False
            focusOnMainCommunities = req["focusOnMainCommunities"] if "focusOnMainCommunities" in req else None
            datasetOrigin = req["datasetOrigin"] if "datasetOrigin" in req else None
            core_ = req['dataSource']
            logger.info(f"THIS IS THE COMMUNITIES: {communitiesList}\nand COMMUNITY INTERACTION: {interactionCommunity}")
            start = time.time()

            rel_sentiments = ['All sentiments', 'Positive', 'Negative', 'Neutral'] if req["sentiment"] == "All" else [req["sentiment"]]

            # Get relevant data from Solr for the current request
            if focusOnMainCommunities:
                print("FOCUSING ON MAIN COMMUNITIES")
                print("This is the communitiesList object", communitiesList)
                responses = get_topic_data(req, interactionCommunity, communitiesList)
            else:
                print("NOT FOCUSING ON MAIN COMMUNITIES")
                responses = get_topic_data(req, interactionCommunity)
            keywords = list(responses.keys())

            # Generate empty object in which results will be stored
            plots_list = dict() # Info for Bokeh plots
            topics_per_com_plots = None if communitiesList is None else {k: dict() for k in keywords} # Topics per community graphs
            top_words = None if req["nb_topics"] == 0 else {k: dict() for k in keywords} # Info for topic wordclouds
            # Get the data that corresponds to the "All" keyword
            if len(keywords) > 1:
                df_ALL = pd.concat([pd.DataFrame(responses[k]) for k in keywords if k != "All"]).drop_duplicates(["fullText"])
                df_ALL = preprocess_data(df_ALL)
            else:
                df_ALL = pd.DataFrame(responses[keywords[0]])
                df_ALL = preprocess_data(df_ALL)

            print("TOTAL NB TWEETS FOUND", len(df_ALL))

            #logger.info(f"COLUMNS IN TM DATA (1): {df_ALL.columns}")

            # If the dataframe with the data does not contain the field "fullText", return an empty results dictionary.
            if not 'fullText' in df_ALL.columns:
                return jsonify({'data': {"figures": "", "top_words": []}}), 200

            # Generate the "Topic" field in the dataframe for the data corresponding to the keyword "All"
            if req["nb_topics"] == 0:
                # If the number of topics specified is 0, all topics are None
                df_ALL['Topic'] = [None] * len(df_ALL)
            else:
                # Otherwise, tweets are labelled with topic numbers by applying the K-means algorithm to the tweets'
                # 5d embeddings
                umap_embeddings = df_ALL["embedding_5d"].to_list()
                model = KMeans(n_clusters=min(req["nb_topics"], len(df_ALL)) if req["nb_topics"] != None else 1)
                model.fit(umap_embeddings)
                yhat = model.predict(umap_embeddings)
                df_ALL['Topic'] = yhat

                # Change topic order
                df_ALL = change_topic_order(df_ALL)

            # Set the "Size" of all tweets in the scatter plot to be equal to 4
            df_ALL["size"] = [4] * len(df_ALL)

            # Generate the "color" field in the dataframe for the data corresponding to the keyword "All"
            if req["nb_topics"] == 0:
                # If the number of topics specified is 0, all the tweets in the scatter plot are colored in grey
                df_ALL["color"] = ['#BDBDBD'] * len(df_ALL)
                bokeh_cmap = None
                topic_names = {}
            else:
                # Otherwise, the color is obtained from the topic number using the "get_color" function
                labels = sorted(list(set(df_ALL["Topic"].to_list())))
                topic_names = {l: l for l in labels}
                max_label = max(labels) + 1
                cmap = get_cmap('jet')
                bokeh_cmap = CategoricalColorMapper(factors=[str(l) for l in labels], palette=[get_color(l, cmap, max_label) for l in labels])
                df_ALL["color"] = df_ALL["Topic"].apply(lambda x: get_color(x, cmap, max_label))
                df_ALL['Topic'] = df_ALL['Topic'].apply(lambda x: str(int(x)))

            # The following code is concerned with adding a custom claim (from the "claim" argument from query header) onto the
            # Topic Discovery scatter plot
            new_row = None
            if req["claim"].strip() != "":

                # Use the SBERT classifier, the parametric UMAP embedder to reduce 768 dimensional embeddings to 5 dimensions
                # and that to reduce 5 dimensional embeddings to 2 dimensions
                global CLASSIFIER
                global EMBEDDERS_5D
                global EMBEDDERS_2D

                # Obtain different encodings for the "claim" query argument
                encoding = CLASSIFIER.encode(req["claim"])
                if ApplicationConfig.LIMITED_RESOURCE:
                    encoding = CLASSIFIER.encode(req["claim"], batch_size=ApplicationConfig.BATCH_SIZE)
                
                encoding_5d = EMBEDDERS_5D[core_].transform([encoding])[0]
                encoding_2d = EMBEDDERS_2D[core_].transform([encoding_5d])[0]

                # Create new row to append to dataframe
                new_row = {"display_text": req["claim"], "color": "#000000", "x": encoding_2d[0], "y": encoding_2d[1], "size": 12, "Topic": None}

            
            for keyword in keywords:
                plots_list[keyword] = dict()
                if not topics_per_com_plots is None:
                    topics_per_com_plots[keyword] = dict()

                # Get the data that corresponds to the current keyword
                if keyword == "All" or len(keywords) == 1:
                    df_sub = df_ALL
                else:
                    df = pd.DataFrame(responses[keyword])
                    df_sub = preprocess_data(df)
                    # Merge the Topic, color and size fields obtained above from df_ALL with the data for the current keyword
                    # This has been added to solve the empty df_sub DataFrame.
                    if len(df_sub) > 0:
                        if "videoId" in df_ALL.columns and new_row!= None: 
                            new_row["videoId"] = None
                        df_sub = pd.merge(df_sub, df_ALL[["id", "videoId", "Topic", "color", "size"]], on="id", how="inner") if "videoId" in df_ALL.columns else pd.merge(df_sub, df_ALL[["id", "Topic", "color", "size"]], on="id", how="inner")
                    else:
                        df_sub = df_ALL[["id", "videoId", "sentiment","Topic", "color", "size"]].sample(0) if "videoId" in df_ALL.columns else df_ALL[["id", "sentiment","Topic", "color", "size"]].sample(0)
                mapping = {
                        'All sentiments': 'All Sentiments',
                        'Positive': 'Positive',
                        'Negative': 'Negative',
                        'Neutral': 'Neutral'
                    }

                # Generate the Topic Discovery scatter plot for each sentiment
                for sentiment in rel_sentiments:

                    plots_list[keyword][mapping[sentiment]] = dict()

                    if sentiment == 'All sentiments':
                        df_rel = df_sub
                    else:
                        df_rel = df_sub[df_sub["sentiment"] == sentiment]

                    #logger.info(f"Nb tweets: {keyword} - {sentiment}: {len(df_rel)}")

                    # Add the datapoint for the "claim" query argument onto the scatter plot
                    if not new_row is None:
                        df_rel = pd.concat([df_rel, pd.DataFrame([new_row])])

                    # If tweets are labelled with topics, generate the TF-IDF info for each topic (for topic wordclouds)
                    if req["nb_topics"] and req["nb_topics"] > 0:
                        top_words[keyword][mapping[sentiment]] = get_tf_idf(df_rel, "processed_text", "Topic")

                    # Append scatter plot to empty results object
                    if len(df_rel) == 0:
                        plot = None
                    else:
                        bokeh_cmap_cop = copy.deepcopy(bokeh_cmap)
                        plot = json_item(get_plot(df_rel, bokeh_cmap=bokeh_cmap_cop, datasetOrigin=datasetOrigin))

                    plots_list[keyword][mapping[sentiment]]["All Communities"] = json.dumps(plot)

                    if communitiesList and keyword in communitiesList:
                        logger.info("--> Generating plot of topics per community")
                        logger.info(f"--> Generating plot of topics per community {communitiesList}")
                        logger.info(f"--> interactionCommunity: {communitiesList[keyword] if keyword in communitiesList else communitiesList}")
                        if len(df_rel) == 0 or len(communitiesList[keyword]) == 0 or keyword not in communitiesList:
                            topics_per_com_plots[keyword][mapping[sentiment]] = None
                        else:
                            logger.info(f"--> interactionCommunity: {communitiesList[keyword] if keyword in communitiesList else communitiesList}")
                            topics_per_com_plots[keyword][mapping[sentiment]] = get_topics_per_communities_plot(df_rel, communitiesList[keyword], interactionCommunity)
                        logger.info("--> Generating plot per community")

                        if keyword in communitiesList and plot is not None:
                            doc = Document.from_json(plot["doc"])
                            new_plot=doc.roots[0]
                            datasource = new_plot.select(dict(type=ColumnDataSource))[0]
                            df_rel = pd.DataFrame(datasource.data.copy())
                            plots_list[keyword][mapping[sentiment]] = filter_topic_modelling_per_community(communitiesList[keyword], interactionCommunity, new_plot, datasource, df_rel)
                        else:
                            plots_list[keyword][mapping[sentiment]] = []
                            #plots_list[keyword][mapping[sentiment]][community] = []
                    elif focusOnMainCommunities:
                        plots_list[keyword][mapping[sentiment]] = []


                if top_words != None:
                    compute_positive_negative(top_words, keyword)

            end = time.time()
            logger.info(f"\t\t...time = {(end - start):.1f}")

            resp = {"figures": plots_list, "top_words": top_words, "topic_names": topic_names, "topics_per_community": topics_per_com_plots}
            return jsonify({'data':resp}), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"Message": "Unauthorized!"}), 401


@app.route("/api/update_topic_modelling_after_SNA", methods=["POST"])
@flask_praetorian.auth_required
def update_topic_modelling_after_SNA():
    """API endpoint called after the Social Network Analysis when a Topic Discovery visualisation already exists in the \
     report. This endpoint generates filtered versions of the Topic Discovery visualisation for each of the main \
     communities in the SNA.

    Query fields under "data" field:
        :topic_modelling_figures: (dict) Dictionary containing existing Topic Discovery visualisation(s)
        :topic_mapping: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
            algorithm) and topic names (as saved by the user in the front-end)
        :communities_list: (dict) Mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end). If this field is different from None, for each community in \
            communities_list a filtered version of the Topic Discovery visualisation containing only posts from that \
            community is generated.
        :interactionCommunity: (str) Network type for which the community names (from communities_list) are for. Must \
            be one of "retweet" or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)

    Output:
        :figures: (dict[dict[bokeh.plotting.figure]]) Bokeh figures per keyword (outter dict) and sentiment \
            (inner dict).
        :topics_per_community: (dict) Bokeh visualisations for the "Topics per community" visualisation.
    """
    try:
        if flask_praetorian.current_user().is_valid:
            # Get API request header
            req = request.get_json(force=True)
            req = req.get('data', None)
            communitiesList = req["communities_list"] if "communities_list" in req else None
            interactionCommunity = req["interactionCommunity"] if "interactionCommunity" in req else False
            plots_list = req["topic_modelling_figures"]
            topic_mapping = req["topic_mapping"]

            topics_per_com_plots = dict()
            new_plots = dict()

            for keyword in plots_list:
                new_plots[keyword] = dict()
                topics_per_com_plots[keyword] = dict()

                for sentiment in plots_list[keyword]:
                    new_plots[keyword][sentiment] = dict()
                    topics_per_com_plots[keyword][sentiment] = dict()
                    plot = json.loads(plots_list[keyword][sentiment]["All Communities"])

                    if communitiesList and plot:

                        logger.info("--> Generating plot per community")
                        doc = Document.from_json(plot["doc"])
                        new_plot=doc.roots[0]
                        datasource = new_plot.select(dict(type=ColumnDataSource))[0]
                        df_rel = pd.DataFrame(datasource.data.copy())
                        print("THESE ARE THE COLUMNS:", df_rel.columns)

                        if keyword in communitiesList:
                            new_plots[keyword][sentiment] = filter_topic_modelling_per_community(communitiesList[keyword], interactionCommunity, new_plot, datasource, df_rel)
                        else:
                            new_plots[keyword][sentiment] = None

                        logger.info("--> Generating plot of topics per community")
                        logger.info(f"--> interactionCommunity: {communitiesList[keyword]}")
                        if len(df_rel) == 0 or len(communitiesList[keyword]) == 0 or keyword not in communitiesList:
                            topics_per_com_plots[keyword][sentiment] = None
                        else:
                            logger.info(f"--> interactionCommunity: {communitiesList[keyword]}")
                            topics_per_com_plots[keyword][sentiment] = get_topics_per_communities_plot(df_rel, communitiesList[keyword], interactionCommunity, list(topic_mapping.values()))

                    else:
                        new_plots[keyword][sentiment] = []
                        topics_per_com_plots = []

            resp = {"figures": new_plots, "topics_per_community": topics_per_com_plots}
            return jsonify({'data':resp}), 200

    except Exception as exp:
            logger.warning(f"Error: {exp}")
            logger.warning(f"Error: {traceback.format_exc()}")
            return jsonify({"Message": "Unauthorized!"}), 401


@app.route("/api/add_claim_topic_modelling", methods=["POST"])
@flask_praetorian.auth_required
def add_claim_topic_modelling():
    """API endpoint to add the claim typed in by the user into the Topic Discovery visualisation(s).

    Query fields under "data" field:
        :figures: (dict) Dictionary containing existing Topic Discovery visualisation(s)
        :claim: (str) Claim to be projected into the same multi-dimensional space as the data.
        :dataSource: (str) Dataset to query from in Solr (i.e. name of Solr core).

    Output:
        :figures: (dict[dict[bokeh.plotting.figure]]) New Bokeh figures for Topic Discovery per keyword (outter dict) \
            and sentiment (inner dict). These new figures contain the claim added by the user.
    """
    logger.info("Add Claim to Topic Modelling endpoint called!")
    try:
        if flask_praetorian.current_user().is_valid:
            # Get API request header
            req = request.get_json(force=True)
            req = req.get('data', None)
            plots = req['figures']
            claim = req['claim']
            core_ = req['dataSource'] if 'dataSource' in req else None
            
            if claim != "":

                # Use the SBERT classifier, the parametric UMAP embedder to reduce 768 dimensional embeddings to 5 dimensions
                # and that to reduce 5 dimensional embeddings to 2 dimensions
                global CLASSIFIER
                global EMBEDDERS_5D
                global EMBEDDERS_2D

                # Obtain different encodings for the "claim" query argument
                encoding = CLASSIFIER.encode(claim)
                encoding_5d = EMBEDDERS_5D[core_].transform([encoding])[0] if core_ and core_ in EMBEDDERS_5D else EMBEDDERS_5D[list(EMBEDDERS_5D.keys()[0])].transform([encoding])[0]
                encoding_2d = EMBEDDERS_2D[core_].transform([encoding_5d])[0] if core_ and core_ in EMBEDDERS_2D else EMBEDDERS_2D[list(EMBEDDERS_2D.keys()[0])].transform([encoding_5d])[0]

                # Create new row to append to dataframe
                new_row = {"display_text": claim, "color": "#000000", "x": encoding_2d[0], "y": encoding_2d[1], "size": 12, "Topic": "No topic", "id": "claim"}

            else:
                new_row = None

            # Add claim to all plots
            new_plots = dict()

            for keyword in plots:
                new_plots[keyword] = dict()
                for sentiment in plots[keyword]:
                    new_plots[keyword][sentiment] = dict()
                    for community in plots[keyword][sentiment]:
                        if plots[keyword][sentiment][community] is None:
                            new_plots[keyword][sentiment][community] = None
                        else:
                            new_plots[keyword][sentiment][community] = json.dumps(json_item(add_claim_to_bokeh_plot(json.loads(plots[keyword][sentiment][community]), new_row)))

            return jsonify({'data':{"new_figures": new_plots}}), 200
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"Message": "Unauthorized!"}), 401


@app.route("/api/update_topic_names", methods=["POST"])
@flask_praetorian.auth_required
def update_topic_names():
    """API endpoint to update the topic names in the Topic Discovery Bokeh visualisation(s) after the user has renamed
    the topics in the front end

        Query fields under "data" field:
            :figures: (dict) Dictionary containing existing Topic Discovery visualisation(s)
            :topics_per_communities: (dict) Bokeh visualisations for the "Topics per community" visualisation.
            :topic_names: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
                algorithm) and topic names (as saved by the user in the front-end)

        Output:
            :figures: (dict[dict[bokeh.plotting.figure]]) New Bokeh figures for Topic Discovery per keyword (outter dict) \
                and sentiment (inner dict) with new topic names.
            :topics_per_community: (dict) New Bokeh visualisations for the "Topics per community" visualisation with \
                new topic names.
        """
    logger.info("Update Topic Modelling endpoint called!")
    try:
        if flask_praetorian.current_user().is_valid:
            # Get API request header
            req = request.get_json(force=True)
            req = req.get('data', None)

            plots = req['figures']
            topic_names_map = req['topic_names']
            topics_per_communities = req["topics_per_communities"]

            new_plots = dict()
            new_topics_per_com = dict()

            for keyword in plots:
                new_plots[keyword] = dict()
                new_topics_per_com[keyword] = dict()
                for sentiment in plots[keyword]:
                    new_plots[keyword][sentiment] = dict()
                    new_topics_per_com[keyword][sentiment] = dict()
                    if not topics_per_communities is None:
                        for unit in ["proportions", "counts"]:
                            new_topics_per_com[keyword][sentiment][unit] = update_topics_per_communities_plot(topics_per_communities[keyword][sentiment][unit], topic_names_map)
                    for community in plots[keyword][sentiment]:
                        if plots[keyword][sentiment][community] is None:
                            new_plots[keyword][sentiment][community] = None
                        else:
                            new_plots[keyword][sentiment][community] = update_bokeh_plot(plots[keyword][sentiment][community], topic_names_map)
            if topics_per_communities is None:
                new_topics_per_com = None
            return jsonify({"data":{"new_figures": new_plots, "new_topics_per_communities": new_topics_per_com}}), 200
            #return make_response(jsonify({"Message": "Unauthorized!"})), 401
    except Exception as exp:
        logger.warning(f"Error: {exp}")
        logger.warning(f"Error: {traceback.format_exc()}")
        return jsonify({"Message": "Unauthorized!"}), 401


if __name__ == "main":
    app.run(host='0.0.0.0', port=5000, debug=True)