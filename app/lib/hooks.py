# -*- coding: utf-8 -*-

import sys

__all__ = ['hook', 'Hooks']


class Hook(object):
    def __init__(self, timing, func):
        self.timing = timing
        self.func = func

    def __call__(self, *args, **kw):
        return self.func(self.inst, *args, **kw)

    def __get__(self, inst, class_=None):
        if inst is None:
            return self
        result = self.__class__.__new__(self.__class__)
        result.__dict__.update(self.__dict__)
        result.inst = inst
        return result


class hook:
    def __init__(self, timing=None, hooks=None):
        caller_locals = sys._getframe(1).f_locals
        if hooks is None:
            hooks = caller_locals.get('hooks')
        if hooks is None:
            hooks = caller_locals['hooks'] = Hooks()
        self.hooks = hooks
        self.timing = timing

    def __call__(self, func):
        if isinstance(func, Hook):
            func = func.func
        hook = Hook(self.timing, func)
        self.hooks.append(hook)
        return hook


class Hooks(object):
    def __init__(self, *hooks):
        self._hooks = hooks

    def __iter__(self):
        return iter(self._hooks)

    def __len__(self):
        return len(self._hooks)

    def append(self, hook):
        self._hooks += (hook,)

    @classmethod
    def exec_hooks(klass, obj, timing=None):
        [x() for x in obj.hooks if timing in [None, x.timing]]

    # TODO need test
    def __add__(self, other):
        return self.__class__(*(self._hooks + other._hooks))

    def copy(self):
        return self.__class__(*self._hooks)

    def __get__(self, inst, class_):
        if inst is None:
            return self
        return self.__class__(*[a.__get__(inst) for a in self._hooks])

