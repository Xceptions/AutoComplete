from typing import List, Dict, TypedDict, Any

"""
Defines the structs of the documents in each collection in our MongoDB

There are two collections in our DB
    - CorpusGraph: The document design of the collection

    e.g.
        {
            'word': 'I',
            'graph': {'want': 1, 'am': 2},
        }

    - MaxWordGraph: The collection holding the prediction for
        each word

    e.g.
        {
            max_words: {
                "I": {
                    "prediction":"am"
                    "prediction_count": 2
                },
                "am":{
                    "prediction":"going"
                    "prediction_count": 3
                }
            }
        }
"""

class CorpusGraph(TypedDict):
    word: str
    graph: Dict[str, int]
    maxWord: str
    maxCount: int

class MaxWordGraph(TypedDict):
    doctype: str
    word: str
    max_words: Dict[str, Dict[str, Any]]