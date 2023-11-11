import pymongo
from pymongo import MongoClient, UpdateOne, InsertOne
from bson.objectid import ObjectId
from core.structs import CorpusGraph

from typing import List, Tuple, Dict
import string


class AutoComplete:

    def __init__(self, conn:str):
        """
            Establishes a connection to the database using the
            connection string that is received from the client
            Args:
                conn : str - connection string to the mongodb
                        instance
            Attributes
                connection: MongoClient(str) - connection to the
                        mongodb instance
                db: MongoClient.DB - the connection to the database
        """
        self.connection = MongoClient(conn)
        self.db = self.connection.AutoCompleteDB

    
    def _clean_text(self, text: str) -> str:
        """
            Returns a cleaned text from the input text
            It performs the following
                - convert the text to lowercase
                - remove punctuations
                - remove numbers
                - remove extra spaces
            Args
                text: str - input string received with the 
                    expectation of being cleaned
            Returns
                text: str - the cleaned version of the input
                    string
        """
        text = text.lower()
        PUNCT_TO_REMOVE = string.punctuation
        text = text.translate(str.maketrans('', '', PUNCT_TO_REMOVE))
        text = ''.join([char for char in text if not char.isdigit()])
        text = " ".join(text.split())

        return text


    def _combine_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """
            Returns a dictionary of combined keys
            This method takes in two dictionaries, expectedly
            the dictionary generated from the `_generate_word_map`
            method, and the dictionary from the document(MongoDB)
            retrieved from the collection. This combination will
            be used to update the document(MongoDB) in the collection
            This function performs the following
                - receives two dictionaries `dict1` and `dict2`
                - add all common keys in `dict1` to `dict2`, summing up
                    their values
                - add uncommon keys in `dict1` to `dict2`
                - return `dict2`
            Args
                dict1: str - input dictionary 1
                dict2: str - input dictionary 2
            Returns
                dict2: str - combined dictionary 1 and dictionary 2
        """
        for key in dict2:
            if key in dict1:
                dict2[key] = dict2[key] + dict1[key]
            
        for key in dict1:
            if key not in dict2:
                dict2[key] = dict1[key]

        return dict2


    def _generate_word_map(self,
                            corpus: List[str],
                            predictions_doc: List[Dict[str, int]]) -> Dict:
        """
            Returns a dictionary
            This method returns a dictionary of str -> str -> int.
            It generates a map of words(present) to other words(next),
            and how many times they (words(next)) appear after
            words(present). It also generates a map (`predictions`) 
            of words to the most occurring word after it, which in turn
            maps to the number of times this word appears after it.
            This is what will be used for prediction
            This function performs the following
                - receives a list `corpus` which contains strings
                - receives a dictionary `predictions_doc` which contains
                    two keys `word` (value - str) and `max_words`(val: a
                    str mapping to dict of str mapping to an integer)
                - it creates two empty dicts `word_map` and `predictions`
                - if there is prediction data in the `predictions_doc`
                    it uses it to populate the `predictions` variable
                - iterates through the corpus and uses it to populate the
                    `word_map` var using the rule that each word in the
                    corpus should be a key and its value should be every other
                    word in the corpus that follows it each time it occurs.
                    These words that follow should also map to how many times
                    they appear after the key words.
                - While performing the iteration, check if any word's count has
                    surpassed key word's highest word count in `predictions`.
                    If yes, this word becomes to new prediction, and its count
                    becomes the new prediction_count
            Args
                corpus: List[str] - a list of strings containing words
                    Expectedly the input from the user, after being
                    cleaned
            Return
                Dict[str, Dict[str, int]] - a dictionary of dictionaries,
                    mapping words to (words to counts). Represents 
                    CorpusGraph. Called word_map
                Dict[str, Dict[str, int]] - a dictionary of dictionaries,
                    mapping words to (words to counts). Represents 
                    MaxWordGraph. Called predictions
        """
        word_map = {}
        predictions = {}
        for doc in predictions_doc:
            if len(doc) > 0:
                predictions = predictions_doc[0]["predictions"]

        for idx in range(len(corpus)-1):
            word = corpus[idx]
            if word not in word_map:
                word_map[word] = {}
            word_to_add = corpus[idx+1]
            if word_to_add in word_map[word]:
                word_map[word][word_to_add] += 1
            else:
                word_map[word][word_to_add] = 1

            if word not in predictions:
                predictions[word] = {
                    'prediction': '',
                    'prediction_count': 0
                }

            if word_map[word][word_to_add] > predictions[word]['prediction_count']:
                predictions[word]['prediction'] = word_to_add
                predictions[word]['prediction_count'] = word_map[word][word_to_add]

        return word_map, predictions


    def train(self, corpus: str) -> bool:
        """
            Returns a boolean indicating whether the train operation
            was successful.
            This method adds documents to the CorpusGraph and MaxWordGraph
            structured in such a way that satisfies what we term as
            training, which is to map words to other words that follow
            them and their frequencies
            It performs the following
                - receives the corpus: str from the `train_corpus` method
                - cleans the corpus and splits it into a list of strings
                - retrieves the `predictions_doc` which is the store of
                    mappings of predictions as structured in our structs
                - retrieves the `collection` which is a list of all documents
                    containing the words in corpus
                - generates `word_map` and `predictions` which are the
                    words in corpus structured in the expected formats of
                    CorpusGraph and MaxWordGraph respectively. It does
                    this by passing in the corpus and predictions_doc
                - In `word_map` and `predictions`, some words which
                    exist in collection and predictions_doc will be present,
                    and others will not. They will be new words. The goal
                    is to update the collections with the data of the words
                    that exist, and insert the new ones
                - Prepare `word_map` for both update and insert bulk operations
                    depending on the word
                - Prepare `predictions` for both update and insert bulk operations
                    depending on the word
                - Run the operations on their appropriate collections. `CorpusGraph`
                    for `word_map` and `MaxWordGraph` for `predictions`
                - Return an AND of the result of their operations
            Args
                corpus: List[str] - a list of strings containing words
                    Expectedly the input from the user, after being
                    cleaned
            Return
                Bool - a bool of the status of the bulk write operations
        """
        corpus = self._clean_text(corpus)
        corpus = corpus.split(" ")
        db_conn = self.db
        predictions_doc = db_conn.MaxWordGraph.find()
        collection = db_conn.CorpusGraph.find(
            { "word": { "$in": corpus } }
        )
        word_map, predictions = self._generate_word_map(
                                            corpus,
                                            predictions_doc
                                        )

        # adding word map
        word_set = set(corpus)
        bulk_write_operations_corpus = []
        for document in collection:
            data_to_update: CorpusGraph = {
                "word": document["word"],
                "graph": document["graph"]
            }
            bulk_write_operations_corpus.append(
                UpdateOne(
                    { "word": data_to_update["word"] },
                    { "$set": {
                        "graph": self._combine_dicts(
                                    data_to_update["graph"],
                                    word_map[data_to_update["word"]]
                                )
                        }
                    }
                )
            )
            if document["word"] in word_set:
                word_set.remove(document["word"])

        for word in word_set:
            if word in word_map:
                data_to_insert: CorpusGraph = {
                    "doctype": "max_word",
                    "word": word,
                    "graph": word_map[word]
                }
                bulk_write_operations_corpus.append(
                    InsertOne({
                        "word": data_to_insert["word"],
                        "graph": data_to_insert["graph"]
                    })
                )

        # adding predictions
        word_set = set(corpus)
        bulk_write_operations_max_word = []
        for document in predictions_doc:
            data_to_update: MaxWordGraph = {
                "word": document["word"],
                "max_words": document["max_words"]
            }
            bulk_write_operations_max_word.append(
                UpdateOne(
                    { "word": data_to_update["word"] },
                    { "$set": {
                        "max_words": data_to_update["max_words"]
                        }
                    }
                )
            )
            if document["word"] in word_set:
                word_set.remove(document["word"])

        for word in word_set:
            if word in predictions:
                data_to_insert: MaxWordGraph = {
                    "word": word,
                    "max_words": predictions[word]
                }
                bulk_write_operations_max_word.append(
                    InsertOne({
                        "word": data_to_insert["word"],
                        "max_words": data_to_insert["max_words"]
                    })
                )

        result_corpus = db_conn.CorpusGraph.bulk_write(bulk_write_operations_corpus)
        result_max_word = db_conn.MaxWordGraph.bulk_write(bulk_write_operations_max_word)
        return result_corpus.acknowledged and result_max_word.acknowledged


    def complete(self, word: str) -> str:
        word = word.lower()
        predictions_doc = self.db.MaxWordGraph.find(
            { "word": word }
        )
        return predictions_doc[0]['max_words']['prediction']



    def drop_db(self):
        """
        Returns the status of dropping both collections in the db
        Args:
            None
        Returns
            Dict[str, str]: the status of dropping the collections
        """
        drop_CorpusGraph = self.db.drop_collection("CorpusGraph")
        drop_MaxWordGraph = self.db.drop_collection("MaxWordGraph")
        return drop_CorpusGraph and drop_MaxWordGraph
