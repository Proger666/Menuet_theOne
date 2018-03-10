# -*- coding:utf8 -*-
# !/usr/bin/env python

@request.restful()
def botWebhook():
    logger.warn("request from bot" + str(request))
    return locals()
