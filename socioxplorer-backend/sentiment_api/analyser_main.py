from analyser_core_huggenface import *
import shutil
import os


if os.path.exists('cardiffnlp'):
    shutil.rmtree('cardiffnlp', )

app = flask.Flask(__name__, template_folder='templates')

@app.route("/api/predict", methods=["POST"])
def api_predict_list():
    """
    A function for the api to receive the prediction requests, call predict_list and return the response.
    """
    tweets = request.get_json()
    print("[SA]: Data Received.\n")
    predictions = predict_list(tweets)
    response = json.dumps(predictions)
    del tweets
    del predictions
    
    return response

@app.route("/api/test", methods=["POST"])
def api_test():
    """
    A test function for the api to receive the prediction requests, call predict_list and return the response.
    """
    #tweets = request.get_json()
    #print(tweets)
    #print('\n\n')
    #print(type(tweets))
    predictions = stanford_sent(tweets['sentence'])
    test={1111:{'language':'en', 'fullText':'We hate you'},2222:{'language':'en', 'fullText':'We love you'}}
    pred=predict_list(test)
    res={'inp':predictions,'builtin':pred}
    response = json.dumps(res)

    return response
