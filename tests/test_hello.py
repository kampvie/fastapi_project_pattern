# Start application before running pytest
from time import sleep

import pytest
import requests

from tests.settings import proc


@pytest.fixture(scope='function')
def supply_text_params():
    text = "Welcome to our test for branch new project"
    return text

def test_hello(supply_text_params):
    proc.start()
    sleep(1)
    response = requests.get(f'http://0.0.0.0:2306/hello/?greetings={supply_text_params}')
    assert response.status_code == 200
    proc.kill()
