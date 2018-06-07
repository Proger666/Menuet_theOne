# -*- coding:utf8 -*-
# !/usr/bin/env python
import datetime
import os
import uuid

import jsonpickle

import pymorphy2
from collections import OrderedDict
import re


##### GLOBAL PARAMETERS ####
class USER:
    MAXDISTANCE = 500


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


def clean_file_cache(user_id):
    start = datetime.datetime.now()
    try:
        path = 'applications/menuet/cache/cache_' + str(user_id)
        # Remove user cache
        os.remove(path)
    except Exception as e:
        logger.error('We failed to clean user cache with ' + str(e) + " " + str(e.message))
    try:
        master_file = 'applications/menuet/cache/cache_master'
        # remove user_id and its cache data from master_file
        # OPen master for read
        f = open(master_file, 'r+')
        # read all lines
        master_cache = simplejson.load(f)
        master_cache = [x for x in master_cache if x['user_id'] != user_id]
        # return to start of the file and rewrite whole file
        # TODO: maybe slow
        f.close()
        f = open(master_file, 'w')
        simplejson.dump(master_cache, f)
        f.close()
    except Exception as e:
        logger.error('We failed to clean master cache with ' + str(e) + " " + str(e.message))
    finally:
        end = datetime.datetime.now() - start
        logger.warning("we finished clean cache in  " + str(end))
    pass


def get_from_cache(user_id, count, query):
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
                path = 'applications/menuet/cache/cache_' + str(user_id)
                if item.get('last_query') != query:
                    clean_file_cache(user_id)
                with open(path, 'r+') as f:
                    cached = simplejson.load(f)
                    r = simplejson.loads(cached['items'])[int(cached['curr_pos']): int(cached['curr_pos']) + count]
                    cached['curr_pos'] += count
                    if len(r) == 0:
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


def get_STD_portion_price_item(item_id):
    _portions = db(db.t_item_prices.f_item == item_id).select(db.t_item_prices.f_price, db.t_item_prices.f_portion)
    if _portions != None:
        # fill array with price and portion name
        for step in _portions:
            # 1 stands for Standard
            if step.f_portion == 1:
                return step.f_price


def search_by_name(query, weight, rest1k, rests_item):
    # search by exact match fast fail if found
    # result obj

    result = []
    exact_match = False
    for item in rests_item:
        item = Storage(item)
        # remove excessive spaces
        # тыквенный суп
        tag_search = [x for x in query.split() if pos(x) in ["NOUN", 'ADJF']][0]
        tag_search = re.compile(tag_search)
        if re.sub(' +', ' ', item.item_name.lower()) == query or tag_search.search(item.item_tags):
            create_result_obj(item, rest1k, result, weight)
            exact_match = True
            break
        if exact_match == True:
            break

        # lets get our noun
        noun = [x for x in query.split() if pos(x) == "NOUN"][0]

        # lets try search word by word until fail
        # lets try search via regex in full string
        compile = re.compile(noun)
        if compile.search(item.item_name.lower().encode('utf-8')) is not None:
            create_result_obj(item, rest1k, result, weight)

    return result


def create_result_obj(item, rest1k, result, weight):
    rest = None
    if item.rest_name is None:
        net_name = db.t_network[item.f_network]
        item.rest_name = "Сеть:" + str(net_name.f_name)
        for key, value in rest1k.iteritems():
            if value['f_network_name'] == net_name.id:
                rest = value
                break
    else:
        rest = rest1k[item.rest_id]

    result.append(result_object(item.item_id, item.item_name,
                                item.rest_id, get_STD_portion_price_item(item.item_id), '0',
                                item.menu_id,
                                weight, rest.get('rest_name'),
                                rest.get('rest_addr', 'Не знаем'), rest.get('distance_in_km', 0),
                                item.get('rest_phone', 'Не знаем'),
                                rest.get('f4sqr') if rest.get(
                                    'f4sqr') is not None else 'https://ru.foursquare.com/v/%D1%88%D0%B8%D0%BA%D0%B0%D1%80%D0%B8/5852d5d10a3d540a0d7aa7a5',
                                get_ingrs_for_item(item.item_id), rest.get('rest_long', '55'),
                                rest.get('rest_lat', '35')))


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
        except UnicodeDecodeError:
            result.append(morph.parse(ingr.decode('utf-8'))[0].normal_form)
    if len(result) > 0:
        return result
    return None


def pos(word, morth=pymorphy2.MorphAnalyzer()):
    try:
        r = morth.parse(word.decode('utf-8'))[0].tag.POS
    except UnicodeDecodeError:
        r = morth.parse(word.encode('utf-8'))[0].tag.POS
    except UnicodeEncodeError:
        r = morth.parse(word)[0].tag.POS
    return r


