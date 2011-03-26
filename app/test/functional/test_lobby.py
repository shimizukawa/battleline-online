# -*- coding: utf-8 -*-

from webtest import TestApp
from nose.tools import *
from app.controllers.lobby import application
from gaefw.test.tools import gae_login

app = TestApp(application())


def test_anonymous_index():
    response = app.get('/lobby')
    assert_true('Googleアカウントでログイン' in response.body)
    assert_false('新規ゲームを作成' in response.body)


def test_loggedin_index():
    gae_login()
    response = app.get('/lobby')
    assert_true('新規ゲームを作成' in response.body)
    assert_false('Googleアカウントでログイン' in response.body)

