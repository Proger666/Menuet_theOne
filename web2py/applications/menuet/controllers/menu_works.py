# -*- coding: utf-8 -*-
### required - do no delete
from gluon.contrib import simplejson
import pymorphy2

def get_network_sugg(q):
    if q != None:
        result = []
        rows = db(db.t_network.f_syn.like('%' + q.encode('utf-8') + '%')).select()
        for row in rows:
            result.append({
                'id': row.id,
                'unrestricted_value': row.f_name,
                'value': row.f_name})
        return result
    return {}


def get_tags_for_object(q, type):
    if q != None:
        result = []
        q = q.encode('utf-8')
        # search for menu or item tags
        query = db.t_menu_tag.f_name.contains(q) if type == 'menu' else db.t_item_tag.f_name.contains(q)
        rows = db(query).select()
        for row in rows:
            result.append({
                'id': row.id,
                'unrestricted_value': row.f_name,
                'value': row.f_name})
        return result
    return {}


def get_sugg_for_ingrs(q):
    if q != None:
        result = []
        q = q.encode('utf-8')
        #lets find ingredients
        rows = db(db.t_ingredient.f_name.contains(q)).select()
        for row in rows:
            result.append({
                'id': row.id,
                'unrestricted_value': row.f_name,
                'value': row.f_name})
        return result
    return {}


@request.restful()
def api():
    def POST(*args, **vars):
        # check if query exists
        query = request.vars.get('query')
        if query != None:
            # search only if we have 2 characters
            if len(query) > 2:
                # Search for rest Network
                if request.args[1] == 'network':
                    huections = get_network_sugg(query)
                    return dict(suggestions=huections)
                # Search for tag (menu or item)
                elif request.args[1] == 'm_tags' or request.args[1] == 'i_tags':
                    huections = get_tags_for_object(query, 'menu') if request.args[
                                                                          1] == 'm_tags' else get_tags_for_object(query,
                                                                                                                  'i_tags')
                    return dict(suggestions=huections)
                elif request.args[1] == 'ingredients':
                    huections = get_sugg_for_ingrs(query)
                    return dict(suggestions=huections)

        else:
            return dict(suggestions={"status": "ok"})

    try:
        result = db()
    except:
        logger.warn('suggestion for Network failed for user ' + auth.user.username)
    return locals()


@auth.requires_login()
def change_price_item():
    try:
        item = request.vars.get('item')
        if item != None:
            # lets try convert everything to int
            item_c = Storage()
            item_c.id = item['id']
            item_c.curr_price = 0 if item.get('curr_price') == u'None' else int(item['curr_price'])
            item_c.new_price = int(item['new_price'])
            # create archive of the current price
            db.t_item_price_archive.insert(f_price=item_c.curr_price, f_item=item_c.id)
            # update current price
            db.t_item[item_c.id] = dict(f_price=item_c.new_price)
            return simplejson.dumps("{'status':'OK'}")
    except:
        return {}
    return {}


@auth.requires_login()
def fill_net():
    try:
        network = db.t_network[request.vars.network['id']]
        # check if request for rest adding
        if 'rest' not in request.vars:
            if network == None:
                logger.error(
                    "fill_net FAILURE !!! Network can't be found. DATABASE ERROR!!! for user " + auth.user.username + " and request was " + str(
                        request))
                return {}
        else:
            rest_id = int(request.vars.rest['id'].encode('utf-8'))
            _old_menu = db((db.t_menu.f_current == True) &
                           (db.t_rest_menu.t_rest == db.t_restaraunt.id) &
                           (db.t_rest_menu.t_menu == db.t_menu.id) &
                           (db.t_restaraunt.id == rest_id)).select()
            for item in _old_menu:
                item.t_menu.f_current = False
                item.t_menu.update_record()
            # let's add network to rest
            _row = db.t_restaraunt[rest_id]
            _row.update_record(f_network_name=network.id, f_is_network=True)
            db.commit()
        # Find ANY restaraunt from this network
        rest_from_net = db(db.t_restaraunt.f_network_name == request.vars.network['id']).select().first()
        # if nothing found - show - Create menu
        if rest_from_net == None:
            # create menu for network
            session.flash = "Меню не найдено, создайте меню"
            return {}
        else:
            db.commit()
            return simplejson.dumps({"status": 'ok'})
    except:
        logger.warn('Something happend with network fullfilment for user ' + auth.user.username)
        return {}
    logger.error("Error in fill_net() - final failure approached for user " + auth.user.username)
    return {}


def ajax_success():
    session.flash = T("Success!")
    return simplejson.dumps("{'status':'OK'}")


def ajax_error():
    session.flash = T("Failure!")
    return {}


@auth.requires_login()
def delete_menu_item():
    # Delete menu item from
    try:
        item = request.vars.get('data_id')
        if item != None:
            # Check for exist item in t_menu
            check_exist = db(db.t_item.id == item).count()
            if check_exist > 0:
                db(db.t_item.id == item).delete()
    except:
        logger.warn('Failure in item delete ' + logUser_and_request())
        return {}
    logger.warn('Failure in item delete - final except ' + logUser_and_request())
    return {}


