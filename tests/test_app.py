from app import app
import json

def test_index_route():
    """
        Standard implementation of pytest
        get request
    """
    response = app.test_client().get('/')
    assert response.status_code == 200


def test_train():
    """
        Standard implementation of pytest
        post request
    """
    with app.test_client() as client:
        data = {
            "document": "This is the test data to train on"
        }

        response = client.post(
            "/train",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
        assert(200, response.status_code)


def test_complete():
    """
        Standard implementation of pytest
        get request
    """
    predict = 'to'
    response = app.test_client().get('/complete/' + predict)
    assert response.status_code == 200