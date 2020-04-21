import json

import pytest

from SARChecker import app


@pytest.fixture()
def apigw_event():
    """ Blank Event - Does not matter"""

    return {
        
    }


def test_lambda_handler(apigw_event, mocker):

    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
    # assert "location" in data.dict_keys()
