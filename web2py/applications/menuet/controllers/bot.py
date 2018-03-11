# -*- coding:utf8 -*-
# !/usr/bin/env python
from gluon.contrib import simplejson
import re

def get_user_location_google(text):
    if text == None:
        logger.error('faled to fullfill user location - parameter is empty ' + logUser_and_request())
    return re.search('\d+\.\d+\,\d+\.\d+',text).group(0)



def get_user_info(userQuery):
    # fast fail if empty req
    if len(userQuery) <1:
        logger.error("Fullfilment failed for bot request" + logUser_and_request())
    # lets get current user context
    userInfo = userQuery['payload']['data']['message']['chat']
    userInfo = Storage(userInfo)
    # apple location parsing
    user_last_loc = get_user_location_google(userQuery['payload']['data']['message']['text'])

    user_name = userInfo.username
    user_id = userInfo.id
    user_context = db(db.t_bot_user_context.f_user_id == user_id).select().first()
    user_f_name = userInfo.first_name
    user_l_name = userInfo.last_name
    if user_context == None:
        new_user = db.bot_user_context.insert(f_username=user_name,f_user_id=user_id,f_first_name=user_f_name,f_last_name=user_l_name,f_last_loc=user_last_loc)
        db.commit()


    userContext = {'userName': user_name,
                   'user_id':user_id,
                   'user_last_location': user_last_loc}

    return userContext


@request.restful()
def webhook():
    def POST(*args, **vars):
        logger.error(str(request))
        print(str(request))
        user_context = get_user_info(request.vars.originalDetectIntentRequest)
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
