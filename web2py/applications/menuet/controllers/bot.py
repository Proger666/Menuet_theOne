# -*- coding:utf8 -*-
# !/usr/bin/env python
from gluon.contrib import simplejson


@request.restful()
def webhook():
    def POST(*args, **vars):
        logger.error(str(request))
        print(str(request))
        return simplejson.dumps({
            "speech": 'lol',
            "displayText": 'nah',
            # "data": data,
            # "contextOut": [],
            "source": "apiai-weather-webhook-sample"
        })

    def GET(*args, **vars):
        logger.error(str(request))
        print(str(request))
        return simplejson.dumps({'speech': "lol"})

    logger.warn("request from bot" + str(request))
    return locals()
