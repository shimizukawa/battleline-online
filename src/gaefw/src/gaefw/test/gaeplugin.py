from nose.plugins.base import Plugin
from gaefw.test.tools import gae_logout


class Test(Plugin):
    name = 'gaefw'

    def afterTest(self, test):
        gae_logout()

