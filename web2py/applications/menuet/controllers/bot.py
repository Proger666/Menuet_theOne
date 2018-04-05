# -*- coding:utf8 -*-
# !/usr/bin/env python
import datetime
import uuid

import pymorphy2

import re

######## todo: redesign ####

# View of m-m-relations
from gluon.contrib import simplejson
from gluon.contrib.simplejson import JSONDecodeError

m_t_m_rest_menu = \
    ((db.t_rest_menu.t_menu == db.t_menu.id) &
     (db.t_rest_menu.t_rest == db.t_restaraunt.id))
m_t_m_menu_item = \
    ((db.t_menu_item.t_item == db.t_item.id) &
     (db.t_menu_item.t_menu == db.t_menu.id))


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


def get_from_cache(user_id, count):
    try:
        master_file = open('applications/menuet/cache/cache_master', 'r+')
    except IOError:
        master_file = open('applications/menuet/cache/cache_master', 'wb')
        master_file.close()
        master_file = open('applications/menuet/cache/cache_master', 'r+')
    try:
        cache_items = simplejson.loads(master_file.read())
    except JSONDecodeError:
        return {'msg': 'none'}
    except Exception as e:
        logger.error("we broke cache" + str(e) + str(e.message))
        return {'msg': 'none'}
    if len(cache_items) == 0:
        return {'msg': 'none'}

    try:
        for item in cache_items:
            # find requested data for user by id
            if item['user_id'] == user_id:
                # if we found record - do we have data ?
                path = 'applications/menuet/cache/cache_' + user_id
                with open(path, 'r+') as f:
                    cached = simplejson.load(f)
                    r = simplejson.loads(cached['items'])[int(cached['curr_pos'])::]
                    cached['curr_pos'] += count
                    if len(r) == 0:
                        import os
                        f.close()
                        os.remove(path)
                        return {'msg': 'no more'}
                    else:
                        f.seek(0)
                        simplejson.dump(cached, f)
                        return {'msg': 'ok', 'items': r}
    except Exception as e:
        # TODO:re design
        logger.error('we failed to fetch from cache with ' + str(e.message) + str(e))
        return {'msg': 'none'}
    return {'msg': 'none'}


def search_by_name(items, query, weight):
    # search by exact match fast fail if found
    # result obj
    query = query.encode('utf-8')
    result = [{}]

    for item in items:
        if item.f_name == query:
            result.append({'item': item, 'weight': weight})

            break
    if len(result) == 1:
        # lets try search word by word until fail
        # strip by words
        words = query.split(" ")
        i = len(words)
        start = datetime.datetime.now()
        while len(result) == 1 and i > 1:
            # search for string and cut string's tail each time until last word
            sub_query = " ".join(words[:i])
            for item in items:
                if item.f_name.startswith(sub_query):
                    result.append({'item': item, 'weight': weight})
                    break
            i -= 1
        end = datetime.datetime.now() - start
        return result
    return None


def query_cleanUp(query):
    # encode to utf-8
    query = query.encode('utf-8')
    return query


def normalize_words(ingrs_list):
    # Do we have ingrs list ?
    if len(ingrs_list) == 0:
        return None
    morph = pymorphy2.MorphAnalyzer()
    result = []
    for ingr in ingrs_list:
        # lets get normal form of the word
        try:
            # bad design of library it will send exception if it doesnt know word
            result.append(morph.parse(ingr)[0].normal_form)
        except AttributeError:
            result.append(ingr)
    if len(result) > 0:
        return result
    return None


def pos(word, morth=pymorphy2.MorphAnalyzer()):
    return morth.parse(word)[0].tag.POS


