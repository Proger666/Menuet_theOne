# -*- coding: utf-8 -*-
### required - do no delete
from __future__ import print_function

import concurrent.futures

from time import gmtime, strftime

import requests

from gluon.contrib import simplejson

### GLOBALS

APIKEY = "5Db[fJeUsssssA(N[+b~P"


def user():
    if request.args(0) == 'register':
        request.vars.username = request.vars.email

    return dict(form=auth())


def download(): return response.download(request, db)


def link(): return response.download(request, db, attachment=False)


def call(): return service()


def download_url(url):
    r = requests.get(url, stream=True, verify=False)
    with open(url, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return url


def jsn_menu():
    if 'file' in request.vars:

        with concurrent.futures.ProcessPoolExecutor() as executor:
            jsn_obj = simplejson.loads(file.read(request.vars.file.file.file))
            for item in jsn_obj:
                executor.map(commit_to_db(item))
    return locals()


def commit_to_db(item):
    # get value or NONE if not exst
    _name = item.get('Name')
    _f_type = item.get('TypeObject')
    _f_coordinateX = item['geoData'].get('coordinates')[0] if item.get('geoData') else None
    _f_coordinateY = item['geoData'].get('coordinates')[1] if item.get('geoData') else None
    _f_address = item.get('Address')
    _f_long = item.get('Longitude_WGS84')
    _f_lat = item.get('Latitude_WGS84')
    _f_q_id = item.get('global_id')
    _b = u'нет'
    if item['IsNetObject'] == _b:
        net = False
    else:
        net = True

        # get hash for unique record
    db.t_restaraunt.insert(f_q_id=_f_q_id, f_name=_name, f_is_network=net, f_type=_f_type, f_active=True,
                           f_coordinateX=_f_coordinateX, f_coordinateY=_f_coordinateY, f_town=u'Moscow',
                           f_address=_f_address, f_latitude=_f_lat,
                           f_longitude=_f_long)
    db.commit()


def delete_menu():
    try:
        db(db.t_menu.id == request.vars.menu['id']).delete()
    except:
        return ajax_error()
    return ajax_success()


def delete_rest():
    try:
        db(db.t_restaraunt.id == request.vars.rest['id']).delete()
    except:
        return ajax_error()
    return ajax_success()


def load_menu():
    return locals()


def ajax_success():
    session.flash = T("Success!")
    response.flash = T("Success!")
    return simplejson.dumps("{'status':'OK'}")


def ajax_error():
    session.flashT("FAILURE!")
    return {}


def delete_course():
    try:
        db(db.t_item.id == request.vars.item['id']).delete()
    except:
        return ajax_error()
    return ajax_success()


def check_api(key):
    if key == APIKEY:
        return True
    else:
        return False


def search_db_item(search):
    item = search.split()[0]
    result = weighted_search(search, item)
    return result


@auth.requires_login()
@request.restful()
def api():
    if not check_api(request.vars.apikey):
        # TODO : redisign logging system
        logger.warn(strftime("%Y-%m-%d %H:%M:%S",
                             gmtime()) + ' Forbidden arised for ' + request.client + ' request is ' + request.url + ' and api key is ' + (
                        'None' if request.vars.apikey is None else request.vars.apikey))
        raise HTTP(403, "Forbidden")
    response.view = 'generic.' + request.extension

    def GET(*args, **vars):

        # TODO: redisign Make dict name callable
        jsn_as_dict = Storage(simplejson.loads(vars['jsn']))
        if jsn_as_dict.search is not '':
            result = search_db_item(jsn_as_dict.search)
            return dict(result=result)
        patterns = 'auto'
        parser = db.parse_as_rest(patterns, args, vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status, parser.error)

    def POST(table_name, **vars):

        return db[table_name].validate_and_insert(**vars)

    def PUT(table_name, record_id, **vars):
        return db(db[table_name]._id == record_id).update(**vars)

    def DELETE(table_name, record_id):
        return db(db[table_name]._id == record_id).delete()

    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)


def we():
    return locals()


