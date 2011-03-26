# -*- coding: utf-8 -*-

from webtest import TestApp
from nose.tools import *
from app.controllers.lobby import application

app = TestApp(application())

def test_index():
    response = app.get('/lobby')
    assert_true('Googleアカウントでログイン' in response.body)

