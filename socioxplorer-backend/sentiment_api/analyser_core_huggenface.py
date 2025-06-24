import flask
import os
from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename
import json
from transformers import pipeline
import re, string
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import sys
import shutil
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    sys.exit(-1)
from configs import ApplicationPaths
#The currently supported languages by the used sentiment analysis model (cardiffnlp/twitter-xlm-roberta-base-sentiment)
SUPPORTED_LANGUAGES = ['ar', 'en', 'fr', 'de', 'hi', 'it', 'sp', 'pt']

MODEL = ApplicationPaths.SENTIMENT_ANALYSIS_MODEL_PATH
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.save_pretrained(MODEL)


def strip_links(text, keep_flag=False):
    """A function to strip links from a text string and replace them with a placeholder "HTTP" when keep_flag is True, or with an empty space when keep_flag is False.

    Args:
        text (str): the text string to strip links from.
        keep_flag (bool, optional): a flag to determine whether to keep the placeholder or not. Defaults to False.
    Returns:
        str: the text string with links stripped.
    """
    return re.sub('http[\w:\/\.]+', 'HTTP ' , text) if keep_flag else re.sub('http[\w:\/\.]+', ' ' , text)

def strip_mentions(text, keep_flag=False):
    """A function to strip mentions from a text string and replace them with a placeholder "@USER" when keep_flag is True, or with an empty space when keep_flag is False.

    Args:
        text (_type_): the text string to strip mentions from.
        keep_flag (bool, optional): a flag to determine whether to keep the mention placeholder or not. Defaults to False.

    Returns:
        str: the text string with mentions stripped.
    """
    return re.sub('@[\w+]+', '@USER ' , text) if keep_flag else re.sub('@[\w+]+', ' ' , text)

def strip_all_entities(text):
    """A function to strip all punctuations defined in "string.punctuation" from a text string and replace them with a space unless the punctuation is a mention or a hashtag.
    The function also removes any leading or trailing spaces from the text.

    Args:
        text (str): the text string to strip entities from.

    Returns:
        str: the text string with entities stripped. The returned string is a concatenation of all the words in the input text separated by a single space.
    """
    entity_prefixes = ['@','#']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)

def preprocess(text, remove_http_mentions=False, keep_flag = True):
    """A function to preprocess a text string by removing mentions and links. The function also replaces multiple spaces, newlines, and tabs with a single space.

    Args:
        text (str): the text string to preprocess.
        remove_http_mentions (bool, optional): a flag to determine whether to remove mentions and links or not. Defaults to False.
        keep_flag (bool, optional): a flag to determine whether to keep the placeholders for mentions and links or not. Defaults to True.

    Returns:
        str: the preprocessed text string.
    """
    return re.sub('[\n\t/ ]+', ' ', strip_mentions(strip_links(text, keep_flag), keep_flag)) if remove_http_mentions else re.sub('[\n\t ]+', ' ', text)
			


def huggingface_sent(sentence, return_tensors='pt'):
    """A function to classify the sentiment of a sentence using a pre-trained Huggingface model. The function preprocesses the input sentence, encodes it using the tokenizer, and passes it to the model to get the output. The output is then converted to probabilities using the softmax function and the label with the highest probability is returned.

    Args:
        sentence (str): the input sentence to classify.
        return_tensors (str, optional): the type of tensors to return. Can be 'pt' for PyTorch tensors or 'tf' for TensorFlow tensors. Defaults to 'pt'.

    Returns:
        str: the predicted sentiment label.
    """
    text=sentence
    if (len(text)>0):
        try:
            text = preprocess(text, remove_http_mentions=True, keep_flag = False)
            encoded_input = tokenizer(text, truncation=True, max_length=512, return_tensors=return_tensors)
            output = model(**encoded_input)
            if return_tensors=='tf':
                scores = output[0][0].numpy()
            else:
                scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            ranking = np.argsort(scores)
            ranking = ranking[::-1]
            return config.id2label[ranking[0]]
        except Exception as e :
            print(e)
            return 'Invalid'
    else:
        return 'Neutral'
    
def predict_list(tweets):
    """A function to predict the sentiment of a list of sentences (tweets) using the Hugging Face model. The function processes the input tweets and predicts the sentiment of each tweet using the Hugging Face model. The predictions are stored in a dictionary with the tweet IDs as keys and the predicted sentiment labels as values. The function prints the statistics of the number of processed tweets and their predictions.

    Args:
        tweets (List): a list of sentinces to predict the sentiment of.

    Returns:
        dict: a dictionary containing the tweet IDs as keys and the predicted sentiment labels as values.
    """
    print('Data Processing\n')
    predictions={}
    predictions_stats ={'Positive':0,'Negative':0,'Neutral':0,'OtherLanguages':0, 'Invalid':0}

    for t_id in tweets.keys():
        if(tweets[t_id]['language'] in SUPPORTED_LANGUAGES):
            prediction_output = huggingface_sent(str(tweets[t_id]['fullText']))
            prediction_output = prediction_output.replace(prediction_output[0], prediction_output[0].upper())
        else :
            prediction_output='OtherLanguages'

        predictions[t_id] = prediction_output
        predictions_stats[prediction_output]+=1

    print(f'Processed {len(tweets.keys())}, Hugging Face')
    print(f'Prediction stats : {predictions_stats}.')
    return predictions

print('Running analyser ....\n')
