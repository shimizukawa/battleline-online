# -*- coding: utf-8 -*-
"""
backport ``with`` statement from django 1.0.3
"""

from django.template import Node, Library, TemplateSyntaxError
register = Library()


class WithNode(Node):
    def __init__(self, var, name, nodelist):
        self.var = var
        self.name = name
        self.nodelist = nodelist

    def __repr__(self):
        return "<WithNode>"

    def render(self, context):
        val = self.var.resolve(context)
        context.push()
        context[self.name] = val
        output = self.nodelist.render(context)
        context.pop()
        return output


def do_with(parser, token):
    """
    Adds a value to the context (inside of this block) for caching and easy
    access.

    For example::

        {% with person.some_sql_method as total %}
            {{ total }} object{{ total|pluralize }}
        {% endwith %}
    """
    bits = list(token.split_contents())
    if len(bits) != 4 or bits[2] != "as":
        raise TemplateSyntaxError("%r expected format is 'value as name'" %
                                  bits[0])
    var = parser.compile_filter(bits[1])
    name = bits[3]
    nodelist = parser.parse(('endwith',))
    parser.delete_first_token()
    return WithNode(var, name, nodelist)
do_with = register.tag('with', do_with)


