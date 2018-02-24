# -*- coding: utf-8 -*-
### required - do no delete
from gluon.contrib import simplejson

# define this DB SHIT!
t_menu = db.t_menu
t_restaraunt = db.t_restaraunt
t_rest_menu = db.t_rest_menu
t_ingredient = db.t_ingredient
t_seosanal_type = db.t_seosanal_type
t_menu_type = db.t_menu_type
t_menu_item = db.t_menu_item
t_item = db.t_item


@auth.requires_login()
def check_rest():
    rest_name = request.vars.rest.get('name')
    result_list = []

    if rest_name != None:
        _rest_name = rest_name.split(' ')
        for word in _rest_name:
            if len(word) > 2:
                result_list.append(db(db.t_restaraunt.f_name.contains(word.encode('utf-8')) & (
                        (db.t_restaraunt.modified_by != auth.user.id) | (
                        db.t_restaraunt.modified_by == None))).select(db.t_restaraunt.f_name,
                                                                      db.t_restaraunt.f_address,
                                                                      db.t_restaraunt.id,
                                                                      db.t_restaraunt.modified_by).as_json())
                # result_list.append(db(db.t_restaraunt.f_name.contains(word.encode('utf-8')), db.t_restaraunt.f_name).select())
    if len(result_list) > 0:
        return result_list
    session.flash = T('Failure')
    return False


@auth.requires_login()
def rest():
    rests = {"rests": []}
    rests = Storage(rests)
    _tmp = db(db.t_restaraunt.modified_by == auth.user.id).select(orderby=~db.t_restaraunt.created_on, limitby=(0, 4))
    for row in _tmp:
        rests.rests.append({"id": row.id, "name": row.f_name, "created_on": row.created_on, "addr": row.f_address})

    rest_disp = [x for x in rests.rests]
    return locals()


@auth.requires_login()
def getMenu_forRest(rest_id, menu_id):
    # is rest from network ?
    network_menu = db.t_menu[menu_id]
    if network_menu != None:
        if network_menu.f_network:
            # just get all menus for network
            menu = db.t_menu[menu_id]
        else:
            # oh shit seems we need to get M-t-M
            menu = db((t_menu.id == menu_id) &
                      (t_restaraunt.id == rest_id) &
                      (t_rest_menu.t_menu == t_menu.id) &
                      (t_rest_menu.t_rest == t_restaraunt.id)).select(t_menu.ALL).first()
    else:
        logger.error(
            "Rest not found in getMenu_forRest, supplied rest_id seems to be corrupted " + logUser_and_request())
        return {}
    return menu


@auth.requires_login()
def getItems_for_menu(menu_id):
    items = db((t_menu.id == menu_id)
               & (t_menu_item.t_menu == t_menu.id)
               & (t_menu_item.t_item == t_item.id)).select(t_item.ALL)
    return items


@auth.requires_login()
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
    ingrs = []
    for _cur_step in steps_ing.select():
        ingr = Storage()
        # get Ingr set names n weight
        ingr.name = db(db.t_ingredient.id == _cur_step.t_step.f_ingr).select(db.t_ingredient.f_name).first().f_name
        ingr.qty = _cur_step.t_step.f_qty
        ingr.unit = db(db.t_unit.id == _cur_step.t_step.f_unit).select().first()
        ingrs.append(ingr)
    return ingrs


def add_rest():
    # reuse existing
    return locals()


@auth.requires_login()
def e_menu():
    try:
        # get something or NONE
        menu_id = request.vars.get('m_id')
        rest_id = request.vars.get('r_id')
        if rest_id == None or menu_id == None:
            # just throw them exception in the face
            raise HTTP(500)
            # are u really a digit ? dont you ?
        elif str.isdigit(menu_id) and str.isdigit(rest_id):
            # get current menu based on URL parameters
            menu = Storage(getMenu_forRest(rest_id, menu_id))
            # Get all ITEMS for this MENU
            _menu_items = getItems_for_menu(menu_id)
            menu_items = []
            # Lets fill item class
            for menu_item in _menu_items:
                # create class storage for item
                item = Storage()
                item.name = menu_item.f_name
                item.id = menu_item.id
                item.unit = None if menu_item.f_unit is None else db.t_unit[menu_item.f_unit].f_name
                item.desc = menu_item.f_desc
                item.price = menu_item.f_price
                item.ingrs = get_ingrs_for_item(item.id)
                menu_items.append(item)
            return locals()
        else:
            logger.error("in e_menu, exception happened! " + logUser_and_request())
            raise HTTP(500)
    except HTTP:
        logger.warn('Missing one or all ids on page e_menu, menu id or rest id are missing ' + str(
            request.vars) + logUser_and_request())
        return None


