# -*- coding: utf-8 -*-

# from google.appengine.ext.webapp.template import render

import os
from jinja2 import Environment, FileSystemLoader

def render(path, value_dict):
    env = Environment(
        extensions=['jinja2.ext.with_', 'jinja2.ext.autoescape'],
        loader=FileSystemLoader(os.path.dirname(path))
    )
    template = env.get_template(os.path.basename(path))
    return template.render(**value_dict)

