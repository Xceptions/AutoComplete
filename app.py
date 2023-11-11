from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_caching import Cache

from core.autocomplete import AutoComplete


app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2"


@app.route('/')
def get_index_html_template():
    """ Standard implementation of Flask render template

        While the plan of the software is to be decoupled
        and work with any frontend, this is a roughly built
        frontend that helps to test the app.
    """
    return render_template("index.html")


@app.route('/train', methods=['POST'])
def train_corpus():
    if request.method == 'POST':
        data = request.get_json()['input_corpus']
        response = AutoComplete( app.config["MONGO_URI"] ).train(data)
        return jsonify({'result': response})


@app.route('/dropdb')
def drop_db():
    """ 
        Returns a map (dict) of [str, str]

        This function drops both collections from the db
        The function performs the following steps:
            - receives the request from the client
            - calls the drop method of the AutoComplete
                class of which, if successful, will drop the MaxWordGraph
                and CorpusGraph collections
            - it returns these documents as a json object to the client
        Args:
            None
        Returns
            Dict: a map/dict[str,List[str]] with 'result' as key and response as value.
                This response is the status of dropping the two collections from the db
    """
    response = AutoComplete( app.config["MONGO_URI"] ).drop_db()
    return jsonify({'result': response})



@app.route('/complete/<phrase>')
# @cache.cached(timeout=10)
def complete(phrase):
    """ 
        Returns a map (dict) of [str, str]

        This function drops both collections from the db
        The function performs the following steps:
            - receives the request data `question` from the client
            - calls the get_answer method of the Info which will
                fetch the answer to the question and return it
            - it returns the answer as a json object to the client
        Args:
            question: str - Question asked from the client
        Returns
            Dict: [str,List[str]] with 'result' as key and response
                as value. This response is the answer to the question
                received from the client
    """
    response = AutoComplete( app.config["MONGO_URI"] ).complete( phrase )
    return jsonify({'result': response})



if __name__ == "__main__":
    app.run()