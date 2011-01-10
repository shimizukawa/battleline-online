# -*- coding: utf-8 -*-
"""
render card
"""

from django.template import Node, Library, TemplateSyntaxError
from django.utils.safestring import mark_safe
register = Library()


class RenderCardNode(Node):
    def __init__(self, card, front=True, index=None):
        self.card = card
        self.front = front

    def __repr__(self):
        return "<RenderCardNode>"

    def render(self, context):
        card = self.card.resolve(context)
        output = self.nodelist.render(context)
        return output


register.tag(name='render_card')
def do_render_card(parser, token):
    """
    {% render_card card,front,index %}
    """
    bits = list(token.split_contents())
    if len(bits) < 2 or 4 < len(bits):
        raise TemplateSyntaxError("wrong argument")
    card = parser.compile_filter(bits[1])
    if len(bits) >= 3:
        front = bits[2]
    else:
        front = True
    if len(bits) >= 4:
        index = bits[3]
    else:
        index = None
    return RenderCardNode(card, front, index)


