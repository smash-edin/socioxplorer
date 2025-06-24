#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the location mapper module.
The module provides the ability to identify the location of a user/tweet based on the available information.
For the tweet-level location, we rely on the location information provided in the tweet object.
For the user location we utilize the location field in the user-object.
The location field provides the user with the ability to provide any text she/he wants, we apply some
preprocessing and dictionary matching to identify any provided location. 
If we couldn't identify the location then we rely on the language to assign a country to a user.
The dictionary contains the European cities that has a population larger the 10K and we tried to cover the places' names in many languages.
"""

import pandas as pd
import numpy as np
import json
import re
import string
from ftlangdetect import detect

map_lang_to_country = {
	'zh-cn': 'China',
	'zh-tw': 'China',
	'ar': 'Arab Countries',
	'ja':'Japan',
	'ko':'Korea, Republic of',
	'ru':'Russian Federation',
	'hi':'India',
	'bn':'Bangladesh'}

class locator:
	# initializing all the required resources.
	def __init__(self):
		with open('./resources/processed_all_lang_countries.json', 'r',encoding='utf-8') as json_file:
			self.countries = json.load(json_file)

		with open('./resources/new_109k_cities_wordwide.json', 'r',encoding='utf-8') as json_file:
			self.cities = json.load(json_file)

		with open('./resources/lang_to_country.json', 'r',encoding='utf-8') as json_file:
			self.lang_to_country = json.load(json_file)

	def tweet_level_loc(self, tweet):
		"""A function to get the location of the tweet based on the tweet's place attribute. If the place attribute is not available, the location is set to 'not_available'.
		It detects the country using the geolocation information in the tweet.

		Args:
			tweet (dict): A dictionary containing the tweet data including the place attribute.

		Returns:
			str: The location of the tweet.
		"""
		location = 'not_available'
		if tweet == None:
			return location
		else:
			if 'place' in tweet.keys():
				if 'country' in tweet['place'].keys():
					gps_loc = str(tweet['place']['country']).strip()
					if gps_loc == 'not_available':
						return location
					location = self.process_location(gps_loc)
					if location != 'not_available':
						return location
				if 'placeFullName' in tweet['place'].keys():
					gps_loc = str(tweet['place']['placeFullName']).strip()
					if gps_loc == 'not_available':
						return location
					location = self.process_location(gps_loc)
					if location != 'not_available':
						return location
		return location


	def user_level_loc(self, tweet):
		"""
		Extracts the location of the user from the user's object in the tweet.

		This function attempts to extract the user's location in the following steps:
		1. Tries to split the location string by punctuation and spaces.
		2. Tries to map the location to a country name, starting with special cases like the United States and the United Kingdom.
		3. Calls the get_country function to map the location to a country name.
		4. Calls the get_location function to map the location to a city name.
		5. If the location is still not available, attempts to detect the language of the location string.

		Args:
			tweet (dict): A dictionary object that contains the tweet information which must includes the user object.

		Returns:
			str: The extracted location if identifiable, 'not_available' otherwise.
		"""
		given = tweet['user']['location']
		location = 'not_available'

		if given is None or str(given) == 'nan' or len(given) < 2:
			return 'not_available'

		return self.process_location(given)

	def process_location(self, given):
		# first try to split by punctuation
		parts1 = [x.strip().casefold().translate(str.maketrans('', '', string.punctuation)) for x in re.split(r',|-|\(|\)|\\|/|&', given)]

		# then, split by spaces
		parts2 = [x.strip().casefold().translate(str.maketrans('', '', string.punctuation)) for x in given.split()]

		parts_list =[parts1, parts2]
		# treat special cases:
		for parts in parts_list :

			# special cases for US locations:
			if 'usa' in parts or 'us' in parts or 'united states'  in parts or 'new england' in parts:
				return 'United States of America'

			# try  with British locations
			if 'united kingdom' in parts or 'great britain' in parts or 'british' in parts or 'uk' in parts or 'gb' in parts:
				return 'United Kingdom of Great Britain and Northern Ireland'

			# try to map the country name, this is to avoid any duplicates in the cities names
			for p in parts:
				location = self.get_country(p)
				if(location != 'not_available'):
					return location

			# last mapping the city name to a country
			for p in parts:
				location = self.get_location(p)
				if(location != 'not_available'):
					return location

		# if all dont work with try with detecting language
		# identifying the language of the location field
		# we detect only top word languages
		# we dont consider other languages because they may render a lot of false positive locations such as suriname or andorra
		if (location == 'not_available'):
			try:
				language = detect(given)
				if 'lang' in language:
					language = language['lang']
				if language in map_lang_to_country.keys():
					location = map_lang_to_country[language]
			except:
				pass
		return location

	def get_location(self, location):
		"""
		Converts the location to one of the available countries

		Args:
			location (str): The location string to be converted.

		Returns:
			str: The city name if the location string is a city name, 'not_available' otherwise.
		"""
		if (location in self.cities.keys()):
			return self.cities[location]
		return 'not_available'


	def get_country(self, location):
		"""
		Converts a location string to a country name.

		Args:
			location (str): The location string to be converted.

		Returns:
			str: The country name if the location string is a country name, 'not_available' otherwise.
		"""
		mapping_dict = {'scotland': 'United Kingdom of Great Britain and Northern Ireland',
        'england': 'United Kingdom of Great Britain and Northern Ireland',
        'wales': 'United Kingdom of Great Britain and Northern Ireland',
        'northern ireland': 'United Kingdom of Great Britain and Northern Ireland',
        'uk': 'United Kingdom of Great Britain and Northern Ireland',
        'united kingdom': 'United Kingdom of Great Britain and Northern Ireland',
        'us': 'United States of America',
        'united states': 'United States of America',
        'usa': 'United States of America',
        'america': 'United States of America'}

		if (location in mapping_dict.keys()):
			return mapping_dict[location]
		elif (location in self.countries.keys()):
			return self.countries[location]
		return 'not_available'