def search_by_ingr(query, weight, rest1k, rests_item, by_name):
    start = datetime.datetime.now()
    # result will be stored as row
    result_final = by_name

    # lets try to get all ingrs ID from query
    ingrs_id = parse_ingrs_id(query)

    if len(ingrs_id) == 0:
        return result_final

    if len(by_name) == 0:
        # collect all ids from item ids
        items_id = [x['item_id'] for x in rests_item]
        # Lets try to find items by their ingrs
        # we join ALL tables + filter by items that we know and filter them out by ingrs
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
            # create list of ints (ids) from DB response and then create uniq set
            _set_ingr_id = set([int(x) for x in result_id[i][1].split(",")])
            # is set equal to ingrs_id ?
            if _set_ingr_id == set(ingrs_id):
                result_AND.append(item[0])
            i += 1
        # do we get anything with and ? if not return OR ids of items to include
        if len(result_AND) == 0:
            results_id = [x[0] for x in result_id]
        else:
            results_id = result_AND
        # result now is list of item IDs
        # now turn it to ROWS
        for item in rests_item:
            item = Storage(item)
            if item.item_id in results_id:
                create_result_obj(item, rest1k, result_final, weight)
                break

    for item in by_name:
        for ingr in ingrs_id:
            if ingr in item.item_ingrs:
                item.search_score += 1

    result_final = by_name
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
    ingrs = db(db.t_ingredient.id.belongs(_)).select()
    ingrs = [x['id'] for x in ingrs]
    return ingrs


def get_price_for_item(item_id):
    if item_id is None:
        return None
    min_price = db(db.t_item_prices.f_item == item_id).select(db.t_item_prices.f_price.min()).first()
    if min_price != None:
        # TODO: redesign
        price = min_price.values()[0].values()[0]
    return price


def get_rest_for_item(item_id, networks_ids):
    rest_info = db((db.t_item.id == item_id) & (m_t_m_rest_menu) & (m_t_m_menu_item)).select(
        db.t_restaraunt.ALL).first()
    # try to search in networks
    if rest_info is None:
        rest_info = db((db.t_item.id == item_id) & (m_t_m_menu_item)).select(db.t_menu.f_network).first().f_network
        # TODO: REDESIGN
        # resolve network info
        _net_info = db(db.t_network.id == rest_info).select(db.t_network.ALL).first()
        rest_info = {"f_name": _net_info.f_name, "f_address": "Москва"}
        rest_info = Storage(rest_info)
    return rest_info


def create_result(by_ingr, networks_ids, sort):
    start = datetime.datetime.now()
    if len(by_ingr) == 0:
        return []
    resulting_array = []
    def bySearch_key(result_object):
        return result_object.search_score
    resulting_array = sorted(by_ingr, key = bySearch_key, reverse=True)
    try:
        # for element in by_name + by_ingr:
        #     # check if it's duplicate
        #     if element is not None:
        #         if element not in resulting_array:
        #             resulting_array.append(element)
        # for element in by_ingr + by_name:
        #     # check if
        #     if len(element) > 0:
        #         if not is_exist(element, resulting_array):
        #             # fetach rest info for item
        #             _rest = get_rest_for_item(element["item"]["id"], networks_ids)
        #             resulting_array.append({"item": element["item"]["f_name"],
        #                                     "ingrs": ",".join(get_ingrs_for_item(element["item"]["id"])),
        #                                     "cost": get_price_for_item(element["item"]["id"]),
        #                                     "rest_name": _rest.f_name,
        #                                     "rest_addr": _rest.f_address,
        #                                     "weight": element["weight"]})
        # # Let's sort this shit now
        # # create ordered dict to remember dict order
        # od = OrderedDict
        by_ingr = 1
    except AssertionError:
        logger.error("DB ERROR!!!! we failed to create result in create_result, " + str(e) + str(e.message))
    end = datetime.datetime.now() - start
    logger.warning('create_result concluded in ' + str(end))
    return resulting_array


def is_exist(element, resulting_array):
    for x in resulting_array:
        if element['item']['f_name'] == x['item']:
            # break if we have element
            return True
    return False


def write_to_cache(user_id, weighted_result, query):
    # add to cache
    if len(weighted_result) > 0:
        # Create new cache for the results
        file = open('applications/menuet/cache/cache_' + str(user_id), 'w')
        _ = {"user_id": user_id,
             "items": jsonpickle.dumps(weighted_result, unpicklable=False),
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
                     "time": str(datetime.datetime.now()),
                     "last_query": query}
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


