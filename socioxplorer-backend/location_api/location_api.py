#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the end point for the location API.
The API would return the location details based on the requests received.
There are two endpoints. The first one would handle a single user, the other one would handle a list of users.
The API relies on the details provided in the tweet object (geo and user).
"""

import flask
import os
from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename
import json
import re
import time
from location_mapper import *

my_locator = locator()
app = flask.Flask(__name__, template_folder='templates')

@app.route("/api/get_location", methods=["POST"])
def get_location():
    """
    Extracts the locations of the user and tweet from the passed (single) tweet object which includes the user's object.

    Returns:
        dict: a dictionary object that contains the user's location and the tweet's location.
    """
    try:
        tweet = request.get_json()
        user_loc = my_locator.user_level_loc(tweet)
        tweet_loc = my_locator.tweet_level_loc(tweet)
        result = {'user': user_loc, 'tweet': tweet_loc}
        response = json.dumps(result, ensure_ascii=False)


        #print(f"Location api-get_location: {result}")
    except Exception as exp:
        pass
    return response

@app.route("/api/get_locations", methods=["POST"])
def get_locations():
    """
    Extracts the locations of the user and tweet from the passed list of tweet objects which includes the users' object.

    Returns:
        dict: a dictionary object that contains the user's location and the tweet's location.
    """
    result = {}
    tweets = request.get_json()
    print("New request received!")
    try:
        for t_id in tweets.keys():
            user_loc = my_locator.user_level_loc(tweets[t_id])
            tweet_loc = my_locator.tweet_level_loc(tweets[t_id])
            result[t_id] = {'user': user_loc, 'tweet': tweet_loc}

        #print(f"Location api-get_locations: {result[t_id]}")
    except Exception as exp:
        pass
    response = json.dumps(result, ensure_ascii=False)
    return response
