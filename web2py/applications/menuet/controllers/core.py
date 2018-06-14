# -*- coding: utf-8 -*-
### required - do no delete
import datetime

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
t_item_prices = db.t_item_prices


def to_latin(string):
    string = string.decode('utf-8')
    import re
    capital_letters = {u'А': u'A',
                       u'Б': u'B',
                       u'В': u'V',
                       u'Г': u'G',
                       u'Д': u'D',
                       u'Е': u'E',
                       u'Ё': u'E',
                       u'З': u'Z',
                       u'И': u'I',
                       u'Й': u'Y',
                       u'К': u'K',
                       u'Л': u'L',
                       u'М': u'M',
                       u'Н': u'N',
                       u'О': u'O',
                       u'П': u'P',
                       u'Р': u'R',
                       u'С': u'S',
                       u'Т': u'T',
                       u'У': u'U',
                       u'Ф': u'F',
                       u'Х': u'H',
                       u'Ъ': u'',
                       u'Ы': u'Y',
                       u'Ь': u'',
                       u'Э': u'E', }

    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                          u'Ц': u'Ts',
                                                          u'Ч': u'Ch',
                                                          u'Ш': u'Sh',
                                                          u'Щ': u'Sch',
                                                          u'Ю': u'Yu',
                                                          u'Я': u'Ya', }

    lower_case_letters = {u'а': u'a',
                          u'б': u'b',
                          u'в': u'v',
                          u'г': u'g',
                          u'д': u'd',
                          u'е': u'e',
                          u'ё': u'e',
                          u'ж': u'zh',
                          u'з': u'z',
                          u'и': u'i',
                          u'й': u'y',
                          u'к': u'k',
                          u'л': u'l',
                          u'м': u'm',
                          u'н': u'n',
                          u'о': u'o',
                          u'п': u'p',
                          u'р': u'r',
                          u'с': u's',
                          u'т': u't',
                          u'у': u'u',
                          u'ф': u'f',
                          u'х': u'h',
                          u'ц': u'ts',
                          u'ч': u'ch',
                          u'ш': u'sh',
                          u'щ': u'sch',
                          u'ъ': u'',
                          u'ы': u'y',
                          u'ь': u'',
                          u'э': u'e',
                          u'ю': u'yu',
                          u'я': u'ya', }

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = re.sub(ur"%s([а-я])" % cyrillic_string, ur'%s\1' % latin_string, string)

    for dictionary in (capital_letters, lower_case_letters):

        for cyrillic_string, latin_string in dictionary.iteritems():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = string.replace(cyrillic_string, latin_string.upper())

    return string


@auth.requires_login()
def check_rest():
    rest_name = request.vars.rest.get('name')
    result_list = []

    if rest_name != None:
        _rest_name = rest_name.split(' ')
        for word in _rest_name:
            if len(word) > 2:
                word = word.encode('utf-8')
                word_to_latin = to_latin(word)
                result_list.append(db(((db.t_restaraunt.f_name.contains(word)) |
                                       (db.t_restaraunt.f_name.contains(word_to_latin))) & (
                                              (db.t_restaraunt.f_locked_by != auth.user.id) | (
                                              db.t_restaraunt.f_locked_by == None))).select(db.t_restaraunt.f_name,
                                                                                            db.t_restaraunt.f_address,
                                                                                            db.t_restaraunt.id,
                                                                                            db.t_restaraunt.f_locked_by).as_json())
                # result_list.append(db(db.t_restaraunt.f_name.contains(word.encode('utf-8')), db.t_restaraunt.f_name).select())
    if len(result_list) > 0:
        return result_list
    session.flash = T('Failure')
    return False


@auth.requires_login()
def rest():
    rests = {"rests": []}
    rests = Storage(rests)
    _tmp = db(db.t_restaraunt.f_locked_by == auth.user.id).select(orderby=~db.t_restaraunt.modified_on, limitby=(0, 4))
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
def get_ingrs_for_item(item_id, units):
    start = datetime.datetime.now()
    # # get recipe for item to use later on
    # item_recipe = db.t_item.f_recipe
    # # get step
    # step = db(db.t_step.id == db.t_ingredient.id).select()
    # Get recipe ID for given item
    # recipe_id = db((db.t_recipe.id == db.t_item.f_recipe)
    #                & (db.t_item.id == item_id)).select()[0].t_recipe.id
    # Get m-t-m relation - get all steps for given recipe id
    steps_ing = db(
                   (db.t_step.id == db.t_step_ing.t_step) &
                   (db.t_recipe.id == db.t_step_ing.t_recipe))
    # Create list of ingrs
    # create ingrs storage class
    ingrs = []
    steps_ingr = steps_ing.select(join=db.t_recipe.on((db.t_recipe.id == db.t_item.f_recipe) & (db.t_item.id == item_id)))

    for _cur_step in steps_ingr:
        ingr = Storage()
        # get Ingr set names n weight
        ingr.name = db(db.t_ingredient.id == _cur_step.t_step.f_ingr).select(db.t_ingredient.f_name).first().f_name
        ingr.qty = _cur_step.t_step.f_qty
        ingr.unit = db(db.t_unit.id == _cur_step.t_step.f_unit).select().first() if units is None else units[_cur_step.t_step.f_unit]['unit']
        ingrs.append(ingr)
    end = datetime.datetime.now() - start
    logger.warning("ingrs fecthed for %s", end)
    return ingrs


