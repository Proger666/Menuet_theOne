# -*- coding:utf8 -*-
# !/usr/bin/env python
import datetime
from gluon.contrib import simplejson
import re

######## todo: redesign ####
USER_CACHE = [{"user_id": 1, "items": [], 'time': datetime.datetime.now()}]


def check_token(token):
    MENUET_TOKEN = "ya29.c.El97BacMtcOVmFuQGwApUY-EikgCG8YtGI2C6oAt73Gd9AsHFBntwabQElx-9ZIQJSRvIBprUaRqDvHo2JHZCOTW8Z80u2FH8k9XlsL1Lqeg"
    if token == MENUET_TOKEN:
        return True
    else:
        logger.warning(
            "TOKEN IS :" + token if token is not None else "no token supplied" + "\n Menuet token is " + MENUET_TOKEN)
        return False


def save_user_loc_to_db(request):
    logger.warning("request to save user loc " + str(request))
    db.t_bot_user_context.update_or_insert(f_user_id=request.user_id, f_username=request.username,
                                           f_last_loc=request.location, f_first_name=request.user_first_name)
    pass


def get_from_cache(user):
    for item in USER_CACHE:
        if item['user_id'] == user.id:
            a = item['items'][:3]
            del item['items'][:3]
            return a
    pass
    return {}


def weighted_search(query, loc,user_id):
    result_list = []
    raw_weights = {'tag': 3, 'ingr': 1, 'item': 2}
    weights = Storage(raw_weights)
    found_items_id = []
    # result format
    results = {'item': []}
    # Structure
    #     {'item': [
    #     {'record': 'record',
    #      'weight': 'weight'}
    #     ]}

    # make it simplier to use
    results = Storage(results)

    # View of m-m-relations
    subquery = (db.t_rest_menu.t_menu == db.t_menu.id) & \
               (db.t_rest_menu.t_rest == db.t_restaraunt.id)
               # (db.t_menu_item.t_item == db.t_item.id) & \
               # (db.t_menu.f_current == True) & \
               # (db.t_item.f_recipe == db.t_recipe.id) & \
               # (db.t_ingredient.id == db.t_step.f_ingr) & \
               # (db.t_step_ing.t_step == db.t_step.id) & \
               # (db.t_step_ing.t_recipe == db.t_recipe.id)
    ############################################################################
    ##################### CREATE LOCATION SLICE ################################
    ##### Search by location
    rest1k = [1,7]
    ############
    ### create slice
    slice = db(db.t_restaraunt.id.belongs(rest1k) & subquery).select()
    ############################################################################



    ############### Search by Name ######################


    #Dump tp cache
    cached = False
    # add to cache
    USER_CACHE.append(
        {'user_id':user_id,
         'items': result_list,
         'time': datetime.datetime.now()}
    )
    cached = True

    # should return status rathen then actual result
    if len(result_list) > 0 and cached:
        return True
    return False


def api_error(msg):
    return {'status':'error',"msg":msg}
def api_success(msg):
    return {'status':'OK', 'msg':msg}

def get_food_with_loc(vars):
    if len(vars) < 1:
        logger.error("failed to get food for user, vars not supplied")
        return {}
    if vars.query is None or vars.query == "":
        logger.error("query is empty :(")
        return api_error("Query is empty")
    # lets get food WITH WEIGHTS
    # query = food
    # From proxy we expet to receive:
    # payload = {'action': 'get_food_loc', 'token': MENUET_TOKEN,
    #            'user_id': update.message.from_user.id,
    #            'query': food,
    #            "location": user_location}
    result = weighted_search(vars.query, Storage(vars.location), vars.user_id)
    if result:
        # return data from cache
        return get_from_cache(vars.user_id)
    else:
        return False
    pass


@request.restful()
def api():
    def POST(*args, **vars):
        logger.debug("We got request with vars:\n " + str(request.vars))
        token = request.vars.get('token')
        if not check_token(token):
            logger.warning("ALARM! Some one using API !!!! " + str(request))
            return {'status': 'error', 'verify': 'failed'}
        if request.vars.get('action') == 'save_user_loc':
            save_user_loc_to_db(request.vars)
        elif request.vars.get('action') == 'get_food_loc':
            return get_food_with_loc(request.vars)

    return locals()


def get_user_location_google(text):
    if text == None:
        logger.error('faled to fullfill user location - parameter is empty ' + logUser_and_request())
    return re.search('\d+\.\d+\,\d+\.\d+', text).group(0)


def get_user_info(userQuery, ll):
    # fast fail if empty req
    if userQuery == None:
        logger.error("Fullfilment failed for bot request")
    # lets get current user context
    userInfo = userQuery['payload']['data']['message']['chat']
    userInfo = Storage(userInfo)
    # apple location parsing
    user_last_loc = ll  # get_user_location_google(userQuery['payload']['data']['message']['text'])

    user_name = userInfo.username
    user_id = userInfo.id
    user_context = db(db.t_bot_user_context.f_user_id == user_id).select().first()
    user_f_name = userInfo.first_name
    user_l_name = userInfo.last_name
    if user_context == None:
        new_user = db.t_bot_user_context.insert(f_username=user_name, f_user_id=user_id, f_first_name=user_f_name,
                                                f_last_name=user_l_name, f_last_loc=user_last_loc)
    else:
        db(db.t_bot_user_context.id == user_context.id).update(f_last_loc=user_last_loc)
    db.commit()

    userContext = {'userName': user_name,
                   'user_id': user_id,
                   'user_last_location': user_last_loc}

    return userContext


@request.restful()
def webhook():
    def POST(*args, **vars):
        logger.error('request is ' + str(request.vars))
        user_context = get_user_info(request.vars.t['request.vars.originalDetectIntentRequest'], request.vars.ll)
        return simplejson.dumps(user_context)

    logger.warn("request from bot" + str(request))
    return locals()
