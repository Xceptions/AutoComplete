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


if __name__ == "__main__":
    app.run()