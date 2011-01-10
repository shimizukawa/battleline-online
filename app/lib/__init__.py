# -*- coding: utf-8 -*-

import google.appengine.ext.webapp.template # need this before import django
from django.conf import settings
settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
settings.INSTALLED_APPS.append('lib')
settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS)

