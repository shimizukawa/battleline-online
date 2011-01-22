from webtest import TestApp
from nose.tools import *
from app.controllers.lobby import application

app = TestApp(application())

def test_index():
    response = app.get('/')
    assert_true('Hello world!' in str(response))