def e_item():
    # safely get item id if it exists else - NONE
    item_id = request.vars.get('itm_id')
    if str(item_id).isdigit():
        item = t_item[item_id]
        return dict(item=item)
    return HTTP(404)


@auth.requires_login()
def rests():
    rests = {"rests": []}
    rests = Storage(rests)
    _tmp = db(db.t_restaraunt.modified_by == auth.user.id).select()
    for row in _tmp:
        rests.rests.append({"id": row.id, "name": row.f_name, "created_on": row.created_on, "addr": row.f_address})
    rest_disp = [x for x in rests.rests]
    return locals()


@auth.requires_login()
def menus():
    menus = {"menus": []}
    menus = Storage(menus)
    _menu = db.t_menu[request.vars.m_id]
    if _menu.f_network != 5:
        network = db.t_network[_menu.f_network]
        _tmp = db(db.t_menu.f_network == _menu.f_network).select()
        for row in _tmp:
            menus.menus.append({"id": row.id, "name": row.f_name, "created_on": row.created_on,
                                "rest_name": network.f_name, "rest_addr": "",
                                "r_id": network.id, "active": row.f_current})
    else:
        _tmp = db((db.t_rest_menu.t_menu == t_menu.id) &
                  (t_rest_menu.t_rest == t_restaraunt.id) &
                  (t_restaraunt.id == request.vars.r_id)).select(orderby=~db.t_menu.modified_on)

        for row in _tmp:
            menus.menus.append({"id": row.t_menu.id, "name": row.t_menu.f_name, "created_on": row.t_menu.created_on,
                                "rest_name": row.t_restaraunt.f_name, "rest_addr": row.t_restaraunt.f_address,
                                "r_id": row.t_restaraunt.id, "active": row.t_menu.f_current})
    menu_disp = [x for x in menus.menus]
    return locals()


@auth.requires_login()
def lock_rest():
    row = db(db.t_restaraunt.id == request.vars.rest['r_id']).select().first()
    row.update_record(modified_by=auth.user.id)
    result = {'status': 'OK'}
    return simplejson.dumps(result)


def test():
    return locals()


@auth.requires_login()
def a_item():
    item = Storage()
    itm_id = request.vars.get('itm_id')
    if itm_id != None:
        _tmp = db.t_item[request.vars.itm_id]
        item.desc = _tmp.f_desc
        item.price = _tmp.f_price
        item.name = _tmp.f_name
        item.weight = _tmp.f_unit.f_name
    else:
        item.desc = item.name = item.price = ''
        item.weight = 0
        units = db().select(db.t_unit.ALL)
    portions = db(db.t_portion).select()
    return locals()


lock = 0


@auth.requires_login()
def get_ingrs():
    global lock
    _tmp = db(db.t_ingredient.f_name.contains(request.vars.q)).select(db.t_ingredient.ALL)
    _rs = []
    for _s in _tmp:
        _rs.append({'label': _s.f_name, 'id': _s.id})
        lock += 1
    return simplejson.dumps(_rs)


@auth.requires_login()
def e_rest():
    if "r_id" in request.vars:
        RU_MONTH_VALUES = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 10,
            'декабря': 12,
        }

        _rest = db(
            (db.t_restaraunt.created_by == auth.user.id) and (db.t_restaraunt.id == request.vars.r_id)).select().first()
        # Form rest ast class
        rest = Storage()
        # fill the attr
        rest.name = _rest.f_name
        rest.town = _rest.f_town
        rest.addr = _rest.f_address
        rest.id = _rest.id
        rest.created_on = _rest.created_on
        rest.img = _rest.f_img
        rest.is_network = _rest.f_is_network
        rest.modified_on = _rest.modified_on
        rest.f_network_name = db.t_network[_rest.f_network_name].f_name
        rest.f_network_id = db.t_network[_rest.f_network_name].id

        # Get all menus for this restaraunt
        if rest.is_network:
            # gets network menu insted of per rest menu
            tmp = db(
                (t_menu.f_network == rest.f_network_id)).select()
            menus = tmp
        else:
            tmp = db(
                (db.t_menu.id == db.t_rest_menu.t_menu) & (db.t_restaraunt.id == db.t_rest_menu.t_rest)
            )
            menus = [menux.t_menu for menux in tmp(db.t_restaraunt.id == rest.id).select()]
        # create menu object
        menu_disp = []
        for _menu in menus:
            if _menu.f_current is True:
                menu = Storage()
                menu.id = _menu.id
                menu.name = _menu.f_name
                menu.created_on = _menu.created_on
                menu_disp.append(menu)
    else:
        redirect(URL("core", "rest"))
    menu_types = db().select(t_menu_type.ALL)
    menu_seosanal = False
    return locals()
