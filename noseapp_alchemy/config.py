# -*- coding: utf-8 -*-


class Config(dict):
    """
    Base config
    """

    def configure(self, **params):
        self.update(params)

    def dns_configure(self, **params):
        self['dns_params'].update(params)