@auth.requires_membership('Admin')
def reset_lock():
    result = {'user': request.vars.user, 'status': 'ERR'}

    try:
        rows = db(db.t_restaraunt.modified_by == request.vars.user['id']).select()
        if len(rows) == 0:
            response.flash = session.flash = T('Failure = USER HAS NO LOCKS')
            logger.warn('reset_lock failed for user ' + str(request.vars.user) + ' by ' + auth.user.username)
            return ajax_error()
        for row in rows:
            row.update_record(modified_by=None)
            session.flash = T('Success')
            result = {'user': request.vars.user, 'status': 'OK'}
            db.commit()
            return simplejson.dumps(result)
    except:
        session.flash = T('Failure = EMPTY USER NAME')
        logger.warn('reset_lock failed for user ' + request.vars.user + ' by ' + auth.user.username)
        return ajax_error()
    return ajax_error()


@auth.requires_membership('Admin')
def index():
    if "rst_all" in request.vars:
        rows = db(db.t_restaraunt).select()
        for r in rows:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                executor.map(r.update_record(modified_by=None))
    if "username" in request.vars:
        if len(request.vars.username) > 0:
            found_users = db(db.auth_user.username.contains(request.vars.username)).select()

            return locals()
    else:
        username = None
        found_users = None
    username = None
    return locals()


@auth.requires_membership('Admin')
def users_m():
    form = SQLFORM.smartgrid(db.auth_user, onupdate=auth.archive)

    return locals()


@auth.requires_login()
### end requires
def rest_menu():
    rest_name = request.vars.rest_name
    rest_id = db(db.t_restaraunt.f_name.contains(rest_name)).select(db.t_restaraunt.id)[0].id
    tmp = db(
        (db.t_menu.id == db.t_rest_menu.t_menu) & (db.t_restaraunt.id == db.t_rest_menu.t_rest)
    )
    menu = [menux.t_menu for menux in tmp(db.t_restaraunt.id == rest_id).select()]
    return locals()


def menu_edit():
    menu_id = db(db.t_menu.f_name.contains(menu_name)).select(db.t_menu.id)[0].id
    tmp = db(
        (db.t_item.id == db.t_menu_item.t_item) & (db.t_menu.id == db.t_menu_item.t_menu) & (db.t_menu.id == menu_id))
    courses = [item.t_item for item in tmp.select()]
    options = db(db.t_unit).select(db.t_unit.ALL)
    options = [x for x in options]
    ingrs = []
    tags = db(db.tag).select(db.tag.ALL)

    return locals()


################# Saving to DB ###################
def save_course():
    try:
        # TODO: make sanity checks on save = what if ingr already exists (sum ingrs) ? What if misspeled (google search) ? What if weight greater than course weight ?
        change_factor = request.vars.course['change_factor']

        # create new records
        class commit_object(object):
            def __init__(self, **kwargs):
                # define default attributes
                default_attr = dict(unit_id=0)
                # define (additional) allowed attributes with no default value
                more_allowed_attr = ['ingr_id']
                allowed_attr = list(default_attr.keys()) + more_allowed_attr
                default_attr.update(kwargs)
                self.__dict__.update((k, v) for k, v in default_attr.iteritems() if k in allowed_attr)

        # Create tmp object to commit to db later on after fullfilment
        _tmp_obj = commit_object()
        # add recipe ID TODO: make multiple recipe per plate

        if change_factor == 'add':

            # Create new recipe
            _tmp_obj.recipe_id = db.t_recipe.insert(f_name=request.vars.course['name'] + '_recipe')
            # Create new Item
            _tmp_obj.item_id = db.t_item.insert(f_name=request.vars.course['name'],
                                                f_weight=request.vars.course['weight'],
                                                f_price=request.vars.course['price'],
                                                f_unit=request.vars.course['unit_id'], f_recipe=_tmp_obj.recipe_id)
            _tmp_obj.item_unit_id = request.vars.course['unit_id']
            _tmp_obj._new_menu_item_id = db.t_menu_item.insert(t_menu=request.vars.course['menu_id'],
                                                               t_item=_tmp_obj.item_id)
        else:
            _tmp_obj.recipe_id = int(request.vars.course['recipe_id'])

            ####################### INGREDIENTS #####################################
        # use shrotcut for check in db for presense of ingr
        for i in range(0, len(request.vars.ingr)):
            # sanity check
            assert str(request.vars.ingr[i]['name']) is not ''
            assert str(request.vars.ingr[i]['unit']) is not ''

            # parse units
            _tmp_obj.unit_id = db(db.t_unit.f_name.contains(request.vars.ingr[i]['unit'])).select(
                db.t_unit.id).first().id

            # remove requested ingrs
            if 'deleted' in request.vars.ingr[i]:
                if request.vars.ingr[i]['deleted'] == 1:
                    db(db.t_step.id == request.vars.ingr[i]['step_id']).delete()
            else:
                # commit all new ingrs
                # do we have ingr in DB ?
                if db.t_ingredient(f_name=request.vars.ingr[i]['name']) is None:
                    _tmp_obj.ingr_id = db.t_ingredient.update_or_insert(f_name=request.vars.ingr[i]['name'])

                else:
                    _tmp_obj.ingr_id = db.t_ingredient(f_name=request.vars.ingr[i]['name']).id
                # Create new step
                _tmp = None
                try:
                    _tmp = int(request.vars.ingr[i]['weight'])
                except ValueError:
                    _tmp = 0
                _tmp_obj._new_step_id = db.t_step.update_or_insert(f_qty=_tmp, f_unit=_tmp_obj.unit_id,
                                                                   f_ingr=_tmp_obj.ingr_id)
                _tmp_obj._t_step_ing_new_id = \
                    db.t_step_ing.update_or_insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)
                db.commit()
    except AssertionError:
        return ajax_error()
    return ajax_success()