def normalize_words(ingrs_list):
    # Do we have ingrs list ?
    if ingrs_list == None:
        # TODO: redesign, add more checks
        logger.warn("Ingredient list has been pushed for normalize_words function " + logUser_and_request())
        return ajax_error()
    morph = pymorphy2.MorphAnalyzer()
    result = []
    for ingr in ingrs_list:
        # lets get normal form of the word
        try:
            # bad design of library it will set exception if it doesnt know word
            result.append(morph.parse(ingr)[0].inflect({'plur'}).word)
        except AttributeError:
            logger.error("Could not find plural form for ingredient! " + logUser_and_request())
            result.append(ingr)
    if len(ingrs_list) > 0:
        return result
    return ajax_error()


@auth.requires_login()
def save_item():
    # Create storage class for item
    item = Storage()
    # lets get our item from request
    item_source = request.vars.get('item')

    if item_source != None:
        item_source = Storage(item_source)
        _tmp_obj = Storage()
        # Lets gather stones

        # Lets play with tags
        # Create tags
        item_tags = item_source['tags_name']
        item_tags_id = item_source['tags_id']

        if item_tags == None:
            logger.warn("User failed to fill tags for item " + logUser_and_request())
            session.flash = T("ТЭГИ НЕ УКАЗАНЫ!")
            return {}
        else:
            item_tags = item_tags.split(",")
            _new_tags = []
        for tag in item_tags:
            _r_t = db(db.t_item_tag.f_name == tag).select().first()
            if _r_t == None and tag != "":
                _new_tags.append(db.t_item_tag.insert(f_name=tag))
            elif _r_t != None:
                _new_tags.append(_r_t.id)

        # Lets play with ingrs
        ####################### ADD INGREDIENTS #####################################

        ingrs_list = [x.strip() for x in item_source.ingrs.split(',')]
        ingrs_to_commit_list = []
        ingrs_list = normalize_words(ingrs_list)
        # Lets find ingrs one by one
        for ingr in ingrs_list:
            found = db(db.t_ingredient.f_name.like(ingr)).select().first()
            ingrs_to_commit = Storage()
            if found is not None:
                ingrs_to_commit.ingr = found.id
                ingrs_to_commit.f_curate = False
                ingrs_to_commit_list.append(ingrs_to_commit)
            else:
                ingrs_to_commit.f_curate = True
                # commit new ingr
                ingrs_to_commit.ingr = db.t_ingredient.insert(f_name=ingr, f_curate=True)
                ingrs_to_commit_list.append(ingrs_to_commit)

        if item_source.change_factor == 'add':

            # Create new recipe
            _tmp_obj.recipe_id = db.t_recipe.insert(f_name=item_source.name + '_recipe')
            item_source.desc = "" if item_source.desc is None else item_source.desc
            # Create new Item
            _tmp_obj.item_id = db.t_item.insert(f_name=item_source.name,
                                                f_weight=item_source.weight,
                                                f_unit=item_source.unit, f_recipe=_tmp_obj.recipe_id,
                                                f_desc=item_source.desc, f_tags=_new_tags)

            for step in item_source.portions:
                _tmp_obj.t_item_prices_id = db.t_item_prices.insert(
                    f_price=int(step['portion_price'].encode('utf-8')),
                    f_portion=int(step['portion_size'].encode('utf-8')),
                    f_item=_tmp_obj.item_id)

            _tmp_obj.item_unit_id = item_source.unit
            _tmp_obj._new_menu_item_id = db.t_menu_item.insert(t_menu=item_source.m_id,
                                                               t_item=_tmp_obj.item_id)

            for step in ingrs_to_commit_list:
                # create new step
                _tmp_obj._new_step_id = db.t_step.insert(f_ingr=step.ingr)
                # create new M-t-M
                _tmp_obj._t_step_ing_new_id = \
                    db.t_step_ing.update_or_insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)


        else:
            _tmp_obj.recipe_id = item_source.recipe_id
        ####################### ADD M-M relations for item #####################################
        step = db(db.t_step.id == db.t_ingredient.id).select()
        # Get m-t-m relation - get all steps for given recipe id
        steps_ing = db((db.t_recipe.id == _tmp_obj.recipe_id) & (db.t_step.id == db.t_step_ing.t_step) & (
                db.t_recipe.id == db.t_step_ing.t_recipe))

        # lets commit steps to DB
        _tmp_obj._new_step_id = db.t_step.update_or_insert(f_unit=_tmp_obj.unit_id,
                                                           f_ingr=_tmp_obj.ingr_id)
        _tmp_obj._t_step_ing_new_id = \
            db.t_step_ing.update_or_insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)
        db.commit()

        return ajax_success()

    return {}
