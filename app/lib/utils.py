# -*- coding: utf-8 -*-
from google.appengine.ext import db


def setdefault(dic, key, value):
    dic[key] = dic.get(key, value)

def obj2key(objects):
    return [x.key() for x in objects]

def key2obj(keys):
    return [db.get(k) for k in keys]


def seq_finder(seq, value, attr_name=None):
    #FIXME: must stop iteration if find.
    if attr_name:
        values = [x for x in seq if getattr(x, attr_name) == value]
    else:
        values = [x for x in seq if x == value]
    if values:
        return values[0]
    else:
        return None


def Accessor(name):
    def getter(self):
        return key2obj(getattr(self, name))
    def setter(self, obj):
        setattr(self, name, obj2key(obj))
    return property(getter, setter)


class ListPropertyWrapper(list):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        objects = getattr(parent, name)
        self.extend(objects)

    def __getitem__(self, index):
        return db.get(super(ListPropertyWrapper,self).__getitem__(index))

    def __setitem__(self, index, obj):
        key = obj.key()
        getattr(self.__parent__, self.__name__)[index] = key
        return super(ListPropertyWrapper,self).__setitem__(index, key)

    def __iter__(self):
        return (db.get(k) for k in super(ListPropertyWrapper,self).__iter__())

    def __len__(self):
        return super(ListPropertyWrapper,self).__len__()

    @property
    def size(self):
        """ compatible to db.ListProperty query object attribute """
        return len(self)

    def append(self, obj):
        return super(ListPropertyWrapper,self).append(obj)

    def remove(self, obj):
        return super(ListPropertyWrapper,self).remove(obj)

    def insert(self, index, obj):
        return super(ListPropertyWrapper,self).insert(index, obj)


def ListPropertyAccessor(name):
    def getter(self):
        return ListPropertyWrapper(self, name)
    def setter(self, obj):
        setattr(self, name, obj2key(obj))
    return property(getter, setter)

