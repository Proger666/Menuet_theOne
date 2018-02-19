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


def getMenu_forRest(rest_id, menu_id):
    menu = db((t_menu.id == menu_id) &
              (t_restaraunt.id == rest_id) &
              (t_rest_menu.t_menu == t_menu.id) &
              (t_rest_menu.t_rest == t_restaraunt.id)).select(t_menu.ALL).first()
    return menu


def getItems_for_menu(menu_id):
    items = db((t_menu.id == menu_id)
               & (t_menu_item.t_menu == t_menu.id)
               & (t_menu_item.t_item == t_item.id)).select(t_item.ALL)
    return items


def get_ingrs_for_item(item_id):
    # get recipe for item to use later on
    item_recipe = db.t_item.f_recipe
    # get all ingrs for this item
    ingrs = db((t_item.id == item_id) &
               # get recipe for this item
               (db.t_recipe.id == item_recipe) &
               # M-to-M relation for step <> recipe
               (db.t_step_ing.t_step == db.t_step.id) &
               (db.t_step_ing.t_recipe == db.t_recipe.id)).select(db.t_ingredient.ALL)

    return ingrs


@auth.requires_login()
def e_menu():
    try:
        # get something or NONE
        menu_id = request.vars.get('m_id')
        rest_id = request.vars.get('r_id')
        if rest_id == None and menu_id == None:
            # just throw them execption in the face
            raise HTTP(500)
            # are u really a digit ? dont you ?
        elif str.isdigit(menu_id) and str.isdigit(rest_id):
            # get current menu based on URL parameters
            menu = Storage(getMenu_forRest(rest_id, menu_id))
            # Get all ITEMS for this MENU
            menu_items = getItems_for_menu(menu_id)
            # create class sotrage for item
            item = Storage()
            # Lets fill item class
            for menu_item in menu_items:
                item.name = menu_item.f_name
                item.id = menu_item.id
                ingrs = get_ingrs_for_item(item.id)
        else:
            raise HTTP(500)
    except HTTP:
        logger.warn('Missing one or all ids on page e_menu, menu id or rest id are missing ' + str(request.vars))
        return None
    return locals()


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
def lock_rest():
    assert request.vars.rest['r_id'] != None
    row = db(db.t_restaraunt.id == request.vars.rest['r_id']).select().first()
    row.update_record(modified_by=auth.user.id)
    result = {'status': 'OK'}
    return simplejson.dumps(result)


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
        rest.addr = _rest.f_address
        rest.id = _rest.id
        rest.created_on = _rest.created_on
        rest.img = _rest.f_img
        rest.is_network = _rest.f_is_network
        rest.modified_on = _rest.modified_on

        # Get all menus for this restaraunt
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
    menu_seosanal = db().select(db.t_seosanal_type.ALL)
    return locals()