@auth.requires_login()
def save_rest():
    try:
        rest_name = request.vars.rest['name']
        rest_addr = request.vars.rest['addr']
        rest_id = request.vars.rest.get('r_id')
        rest_town = request.vars.rest.get('town')
        _rst_net = request.vars.rest.get('network')
        rest_is_network = request.vars.rest['is_network']

        if _rst_net != u'None' and _rst_net != None:
            rest_network = _rst_net.encode('utf-8') if str.isdigit(_rst_net.encode('utf-8')) else 5

        else:
            rest_network = 5
        if rest_is_network and rest_network == 5:
            session.flash = ("Сеть не указана!")
            return {}
        if rest_town == None:
            logger.warn('save_Rest failed, town not on request. for user ' + auth.user.username + " request was " + str(
                request))
            return ajax_error()
        if rest_id != u'None' and rest_id != None:
            rest_id = int(request.vars.rest['r_id'])
        # just create menu TODO: redesign
        # Check if rest already exists
        rest = db(db.t_restaraunt.f_name.like(rest_name)).select().first()
        if rest is None:
            # create new rest if nothing found
            if int(rest_network):
                db.t_restaraunt.insert(f_name=rest_name, f_active=True, f_is_network=rest_is_network,
                                       f_address=rest_addr,
                                       f_town=rest_town, f_network_name=rest_network)
                db.commit()
                return ajax_success()
            else:
                logger.error("save_Rest failure!!! rest_network doesnt filled as number!!!" + logUser_and_request())
                return ajax_error()
        elif rest != None:
            # UPDATE existing rest
            db(db.t_restaraunt.id == rest_id).update(f_name=rest_name, f_active=True, f_is_network=rest_is_network,
                                                     f_address=rest_addr, f_town=rest_town, f_network_name=rest_network)
            db.commit()
            return ajax_success()

        else:
            session.flash = T('Ресторан с таким именем уже существует')
            logger.warn('User:' + auth.user.username + " tried create existing rest " + " request was " + str(request))
            return ajax_success()

    except:
        session.flash = T('FAILURE!!!! Exception')
        logger.warn('Problem in save_rest - Exception occurred' + str(
            Exception.message) + ' for user ' + auth.user.username + " request was " + str(request))
    return ajax_error()


