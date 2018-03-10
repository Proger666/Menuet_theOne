# -*- coding:utf8 -*-
# !/usr/bin/env python

@request.restful()
def botWebhook():
    def POST(*args, **vars):
        logger.error(str(request))
        print(str(request))

    def GET(*args, **vars):
        logger.error(str(request))
        print(str(request))

    logger.warn("request from bot" + str(request))
    return locals()
