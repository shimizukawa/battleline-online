# -*- coding: utf-8 -*-
# 日本語

import os, sys
sys.path.append(os.path.abspath('..'))

import unittest
from hooks import hook


class HooksTest(unittest.TestCase):
    def test_register_hook(self):
        class Base(object):
            @hook('before')
            def func1(self):
                pass
        obj = Base()
        self.assertEqual(1, len(obj.hooks.befores))

    def test_call_func(self):
        class Base(object):
            value = 0
            @hook('before')
            def func1(self):
                self.value = 1
        obj = Base()
        obj.hooks.exec_before_hooks()
        self.assertEqual(1, obj.value)

    def test_hooks_does_not_inherit(self):
        class Base(object):
            value1 = 0
            @hook('before')
            def func1(self):
                self.value1 = 1
        class Derive(Base):
            value2 = 0
            @hook('before')
            def func2(self):
                self.value2 = 2
        obj = Derive()
        obj.hooks.exec_before_hooks()
        self.assertEqual(0, obj.value1) # value1 was inherited, but not hooked
        self.assertEqual(2, obj.value2)

    def test_hooks_can_inherit(self):
        #import pdb;pdb.set_trace()
        class Base(object):
            value1 = 0
            @hook('before')
            def func1(self):
                self.value1 = 1
        class Derive(Base):
            hooks = Base.hooks.copy()
            value2 = 0
            @hook('before')
            def func2(self):
                self.value2 = 2
        obj = Derive()
        obj.hooks.exec_before_hooks()
        self.assertEqual(1, obj.value1)
        self.assertEqual(2, obj.value2)

        obj = Base()
        obj.hooks.exec_before_hooks()
        self.assertEqual(1, obj.value1)
        self.assert_(not hasattr(obj, 'value2'))


    def test_inherited_brother_hooks_must_not_pollution(self):
        class Base(object):
            value1 = 0
            @hook('before')
            def func1(self):
                self.value1 = 1
        class DeriveA(Base):
            value2 = 0
            @hook('before')
            def func2(self):
                self.value2 = 2
        class DeriveB(Base):
            value3 = 0
            @hook('before')
            def func3(self):
                self.value3 = 3
    
        obj = Base()
        obj.hooks.exec_before_hooks()
        self.assertEqual(1, obj.value1)
        self.assert_(not hasattr(obj, 'value2'))
        self.assert_(not hasattr(obj, 'value3'))

        obj = DeriveA()
        obj.hooks.exec_before_hooks()
        self.assertEqual(0, obj.value1) # value1 was inherited, but not hooked
        self.assertEqual(2, obj.value2)
        self.assert_(not hasattr(obj, 'value3'))

        obj = DeriveB()
        obj.hooks.exec_before_hooks()
        self.assertEqual(0, obj.value1) # value1 was inherited, but not hooked
        self.assert_(not hasattr(obj, 'value2'))
        self.assertEqual(3, obj.value3)

    def test_inherit_hooks_must_not_pollution(self):
        class Base(object):
            value1 = 0
            @hook('before')
            def func1(self):
                self.value1 = 1
        class DeriveA(Base):
            hooks = Base.hooks.copy()
            value2 = 0
            @hook('before')
            def func2(self):
                self.value2 = 2
        class DeriveB(Base):
            value3 = 0
            @hook('before')
            def func3(self):
                self.value3 = 3
    
        obj = DeriveB()
        obj.hooks.exec_before_hooks()
        self.assertEqual(0, obj.value1) # value1 was inherited, but not hooked
        self.assertEqual(3, obj.value3)
        self.assert_(not hasattr(obj, 'value2'))


def test_suite():
    return unittest.TestSuite((
        TestSuite(HooksTest),
    ))

if __name__ == '__main__':
    unittest.main()