@auth.requires_login()
def add_rest():
    # reuse existing
    return locals()


def check_exist(item):
    if item is not None and len(item) > 0:
        return True
    return False


def get_tags_for_item(tags_list):
    if tags_list is None or len(tags_list) == 0:
        return []
    tags = []
    tags_list = [x.encode('utf-8') for x in tags_list if len(x)]
    tags = db(db.t_item_tag.id.belongs(tags_list)).select(db.t_item_tag.f_name)
    return [x.f_name for x in tags]


@auth.requires_login()
def e_menu():
    start = datetime.datetime.now()
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
            menu_items = []
            # Get all ITEMS for this MENU and its details

            start = datetime.datetime.now()
            # is it Network menu or not ?
            _ = db(db.t_restaraunt.id == rest_id).select(db.t_restaraunt.f_is_network).first().f_is_network
            # sophisticated query that should return evrything we need for item
            if _  == True:
                _menu_items = getItems_for_menu(menu_id)
            elif _ == False:
                _menu_items = getItems_for_menu(menu_id)
            end1 = datetime.datetime.now() - start
            logger.warning("all menu loaded in %s", end1)
            _units = db(db.t_unit.id > 0 ).select()
            units = [{'id':x['id'], 'unit':x} for x in _units]
            # Lets fill item class
            for menu_item in _menu_items:
                # create class storage for item and items with context
                item = Storage()
                item.name = menu_item['item_name']
                item.id = menu_item['item_id']
                item.unit = None if menu_item.get('item_unit') is None else units[menu_item.get('item_unit')]['unit']['f_name']
                item.desc = ' '.join(menu_item.get('item_desc', "").split()[:4]) if check_exist(
                    menu_item.get('item_desc', "")) else ""  + "..."# ограничиваем 4 словами вывод
                item.ingrs = menu_item.get('ingrs_names', "").split(",") if menu_item.get('ingrs_names', "") is not None else []
                item.tags = get_tags_for_item(menu_item['item_tags'].split("|"))
                logger.warning("______ %s", datetime.datetime.now() - start)
                item.portions = []
                # get portions name from DB
                _portions = db(t_item_prices.f_item == item.id).select(t_item_prices.f_price, t_item_prices.f_portion)
                if _portions != None:
                    # fill array with price and portion name
                    for step in _portions:
                        portion = db.t_portion[step.f_portion].f_name
                        item.portions.append({'portion_size': portion, "portion_price": step.f_price})
                else:
                    logger.warn('No portions in request ' + logUser_and_request())
                    return {}
                end2 = datetime.datetime.now() - start
                menu_items.append(item)
                logger.warning('We add new menu item in %s', str(end2))
            tags = db.t_menu[menu_id].f_tags
            end3 = datetime.datetime.now() - start
            logger.warning("we loaded menu list in %s ", str(end3))
            return locals()
        else:
            logger.error("in e_menu, exception happened! " + logUser_and_request())
            raise HTTP(500)
    except HTTP:
        logger.warn('Missing one or all ids on page e_menu, menu id or rest id are missing ' + str(
            request.vars) + logUser_and_request())
        return None


@auth.requires_login()
def e_item():
    item = Storage()
    itm_id = request.vars.get('itm_id')
    units = db().select(db.t_unit.ALL)
    if itm_id != None:
        # fetch item by ID TODO: redesign to single SELECT
        _tmp = db.t_item[request.vars.itm_id]
        # create class storage for item
        item = Storage()
        item.name = _tmp.f_name
        item.weight = _tmp.f_weight
        item.cal = _tmp.f_cal
        item.id = _tmp.id
        item.unit = None if _tmp.f_unit is None else db.t_unit[_tmp.f_unit]
        item.desc =  "" if _tmp.f_desc is None else _tmp.f_desc
        item.ingrs = get_ingrs_for_item(item.id, None)
        item.tags = get_tags_for_object(item.id, 'item')
        item.portions = []
        # get portions name from DB
        _portions = db(t_item_prices.f_item == item.id).select(t_item_prices.f_price, t_item_prices.f_portion)
        if _portions != None:
            # fill array with price and portion name
            for step in _portions:
                portion = db.t_portion[step.f_portion]
                item.portions.append({'size': portion, "price": step.f_price})
        else:
            logger.warn('No portions in request ' + logUser_and_request())
            return locals()
    portions_name = db(db.t_portion).select()
    return locals()


@auth.requires_login()
def rests():
    rests = {"rests": []}
    rests = Storage(rests)
    _tmp = db(db.t_restaraunt.f_locked_by == auth.user.id).select()
    for row in _tmp:
        rests.rests.append({"id": row.id, "name": row.f_name, "created_on": row.created_on, "addr": row.f_address})
    rest_disp = [x for x in rests.rests]
    return locals()


