# -*- coding:utf8 -*-
# !/usr/bin/env python
from gluon.contrib import simplejson


def botWebhook():
    def POST(*args, **vars):
        logger.error(str(request))
        print(str(request))
        return simplejson.dumps({'speech':"lol"})

    def GET(*args, **vars):
        logger.error(str(request))
        print(str(request))
        return simplejson.dumps({'speech':"lol"})

    logger.warn("request from bot" + str(request))
    return locals()