@auth.requires_login()
def save_menu():
    try:

        menu_type = int(request.vars.menu['type'])
        menu_name = request.vars.menu.get('name')
        if menu_name is None and menu_type != 3:
            logger.error(
                'Exception happened in save_menu for user ' + auth.user.username + " request was " + str(request))
            session.flash = "Ошибка - Имя меню не задано"
            return ajax_error()
        else:
            menu_name = menu_name.encode('utf-8')

        rest_id = request.vars.rest['id']
        comment = '' if request.vars.menu.get('comment') == u'None' else request.vars.menu['comment']
        # just create menu TODO: redesign
        # Check if Menu already exists for this rest by name and type

        #  create new menu and set it to active
        if request.vars.rest['is_network']:
            network = db.t_network[request.vars.rest['network_id']]
            if network == None:
                session.flash = "Ошибка! Не задана сеть."
                logger.error(
                    "Someone messed with the network menu creation. user is " + auth.user.username + " request was " + str(
                        request))
                return {}
            # Lets find old menu and make it inactive
            # Find all active menus with given type
            _old_menu = db((db.t_menu.f_network == network.id) &
                           (db.t_menu.f_type.belongs(request.vars.menu['type']))).select()
            for item in _old_menu:
                item.f_current = False
                item.update_record()
            # Get Menu type name and fill menu namu for DB savings

            menu_name = menu_name + ' для сети ' + network.f_name
            # update network for this rest
            _tmp = db.t_restaraunt[request.vars.rest['id']]
            _tmp.update_record(f_network_name=network.id)
            _new_menu = db.t_menu.insert(f_name=menu_name, f_current=True, f_type=[menu_type],
                                         f_comment=comment, f_network=network.id)
            db.commit()
            del _tmp
        ### Fill some variables
        else:
            # Lets find old menu and make it inactive
            # Find all active menus with given type
            _old_menu = db((db.t_menu.f_current == True) &
                           (db.t_rest_menu.t_rest == db.t_restaraunt.id) &
                           (db.t_rest_menu.t_menu == db.t_menu.id) &
                           (db.t_menu.f_type.belongs(request.vars.menu['type']))).select()
            for item in _old_menu:
                item.t_menu.f_current = False
                item.t_menu.update_record()

            menu_name = menu_name + ' для  ' + request.vars.rest['name'].encode('utf-8')
            _new_menu = db.t_menu.insert(f_name=menu_name, f_current=True, f_type=[menu_type],
                                         f_comment=comment)
            db.t_rest_menu.insert(t_menu=_new_menu, t_rest=rest_id)
            db.commit()
        return ajax_success()
    except AssertionError:
        logger.error('Exception happened in save_menu for user ' + auth.user.username + " request was " + str(request))
        return ajax_error()
    except Exception, e:
        logger.warn('Error in save_menu' + str(e) + ' for user ' + auth.user.username + " request was " + str(request))
        return ajax_error()


def course_edit():
    menu_name = request.vars.men_name
    course_name = request.vars.item_name
    menu_id = db(db.t_menu.f_name.contains(menu_name)).select(db.t_menu.id)[0].id
    item_id = db(db.t_item.f_name.contains(course_name)).select(db.t_item.id)[0].id
    course_price = db(db.t_item.id == item_id).select().first().f_price
    course_weight = db(db.t_item.id == item_id).select().first().f_weight
    # Create course object
    coar = course(course_name, course_price, course_weight)

    step = db(db.t_step.id == db.t_ingredient.id).select()
    # Get recipe ID for given item
    recipe_id = db((db.t_recipe.id == db.t_item.f_recipe) & (db.t_item.id == item_id)).select()[0].t_recipe.id
    # Get m-t-m relation - get all steps for given recipe id
    steps_ing = db((db.t_recipe.id == recipe_id) & (db.t_step.id == db.t_step_ing.t_step) & (
            db.t_recipe.id == db.t_step_ing.t_recipe))
    # Create list of ingrs
    ingrs = []
    for _cur_step in steps_ing.select():
        # get Ingr set names n weight
        ingr_name = db(db.t_ingredient.id == _cur_step.t_step.f_ingr).select(db.t_ingredient.f_name).first().f_name
        ingr_qty = _cur_step.t_step.f_qty
        ingr_unit = db(db.t_unit.id == _cur_step.t_step.f_unit).select().first()
        ingrs.append(ingredient(_cur_step.t_step.id, _cur_step.t_step.f_ingr, ingr_name, ingr_qty, ingr_unit.f_name,
                                ingr_unit.id))

    # tmp = db((db.t_ingredient.id == db.t_menu_item.t_item) & (db.t_menu.id == db.t_menu_item.t_menu))
    # courses = [item.t_item for item in tmp.select()]

    options = db(db.t_unit).select(db.t_unit.ALL)
    options = [x.f_name for x in options]
    return locals()


class menu_object():
    def __init__(self):
        self.menu_name = None
        self.rest_name = None
        self.items = []
        self.ingrs = []


class course():
    def __init__(self, item_name, item_price, item_weight):
        self.name = item_name
        self.price = item_price
        self.weight = item_weight


class ingredient():
    def __init__(self, step_id, ingr_id, ingr_name, ingr_weight, ingr_unit, ingr_unit_id):
        self.step_id = step_id
        self.id = ingr_id
        self.name = ingr_name
        self.weight = ingr_weight
        self.unit = ingr_unit
        self.unit_id = ingr_unit_id


def error():
    return dict()