def search_by_ingr(items, query, weight):
    start = datetime.datetime.now()
    # result will be stored as row
    result_final = [{}]
    # try search word by word
    # strip by words
    # delete all trash
    # remove all adjectives https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html
    functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP', 'ADJF'}  # function words from Pymorphy2
    _query_list = query.split()
    ingrs = [word for word in _query_list if pos(word) not in functors_pos]
    # now lets normalize everything
    ingrs_normal = normalize_words(ingrs)

    # Now lets find INGRS id if we have such by their normal form
    # TODO: redesign set search
    ingrs_id = [x.id for x in db(db.t_ingredient.f_normal_form.belongs(ingrs_normal)).select()]
    # if we dont have ingrs in DB = sorry
    if len(ingrs_id) == 0:
        return None

    items_id = [x.id for x in items]
    # Lets try to find items by their ingrs
    # we join ALL tables + filter by items that we know and  filter them out by ingrs
    # SEARCH BY IN thats OR search
    result_id = db.executesql(
        'SELECT itm.id, group_concat(concat(rc_ingr.ingr))'
        ' FROM(SELECT rc.id, t_ingredient.id AS ingr'
        ' FROM t_ingredient'
        ' INNER JOIN t_step ON t_step.f_ingr = t_ingredient.id'
        ' INNER JOIN t_step_ing si ON si.t_step = t_step.id'
        ' INNER JOIN t_recipe rc ON si.t_recipe = rc.id'
        ' WHERE t_ingredient.id IN (' + ",".join(
            str(x) for x in ingrs_id) + ')) AS rc_ingr JOIN (SELECT * FROM t_item WHERE t_item.id IN(' + ",".join(
            str(x) for x in items_id) + ')) AS itm ON itm.f_recipe=rc_ingr.id'
                                        ' GROUP BY itm.id'
                                        ' ORDER BY itm.id')

    # Lets try search by AND in results
    result_AND = []
    # 0 is ITEM 1 is INGR
    i = 0
    # RESULT WILL BE ITEM ID!!!
    for item in result_id:
        # create list of ints from DB response and then create uniq set
        _set_ingr_id = set([int(x) for x in result_id[i][1].split()])
        # is set equal to ingrs_id ?
        if _set_ingr_id == set(ingrs_id):
            result_AND.append(item[0])
        i += 1
    # do we get anything with and ? if not return OR
    if len(result_AND) == 0:
        result = [x[0] for x in result_id]
    else:
        result = result_AND
    # result now is list of item IDs
    # now turn it to ROWS
    [result_final.append({'item': x, 'weight': weight}) for x in items if x.id in result]
    end = datetime.datetime.now() - start
    logger.warning('search by ingr concluded in ' + str(end))
    return result_final


# TODO: optimize too slow
def get_ingrs_for_item(item_id):
    # get recipe for item to use later on
    item_recipe = db.t_item.f_recipe
    # get step
    step = db(db.t_step.id == db.t_ingredient.id).select()
    # Get recipe ID for given item
    recipe_id = db((db.t_recipe.id == db.t_item.f_recipe)
                   & (db.t_item.id == item_id)).select()[0].t_recipe.id
    # Get m-t-m relation - get all steps for given recipe id
    steps_ing = db((db.t_recipe.id == recipe_id) &
                   (db.t_step.id == db.t_step_ing.t_step) &
                   (db.t_recipe.id == db.t_step_ing.t_recipe))
    # Create list of ingrs
    # create ingrs storage class
    # get all ingrs
    _ = steps_ing.select()
    # get ingrs id
    _ = [x.t_step.f_ingr for x in _]
    # get all ingrs name
    ingrs = db(db.t_ingredient.id.belongs(_)).select(db.t_ingredient.f_name)
    ingrs = [x['f_name'] for x in ingrs]
    return ingrs


def get_price_for_item(item_id):
    if item_id is None:
        return None
    min_price = db(db.t_item_prices.f_item == item_id).select(db.t_item_prices.f_price.min()).first()
    if min_price != None:
        # TODO: redesign
        price = min_price.values()[0].values()[0]
    return price


def create_result(by_name, by_ingr):
    start = datetime.datetime.now()
    if len(by_name) == 1 or len(by_ingr) == 1:
        return []
    resulting_array = []
    for element in by_ingr + by_name:
        # check if
        if len(element) > 0:
            if not is_exist(element, resulting_array):
                resulting_array.append({"item": element["item"]["f_name"],
                                        "ingrs": ",".join(get_ingrs_for_item(element["item"]["id"])),
                                        "cost": get_price_for_item(element["item"]["id"]),
                                        "weight": element["weight"]})
    end = datetime.datetime.now() - start
    logger.warning('create_result concluded in ' + str(end))
    return resulting_array


def is_exist(element, resulting_array):
    for x in resulting_array:
        if element['item']['f_name'] == x['item']:
            # break if we have element
            return True
    return False


def write_to_cache(user_id, weighted_result):
    # add to cache
    if len(weighted_result) > 0:
        # Create new cache for the results
        file = open('applications/menuet/cache/cache_' + user_id, 'wb')
        _ = {"user_id": user_id,
             "items": simplejson.dumps(weighted_result),
             "curr_pos": 0}
        # dumps this results
        simplejson.dump(_, file)
        file.close()
        import os
        # do we have master cache?
        if os.path.isfile('applications/menuet/cache/cache_master'):
            # create with list if doesnt have master file
            with open('applications/menuet/cache/cache_master', 'w') as master_file:
                simplejson.dump([], master_file)

        # populate master with info about new created cache
        with open('applications/menuet/cache/cache_master', mode='r+') as feedsjson:
            feedsjson.seek(0)
            entry = {"user_id": user_id,
                     "time": str(datetime.datetime.now())}
            try:
                feeds = simplejson.load(feedsjson)
            except Exception as e:
                logger.error("something broken in cache creation " + str(e) + str(e.message))
                feeds = []
            feeds.append(entry)
            feedsjson.seek(0)
            simplejson.dump(feeds, feedsjson)
            return True
    return None


