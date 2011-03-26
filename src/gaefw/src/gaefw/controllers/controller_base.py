# -*- coding: utf-8 -*-

import os, sys
from google.appengine.ext import webapp

from gaefw.hooks import hook, Hooks
from gaefw import template

__all__ = ['ControllerBase', 'StopRequestProcess']


class DictMapper(dict):
   def __getattr__(self, name):
       if name in self:
           return self[name]
   def __setattr__(self, name, value):
       self[name] = value


class StopRequestProcess(Exception):
    pass


class ControllerBase(webapp.RequestHandler):
    hooks = Hooks()
    helper_factory = None

    def __init__(self, *args, **kw):
        super(ControllerBase, self).__init__(*args, **kw)
        self._v = DictMapper()

    @property
    def _file_path(self):
        m = __import__(self.__class__.__module__)
        l = [m] + self.__class__.__module__.split('.')[1:]
        basepath = reduce(lambda x,y:getattr(x,y),l).__file__
        return os.path.abspath(basepath)

    @property
    def _app_path(self):
        dirpath, name = os.path.split(self._file_path)
        return os.path.dirname(dirpath)

    @property
    def _controller_name(self):
        dirpath, name = os.path.split(self._file_path)
        name, ext = os.path.splitext(name)
        return name

    def render(self, filename, template_values={}, layout='application.html'):
        values = self._v.copy()
        values.update(template_values)
        values['helper'] = self.helper_factory(self, values)

        apppath = self._app_path
        viewpath = os.path.join(apppath, 'views', self._controller_name, filename)
        rendered_view = template.render(viewpath, values)

        values['content_for_layout'] = rendered_view

        layoutpath = os.path.join(apppath, 'views', 'layouts', layout)
        self.response.out.write(template.render(layoutpath, values))

    def get(self, *args):
        actions = []
        args = list(args)
        if args:
            actions = filter(None, args.pop(0).split('/')) or []
        if not actions:
            actions.append('index')
        method_name = actions.pop(0)
        if actions:
            args[0:0] = '/'.join(actions)
        method = getattr(self, method_name, None)
        if method:
            r = None
            try:
                if self.hooks:
                    Hooks.exec_hooks(self, 'before')
                r = method(*args)
                if self.hooks:
                    Hooks.exec_hooks(self, 'after')
            except StopRequestProcess, e:
                pass
            return r

        return self.response.set_status(404)


