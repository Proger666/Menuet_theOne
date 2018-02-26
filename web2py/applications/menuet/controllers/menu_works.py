# -*- coding: utf-8 -*-
### required - do no delete
from gluon.contrib import simplejson


def get_network_sugg(q):
    result = {}
    if q != None:
        result = []
        rows = db(db.t_network.f_syn.like('%' + q.encode('utf-8') + '%')).select()
        for row in rows:
            result.append({
                'id': row.id,
                'unrestricted_value': row.f_name,
                'value': row.f_name})
    return result


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


@auth.requires_login()
@request.restful()
def api():
    def POST(*args, **vars):
        query = request.vars.get('query')
        if query != None:
            # find from second letter
            if request.args[1] == 'network' and len(query) > 2:
                huections = get_network_sugg(query)
                return dict(suggestions=huections)
        else:
            return dict(suggestions={"status" : "ok"})

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

        ingrs_list = [x.strip() for x in item_source.ingrs.split(',')]
        ingrs_to_commit_list = []
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
                                                f_desc=item_source.desc)

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
        ####################### ADD INGREDIENTS #####################################
        step = db(db.t_step.id == db.t_ingredient.id).select()
        # Get m-t-m relation - get all steps for given recipe id
        steps_ing = db((db.t_recipe.id == _tmp_obj.recipe_id) & (db.t_step.id == db.t_step_ing.t_step) & (
                db.t_recipe.id == db.t_step_ing.t_recipe))

        # lets commit ingrs to db
        _tmp_obj._new_step_id = db.t_step.update_or_insert(f_unit=_tmp_obj.unit_id,
                                                           f_ingr=_tmp_obj.ingr_id)
        _tmp_obj._t_step_ing_new_id = \
            db.t_step_ing.update_or_insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)
        db.commit()

        return ajax_success()

    return {}
