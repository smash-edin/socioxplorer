import os
import requests
import sys
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("configs Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig
configs_path = '../../configs.py'
datasetOptions_path = '../../socioxplorer-frontend/src/.data/datasetOptions.csv'
import ast
import astor
import json 
import pandas as pd

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   
class ConfigModifier(ast.NodeTransformer):
    def __init__(self, cores):
        self.cores = cores

    def visit_ClassDef(self, node):
        if node.name == "ApplicationConfig":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    if any(target.id == 'SOLR_CORES' for target in stmt.targets):
                        stmt.value = ast.List(elts=[ast.Constant(value=core) for core in self.cores], ctx=ast.Load())
        return node

def save_core_to_datasetOptions(filePath, core):
    try:
        df = pd.read_csv(filePath)
        core_temp = " ".join(word.capitalize() for word in core.split("_"))
        new_row = {"key": f"{core}", "text": core_temp, "value": core}
        if not (df['value'] == core).any():
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(filePath, index=False)
    except Exception as exp:
        print(exp)

def delete_core_from_datasetOptions(filePath, core):
    try:
        df = pd.read_csv(filePath)
        if len(df[df['value'] == core]) > 0:
            index_to_remove = df[df['value'] == core].index[0]
            df = df.drop(index_to_remove)
            df.to_csv(filePath, index=False)
        else:
            print(f"Core {core} not found in the datasetOptions.csv file.")
    except Exception as exp:
        print(exp)
        
def save_config_to_file(file_path, cores):
    try:    
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
        modifier = ConfigModifier(cores)
        modified_tree = modifier.visit(tree)
        with open(file_path, 'w') as file:
            file.write(astor.to_source(modified_tree))
    except Exception as exp:
        print(exp)

def init_schema(url):
    scehma_contents = [
    {"name":"id","type":"string","stored":True,"multiValued":False,"required":True,"indexed":True},
    {"name":"createdAt","type":"pdates","multiValued":False,"stored":True},
    {"name":"createdAtDays","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"createdAtMonths","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"createdAtYears","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"userScreenName","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"userName","type":"string","stored":True,"multiValued":False,"omitNorms":True,"indexed":True},
    {"name":"userId","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"usersFollowersCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"usersFriendsCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"retweetCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"favoriteCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"quoteCount","type":"plong","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"replyCount","type":"plong","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"embedding_2d","type":"pfloat","uninvertible":True,"omitNorms":True,"multiValued":True,"indexed":True,"stored":True},
    {"name":"embedding_5d","type":"pfloat","uninvertible":True,"omitNorms":True,"multiValued":True,"indexed":True,"stored":True},
    {"name":"conversationId","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"domains","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"emojis","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"emotion","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"emotionDistribution","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"features","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"fullText","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"fullTextLowered","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"text","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"hashtags","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"mentions","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"retweeters","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"retweetTimes","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"usersDescription","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"usersLocation","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"inReplyToId","type":"string","stored":True,"multiValued":False,"omitNorms":True,"indexed":False,"uninvertible":False},
    {"name":"language","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"languagePlatform","type":"string","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"locationGps","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"userLocation","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"userLocationOriginal","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"locationLanguage","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"matchingRule","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"media","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"original","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"verified","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"placeCountry","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"placeFullName","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"platform","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"possiblySensitive","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"processedDescTokens","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"processedTokens","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"protected","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"quotationId","type":"string","stored":True,"multiValued":False,"indexed":False,"uninvertible":False,"omitNorms":True},
    {"name":"quoteTimes","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"quoteTweets","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"quoters","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"repliesTimes","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"repliesTweets","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"replyCommunity","type":"pint","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"retweetCommunity","type":"pint","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"replyNetworkNodes","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"retweetNetworkNodes","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"sentiment","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"sentimentDistribution","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"topic","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"urls","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"channelId","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"videoId","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"originalText","type":"text_general","stored":True,"multiValued":False,"indexed":False},
    {"name":"authorImageUrl","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"authorChannelUrl","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"authorChannelId","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"canRate","type":"boolean","stored":True,"multiValued":False,"indexed":False},
    {"name":"viewerRating","type":"pint","stored":True,"multiValued":False,"indexed":False},
    {"name":"updatedAt","type":"pdates","multiValued":False,"stored":True},
    {"name":"moderationStatus","type":"string","multiValued":False,"stored":True},
    {"name":"videoCreatedAt","type":"pdates","multiValued":False,"stored":True},
    {"name":"videoCreatedAtDays","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"videoCreatedAtMonths","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"videoCreatedAtYears","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"videoChannelId","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"videoTitle","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"videoChannelTitle","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"videoDescription","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"videoThumbnails","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"videoTags","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"videoCategoryId","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"videoLiveBroadcastContent","type":"text_general","stored":True,"multiValued":False,"indexed":False},
    {"name":"videoLanguage","type":"string","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoLanguagePlatform","type":"string","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoDefaultAudioLanguage","type":"string","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoTopicDetails","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"videoMadeForKids","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoPrivacyStatus","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoLikeCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"videoFavoriteCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"videoViewCount","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"videoHashtags","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"videoMentions","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"videoEmojis","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"videoText","type":"text_general","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoLocalizedTitle","type":"text_general","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoLocalizedDescription","type":"text_general","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"videoProcessedTokens","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"videoSentiment","type":"string","stored":True,"multiValued":False,"indexed":False},
    ]
    headers = {'Content-type': 'application/json'}
    
    try:
        res = requests.get(url + "/fields?wt=json")
        existingFields = [x['name'] for x in json.loads(res.content)['fields']]
        requiredFields = [x for x in scehma_contents if x["name"] not in existingFields]
        payload = {"add-field":requiredFields}
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as exp:
        print(exp)
        return False

def add_core(core_name,path,url,port):
    #If you want to use solr 9.3.0 uncomment the following line and comment the next line.
    if '9.3.0' in path:
        r1 = os.system(f"{path}/bin/solr create -c {core_name}  -p {port}") 
    else:
        r1 = os.system(f"{path}/bin/solr create -c {core_name}  -url {url}:{port}") #This works for solr 9.7.0
    url = f"{url}:{port}/solr/{core_name}/schema"
    r2 = init_schema(url)
    if r1 == 0 and r2:
        if core not in ApplicationConfig.SOLR_CORES:
            ApplicationConfig.SOLR_CORES.append(core)
            #updating config.py file with the new core.
            save_config_to_file(configs_path, ApplicationConfig.SOLR_CORES)
            save_core_to_datasetOptions(datasetOptions_path, core)
        print("The collection has been created successfully and the configs file updated.")

def delete_core(core_name,path,url,port):
    #If you want to use solr 9.3.0 uncomment the following line and comment the next line.
    if '9.3.0' in path:
        r = os.system(f"{path}/bin/solr delete -c {core_name}  -p {port}") 
    else:
        r = os.system(f"{path}/bin/solr delete -c {core_name}  -url {url}:{port}") #This works for solr 9.7.0
    if r == 0:
        if core in ApplicationConfig.SOLR_CORES:
            ApplicationConfig.SOLR_CORES.remove(core)
            # updating the config.py file to delete the removed core.
            save_config_to_file(configs_path, ApplicationConfig.SOLR_CORES)
            delete_core_from_datasetOptions(datasetOptions_path, core)
        print("The collection has been deleted successfully and the configs file updated.")

def start_solr(path, port):
    r1 = os.system(f"{path}/bin/solr start -p {port} > ./.run_solr.log")
    with open('./.run_solr.log', 'r') as file:
        log = file.read()
    os.remove('./.run_solr.log')
    if r1 != 0:
        print("ERR: Solr could not be start.\n")
        if 'choose a different port' in log:
            print(f"Port number {color.BOLD}{port}{color.END} is used by another process.\n \
                Please try with a different port by updating the {color.BOLD}configs.py{color.END} file in {color.BOLD}root{color.END} folder.\n")
        else:
            print("Please check the path and port number and update the configs.py file.\n")
        exit(-1)
    return True

def restart_solr(path, port):
    r1 = os.system(f"{path}/bin/solr restart -p {port} > ./.run_solr.log")
    with open('./.run_solr.log', 'r') as file:
        log = file.read()
    os.remove('./.run_solr.log')
    if r1 != 0:
        print("ERR: Solr could not be restart.\n")
        exit(-1)
    return True

def stop_solr(path, port):
    r1 = os.system(f"{path}/bin/solr stop -p {port} > ./.run_solr.log")
    with open('./.run_solr.log', 'r') as file:
        log = file.read()
    os.remove('./.run_solr.log')
    if r1 != 0:
        print("ERR: Solr could not be stop.\n")
        exit(-1)
    return True

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="The Solr collection name", default=None)
    parser.add_argument('-d', '--command', help="The command to be performed (add or delete core, or start solr).", default=None)

    args = parser.parse_args()
    cmd = args.command
    core = args.core
    err_msg = "Usage: python solr_controller.py -c [core_name] -d [command]\n"
    if cmd == None:
        print("ERR: command not specified.\n \
            Please specify the command to be performed (add/create or delete) to handle a core, or start to run solr).\n \
            Usage: python solr_controller.py -d [command]\n")
        exit(-1)

    elif cmd == "start":
        if start_solr(ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_PORT):
            print("Solr has been started successfully.")
    elif cmd == "stop":
        if stop_solr(ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_PORT):
            print("Solr has been stopped successfully.")
    elif cmd == "restart":
        if restart_solr(ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_PORT):
            print("Solr has been restarted successfully.")
    elif core == None:
        print("ERR: Please specify the collection name (core).\n \
            Usage: python solr_controller.py -c [core_name] -d [command]\n")
        exit(-1)
    else:
        if cmd == "add" or cmd == "create":
            add_core(core, ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_URL, ApplicationConfig.SOLR_PORT)
        
        elif cmd == "delete":
            delete_core(core, ApplicationConfig.SOLR_PATH,ApplicationConfig.SOLR_URL,ApplicationConfig.SOLR_PORT)