@auth.requires_login()
def menus():
    menus = {"menus": []}
    _page = int(request.vars.get('page', 1))
    menus = Storage(menus)
    _menu = db.t_menu[request.vars.m_id]
    if _menu.f_network != 5:
        # how much items per page?
        itm_page = 7
        network = db.t_network[_menu.f_network]
        # lets fund all menus for this network
        query = db(db.t_menu.f_network == _menu.f_network)
        ############ PAGINATION #####################
        menus_count = query.count()
        # lets get how much pages wew wil have with round to nearest whole as
        # (something + divisor // 2) // divisor
        _tmp_calc = (menus_count + itm_page // 2) // itm_page
        pages_count = _tmp_calc if _tmp_calc > 0 else 1
        ###############################################
        _tmp = query.select(orderby=~db.t_menu.f_current)
        for row in _tmp:
            item_count = db(db.t_menu_item.t_menu == row.id).count()
            menus.menus.append({"id": row.id, "name": row.f_name, "created_on": row.created_on,
                                "rest_name": network.f_name, "rest_addr": "",
                                "r_id": network.id, "active": row.f_current, "item_count": item_count})
    else:
        _tmp = db((db.t_rest_menu.t_menu == t_menu.id) &
                  (t_rest_menu.t_rest == t_restaraunt.id) &
                  (t_restaraunt.id == request.vars.r_id)).select(orderby=~db.t_menu.f_current)

        for row in _tmp:
            item_count = db(db.t_menu_item.t_menu == row.t_menu.id).count()
            menus.menus.append({"id": row.t_menu.id, "name": row.t_menu.f_name, "created_on": row.t_menu.created_on,
                                "rest_name": row.t_restaraunt.f_name, "rest_addr": row.t_restaraunt.f_address,
                                "r_id": row.t_restaraunt.id, "active": row.t_menu.f_current, "item_count": item_count})

    menu_disp = [x for x in menus.menus]
    return locals()


def pagination(c, m, d):
    _range = []
    current = c
    last = m
    delta = d
    left = current - delta
    right = current + delta + 1
    rangeWithDots = []
    l = None
    i = 1
    for i in range(1, last):
        if i == 1 or i == last or (i >= left and i < right):
            _range.append(i)
        i += 1
    for x in range(1, len(_range)):
        if l:
            if x - l == delta:
                rangeWithDots.append(l + 1)
            elif x - l != 1:
                rangeWithDots.append('...')
        rangeWithDots.append(x)
        l = x
        x += 1
    return rangeWithDots


@auth.requires_login()
def lock_rest():
    row = db(db.t_restaraunt.id == request.vars.rest['r_id']).select().first()
    row.update_record(f_locked_by=auth.user.id)
    result = {'status': 'OK'}
    return simplejson.dumps(result)


def test():
    return locals()


def get_tags_for_object(id, type):
    result = []
    if id == None:
        logger.warn('Could not fetch tags for object, id is NULL!!! ' + logUser_and_request())
        return {}
    # select tags via lazy fetch
    if type == 'rest':
        query = db.t_restaraunt[id].f_tags
    elif type == 'item':
        query = db.t_item[id].f_tags
    else:
        logger.warn('Failed to get tags for object of type ' + str(type) + logUser_and_request())
        return {}
    if query != None:
        return [x.f_name for x in query]
    return []


@auth.requires_login()
def a_item():
    item = Storage()
    itm_id = request.vars.get('itm_id')
    units = db().select(db.t_unit.ALL)
    if itm_id != None:
        # fetch item by ID TODO: redesign to single SELECT
        _tmp = db.t_item[request.vars.itm_id]
        # create class storage for item
        item = Storage()
        item.name = _tmp.f_name
        item.weight = _tmp.f_weight
        item.id = _tmp.id
        item.unit = None if _tmp.f_unit is None else db.t_unit[_tmp.f_unit]
        item.desc = _tmp.f_desc
        item.ingrs = get_ingrs_for_item(item.id, None)
        item.tags = get_tags_for_object(item.id, 'item')
        item.portions = []
        # get portions name from DB
        _portions = db(t_item_prices.f_item == item.id).select(t_item_prices.f_price, t_item_prices.f_portion)
        if _portions != None:
            # fill array with price and portion name
            for step in _portions:
                portion = db.t_portion[step.f_portion]
                item.portions.append({'portion_size': portion, "portion_price": step.f_price})
        else:
            logger.warn('No portions in request ' + logUser_and_request())
            return locals()
    else:
        item.menu_name = db.t_menu[request.vars.get('m_id', 0)].f_name
        item.name = ""
        item.weight = ""
        item.desc = ""
        item.unit = ""
        item.m_id = ""
        item.ingrs = ""
        item.portions = ""
        item.tags_id = ""
        item.tags_name = ""
        item.desc = item.name = ''
        item.weight = 0
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
        rest.tags = get_tags_for_object(_rest.id, 'rest')

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