def weighted_search(query, lng, lat, user_id, sort):
    start_all = datetime.datetime.now()
    raw_weights = {'ingr': 1, 'item': 2, 'tag': 3}
    # remove escessive spaces from query
    query = re.sub(' +', ' ', query.lower()).encode('utf-8')
    query_id = str(uuid.uuid4()) + ': ' + query
    logger.warning('We got new query: %s', query_id)
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
    try:
        #### Try to calculate location
        ## TODO: redesign
        db.executesql('SET @lat =' + str(lat))
        db.executesql('SET @lng = ' + str(lng))
        rest1k = db.executesql(
            'SELECT t_restaraunt.f_longitude AS rest_long, t_restaraunt.f_latitude AS rest_lat,  t_restaraunt.id AS rest_id, t_restaraunt.f_name AS rest_name, t_restaraunt.f_f4sqr AS f4sqr, t_restaraunt.f_public_phone AS rest_phone, t_restaraunt.f_is_network,t_restaraunt.f_address AS rest_addr,'
            't_restaraunt.f_network_name,(ACOS(COS(RADIANS(@lat))'
            '*COS(RADIANS(t_restaraunt.f_latitude))*COS(RADIANS(t_restaraunt.f_longitude)-RADIANS(@lng))+SIN(RADIANS(@lat))'
            '*SIN(RADIANS(t_restaraunt.f_latitude)))*6371)'
            'AS distance_in_km FROM t_restaraunt GROUP BY distance_in_km HAVING distance_in_km < 5000 LIMIT 10000',
            as_dict=True)
    except:
        # We failed - get long with it
        logger.error("ALARMA! Database error in location calculation")
        rest1k = db(db.t_restaraunt.id > 0).select()

    # Get all menus for this rests
    # u'T' = True for mySQL
    _tmp_nets = set()
    # get ids of networks
    [_tmp_nets.add(x['f_network_name']) for x in rest1k if
     x['f_is_network'] == u'T' or x['f_is_network'] == True and x['f_network_name'] is not None and (x[
                                                                                                         'f_network_name'] != 5 and
                                                                                                     x[
                                                                                                         'f_network_name'] != 6)]

    _tmp_rests_id = [x['rest_id'] for x in rest1k]
    menus = db((db.t_menu.f_current == True)
               & ((db.t_restaraunt.id.belongs(_tmp_rests_id)) & (m_t_m_rest_menu))).select(
        db.t_menu.id)
    menus_id = [x.id for x in menus]
    ## Add menus for networks
    menus_id += [x.id for x in db(db.t_menu.f_network.belongs(_tmp_nets)).select()]

    # TODO:redesign
    rests_item = db.executesql(
        "SELECT t_menu.id AS menu_id, ifnull(t_restaraunt.id,5) AS rest_id,t_restaraunt.f_name AS rest_name,"
        "t_restaraunt.f_address AS rest_address,t_item.id AS item_id,t_item.f_tags AS item_tags,t_item.f_name AS item_name, "
        "t_menu.f_network FROM t_item "
        "left OUTER JOIN t_menu_item ON t_item.id = t_menu_item.t_item "
        "left OUTER JOIN t_menu ON t_menu_item.t_menu = t_menu.id "
        "left OUTER JOIN t_rest_menu ON t_menu.id = t_rest_menu.t_menu "
        "left OUTER JOIN t_restaraunt ON t_restaraunt.id = t_rest_menu.t_rest "
        "where t_restaraunt.id IN(" + ', '.join(str(x) for x in _tmp_rests_id) + ") OR t_restaraunt.id IS NULL",
        as_dict=True)

    ############
    # we expect ROW object
    start = datetime.datetime.now()
    # lets create cache in order to lower SQL queries
    internal_cache = internalSearchCache()

    # lets reformat dictionary to add ID
    _f_rest1k = {}
    for item in rest1k:
        _f_rest1k[item.get('rest_id', 0)] = item

    # we expect RESULT object
    by_name = search_by_name(query, raw_weights['item'], _f_rest1k, rests_item)
    end = datetime.datetime.now() - start
    logger.warning("We got %s results by name in %s, for query: %s", len(by_name), str(end), query_id)
    # we expect RESULT object
    start = datetime.datetime.now()
    by_ingr = search_by_ingr(query, raw_weights['ingr'], _f_rest1k, rests_item, by_name)
    end = datetime.datetime.now() - start
    logger.warning("We got %s results by ingr in %s, for query: %s", len(by_ingr), str(end), query_id)
    # by_tag = search_by_tag(items, query, raw_weights['tag'])
    weighted_result = create_result(by_ingr, _tmp_nets, sort)
    end_all = datetime.datetime.now() - start_all
    logger.warning("We got %s results in our search in %s, for query: %s", len(weighted_result), str(end), query_id)
    return weighted_result


def get_food_with_loc(vars):
    if len(vars) < 1:
        logger.error("failed to get food for user, vars not supplied")
        return {}
    if not checkIfExist(vars.query):
        logger.error("query is empty :(")
        return api_error("Query is empty")
    if not checkIfExist(vars.loc_lng, vars.loc_lat):
        logger.error("Locations is not present")
        return api_error("Locations is missing")
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
    result = get_from_cache(vars.user_id, count, vars.query)
    if result['msg'] == 'ok':
        # return data from cache
        return result
    elif result['msg'] == 'no more':
        return result
    elif result['msg'] == 'none':
        # run new search
        weighted_result = weighted_search(vars.query, vars.loc_lng, vars.loc_lat, vars.user_id, vars.sort)
        # write result to cache
        write_to_cache(vars.user_id, weighted_result, vars.query)
        # give control to cache
        result = get_from_cache(vars.user_id, count, vars.query)
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
