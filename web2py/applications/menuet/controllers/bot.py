# -*- coding:utf8 -*-
# !/usr/bin/env python
from gluon.contrib import simplejson
import re

######## todo: redesign ####
USER_CACHE = {"user_id": 1, "items": []}


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


def weighted_search(query):
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
               (db.t_rest_menu.t_rest == db.t_restaraunt.id) & \
               (db.t_menu_item.t_item == db.t_item.id) & \
               (db.t_menu.f_current == True) & \
               (db.t_item.f_recipe == db.t_recipe.id) & \
               (db.t_ingredient.id == db.t_step.f_ingr) & \
               (db.t_step_ing.t_step == db.t_step.id) & \
               (db.t_step_ing.t_recipe == db.t_recipe.id)

    ## filter records
    # TODO: redesign
    # select_filter = 'db.t_menu.ALL,db.t_item.ALL,db.t_restaraunt.ALL,db.t_ingredient.ALL'
    ###### Find all items by tag
    _tmp = db(db.tag.name == item).select(db.tag.id)
    _tmpA = [x.id for x in _tmp]
    # damn python

    s_tag = db(db.t_item.tags.contains(_tmpA) & subquery).select(distinct=True)
    # form result
    _cur_id = None
    _cur_menu = None
    add_results(_cur_id, _cur_menu, result_list, s_tag, weights.tag)

    # add found id via SET to exclude repeats
    _id = set([x['t_item'].id for x in s_tag])
    [found_items_id.append(x) for x in _id]

    ######## find all items by item
    s_item = db(
        (db.t_item.f_name.like('%' + item + '%')) & (~db.t_item.id.belongs(found_items_id)) & (subquery)).select(
        distinct=True)

    add_results(_cur_id, _cur_menu, result_list, s_item, weights.item)
    [found_items_id.append(x['t_item'].id) for x in s_item]
    ####### find all items by ingrs
    ingrs = find_ingr(search)
    # find all id of ingrs
    ingrs_id = [x.id for x in db(db.t_ingredient.f_name.belongs(ingrs)).select(db.t_ingredient.id)]
    # filter by acive menu and ingrs_id search only once
    s_ingrs = db((subquery) &
                 (db.t_ingredient.id.belongs(ingrs_id)) &
                 (~db.t_item.id.belongs(found_items_id))).select(distinct=True)
    add_results(_cur_id, _cur_menu, result_list, s_ingrs, weights.ingr)

    return jsonpickle.dumps(result_list, unpicklable=False)


def get_food_with_loc(vars):
    if len(vars) < 1:
        logger.error("failed to get food for user, vars not supplied")
        return {}
    # lets get food by ingr
    result = weighted_search(vars.query)
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
        logger.warning(request.vars.token)
        logger.warning(request.vars.get('token'))
        logger.warning(request.vars['token'])
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
