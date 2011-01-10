# -*- coding: utf-8 -*-
"""
call helper tag
"""

from django.template import Node, Library, TemplateSyntaxError
from django.template import resolve_variable
register = Library()

from app.helpers import Helper


class HelperNode(Node):
    def __init__(self, name, args, kw):
        self.name = name
        self.args = args
        self.kw = kw

    def __repr__(self):
        return "<HelperNode>"

    def render(self, context):
        helper = context.get('helper')
        helper = Helper(helper.controller, context)
        attr = getattr(helper, self.name, None)
        if attr is None:
            output = ''
        elif callable(attr):
            args = [resolve_variable(x, context) for x in self.args]
            kw = dict((k,resolve_variable(v, context))
                       for k,v in self.kw.iteritems())
            output = attr(*args, **kw)
        else:
            output = attr
        return str(output)


def do_helper(parser, token):
    """
    {% helper helperfunc arg1,...,argN kw1=x,...,kwN=z %}
    """
    tag, helper_name, args, kw = (token.split_contents() + [None,]*4)[:4]
    if helper_name is None:
        raise TemplateSyntaxError("%s needs helper name." % (tag or 'helper'))
    if not getattr(Helper, helper_name):
        raise TemplateSyntaxError("`Helper.%s` is not exist." % helper_name)

    try:
        args = args and args.split(',') or []
        kw = kw and dict([x.split('=') for x in kw.split(',')]) or {}
    except:
        raise TemplateSyntaxError("%s receive wrong arguments: %s, %s" % (helper_name, args, kw))

    return HelperNode(helper_name, args, kw)

do_helper = register.tag('helper', do_helper)

