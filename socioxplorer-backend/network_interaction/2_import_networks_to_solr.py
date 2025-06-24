#!/usr/bin/env python3
from os.path import abspath, join
import sys
import json
try:
    source_dir = abspath(join('../data_updater/'))
    sys.path.append(source_dir)
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *
from utils import print_this
from configs import ApplicationConfig, ApplicationPaths
DATA_DIR = ApplicationPaths.SNA_DATA_DIR
DATA_FILE = ApplicationPaths.SNA_DATA_FILE
SNA_THRESHOLD = ApplicationConfig.SNA_THRESHOLD

def get_netowrk_from_json_file(fileName):
    try:
        with open(fileName, "r", encoding="utf-8" ) as fin:
            lines = json.load(fin)
        nodes = dict()
        for node in lines['nodes']:
            if node['key'] not in nodes:
                nodes[node['key']] = f"{node['key']} {int(node['attributes']['modularity_class'])} {int(node['attributes']['size'])} ({node['attributes']['x']}, {node['attributes']['y']})"
        return nodes
    except Exception as exp:
        print_this(f"Error at loading data from file\n{exp}\n")
        return None

if __name__== "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="The Solr core.", default=None)
    parser.add_argument('-i', '--interaction', help="The network interaction (retweet or reply).", default=None)

    args = parser.parse_args()
    core = args.core
    try:
        threshold = int(SNA_THRESHOLD)
    except:
        threshold = 'all'
    interaction = str(args.interaction).strip().lower()
    interaction_options = {'retweet':'retweetTimes', 'reply':'repliesTimes'}
    
    if core == None or interaction_options == None:
        print("Please select the Solr core and the netowrk interaction (retweet/reply). The command might be:\n python 2_import_networks_to_solr.py -c new_core -i retweet\nwhile threshold is optional, the core and interaction are required.")
    else:
        if interaction not in interaction_options.keys():
            print(f"{interaction} is not a valid network interaction. Please select retweet or reply.")
            sys.exit(-1)
        dataSource = SolrClass({})
        input_file = f'{DATA_FILE}_{core}_{threshold}_{interaction}_GRAPH.json'
        nodes_networks = get_netowrk_from_json_file(input_file)

        if core in ApplicationConfig.SOLR_CORES and nodes_networks!= None:
            print(f"{interaction}NetworkNodes")
            response = dataSource.get_network_interactions(solr_core=core, interaction=interaction, interaction_options=interaction_options)
            print(f"{interaction}NetworkNodes")
            if response is not None:
                if "msg" in response.keys():
                    print(response['msg'])
                elif response['response']['numFound'] > 0:
                    tweets_packet = dict()
                    docs = response['response']['docs']
                    print(f"length of data: {len(docs)}")
                    for doc in docs:
                        if interaction_options[interaction] in doc.keys():
                            new_list_of_network = list(set([doc['userScreenName']] + [x.split(" ")[0] for x in doc[interaction_options[interaction]]]))
                        if interaction == 'retweet' and 'retweeters' in doc.keys():
                            new_list_of_network = list(set(new_list_of_network + doc['retweeters']))
                        new_list_of_network = [nodes_networks[k] for k in new_list_of_network if k in nodes_networks.keys()]
                        tweets_packet[doc['id']] = {'id': doc['id'], f'{interaction}NetworkNodes': new_list_of_network, f'{interaction}Community':int(nodes_networks[doc['userScreenName']].split(" ")[1] if doc['userScreenName'] in nodes_networks else -333)}
                    print(f"Saving {interaction} network to Solr")
                    items = list(tweets_packet.values())
                    trials = 1
                    initial_len = len(items)
                    while len(items) > 0 and trials <= 10:
                        items = dataSource.add_items_to_solr(core, items, reduced=trials)
                        if initial_len > len(items):
                            initial_len = len(items)
                            trials = 1
                        else:
                            trials += 1
            print("Extracting Networks Done")