def weighted_search(query, loc, user_id):
    raw_weights = {'ingr': 1, 'item': 2}
    # result format
    # Structure
    #     {'item': [
    #     {'record': 'record',
    #      'weight': 'weight'}
    #     ]}

    # (db.t_item.f_recipe == db.t_recipe.id) & \
    # (db.t_ingredient.id == db.t_step.f_ingr) & \
    # (db.t_step_ing.t_step == db.t_step.id) & \
    # (db.t_step_ing.t_recipe == db.t_recipe.id)
    ############################################################################
    ##################### CREATE LOCATION SLICE ################################
    ##### Search by location
    # ROWS of rests
    rest1k = db.executesql('SET @lat =' + str(loc['latitude']))
    rest1k = db.executesql('SET @lng = ' + str(loc["longitude"]))
    rest1k = db.executesql('SELECT t_restaraunt.id,t_restaraunt.f_is_network,'
                           't_restaraunt.f_network_name,(ACOS(COS(RADIANS(@lat))'
                           '*COS(RADIANS(t_restaraunt.f_latitude))*COS(RADIANS(t_restaraunt.f_longitude)-RADIANS(@lng))+SIN(RADIANS(@lat))'
                           '*SIN(RADIANS(t_restaraunt.f_latitude)))*6371)'
                           'AS distance_in_km FROM t_restaraunt GROUP BY distance_in_km HAVING distance_in_km < 5000 LIMIT 10000',
                           as_dict=True)

    # Get all menus for this rests
    # u'T' = True for mySQL
    _tmp_nets = set()
    # get ids of networks
    [_tmp_nets.add(x['f_network_name']) for x in rest1k if
     x['f_is_network'] == u'T' and x['f_network_name'] is not None and x['f_network_name'] != 5]
    _tmp_rests_id = [x['id'] for x in rest1k]
    menus = db((db.t_menu.f_current == True) & (
            (db.t_restaraunt.id.belongs(_tmp_rests_id)) | (db.t_menu.f_network.belongs(_tmp_nets))) & (
                   m_t_m_rest_menu)).select(
        db.t_menu.id)

    menus_id = [x.id for x in menus]
    ## Add menus for networks
    menus_id += [x.id for x in db(db.t_menu.f_network.belongs(_tmp_nets)).select()]

    items = db((db.t_menu.id.belongs(menus_id)) & (m_t_m_menu_item)).select(db.t_item.ALL)
    ############
    # we expect ROW object
    start = datetime.datetime.now()
    by_name = search_by_name(items, query, raw_weights['item'])
    end = datetime.datetime.now() - start
    logger.warning('by name search concluded in ' + str(end))
    # we expect ROW object
    by_ingr = search_by_ingr(items, query, raw_weights['ingr'])

    weighted_result = create_result(by_name, by_ingr)
    end = datetime.datetime.now() - start
    logger.warning('Weighted search concluded in ' + str(end))
    return weighted_result


def api_error(msg):
    return {'status': 'error', "msg": msg}


def api_success(msg):
    return {'status': 'OK', 'msg': msg}


def get_food_with_loc(vars):
    if len(vars) < 1:
        logger.error("failed to get food for user, vars not supplied")
        return {}
    if vars.query is None or vars.query == "":
        logger.error("query is empty :(")
        return api_error("Query is empty")
    # lets get food WITH WEIGHTS
    # query = food
    # From proxy we expect to receive:
    # payload = {'action': 'get_food_loc', 'token': MENUET_TOKEN,
    #            'user_id': update.message.from_user.id,
    #            'query': food,
    #            "location": user_location}
    # Check cache - do we have anything ?
    # if yes - show some
    # if not - new search
    # if nothing - sorry
    count = 3
    result = get_from_cache(vars.user_id, count)
    if result['msg'] == 'ok':
        # return data from cache
        return result
    elif result['msg'] == 'no more':
        return result['msg']
    elif result['msg'] == 'none':
        # run new search
        weighted_result = weighted_search(vars.query, simplejson.loads(vars.location), vars.user_id)
        # write result to cache
        write_to_cache(vars.user_id, weighted_result)
        # give control to cache
        result = get_from_cache(vars.user_id, count)
        if result['msg'] == 'ok':
            return result

    return []


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
