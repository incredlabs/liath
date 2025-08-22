import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from liath.plugin_base import PluginBase

class DBPlugin(PluginBase):
    @property
    def name(self):
        return "db"

    def initialize(self, context):
        self.db = context['db']
        self.namespace = context['namespace']

    def get_lua_interface(self):
        return {
            'db': self.db
        }