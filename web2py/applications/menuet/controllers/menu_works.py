# -*- coding: utf-8 -*-
### required - do no delete
import datetime

from gluon.contrib import simplejson


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
        if type == 'rest':
            query = db.t_rest_tag.f_name.contains(q)
        elif type == 'm_tags':
            query = db.t_menu_tag.f_name.contains(q)
        elif type == 'i_tags':
            query = db.t_item_tag.f_name.contains(q)
        else:
            logger.info('Failure happened in tag suggestions ! ' + logUser_and_request())
            return {}
        # get suggestions from db based on type of the query
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
        # lets find ingredients
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
                    huections = get_tags_for_object(query, 'm_tags') if request.args[
                                                                            1] == 'm_tags' else get_tags_for_object(
                        query,
                        'i_tags')
                    return dict(suggestions=huections)
                elif request.args[1] == 'ingredients':
                    huections = get_sugg_for_ingrs(query)
                    return dict(suggestions=huections)
                elif request.args[1] == 'r_tags':
                    huections = get_tags_for_object(query, 'rest')
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
def dis_enab_menu():
    '''This one should enable/disable MENU via f_current field'''

    menu_id = request.vars.menu['id']

    #Inverse state
    state = False if request.vars.menu['state'] == 'True' else True
    if request.vars.menu is None:
        return ajax_error("oy wey")
    db(db.t_menu.id == menu_id).update(f_current=state)
    return ajax_success("Job done")


@auth.requires_login()
def fill_net():
    '''This function adds rest to existing NETWORK and making all present menus as OUTDATED '''
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


def find_item_tags_id(tags_name):
    '''Should return tags IDs as list'''
    if tags_name is None or len(tags_name) == 0:
        # return nothing if no data
        return []
    # returns list of ROWS with ID attribute inside - cast to list of pure IDs from this shit
    return [x.id for x in db(db.t_item_tag.f_name.belongs(str(tags_name.encode('utf-8')).split(","))).select(
        db.t_item_tag.id).as_list(storage_to_dict=False)]


@auth.requires_login()
def save_item():
    start = datetime.datetime.now()
    # Create storage class for item
    item = Storage()
    # lets get our item from request or get None
    item_source = request.vars.get('item', None)

    if item_source != None:
        item_source = Storage(item_source)
        _tmp_obj = Storage()
        # Lets gather stones
        _tmp_obj.cal = item_source['cal']
        # Lets play with tags
        # Create tags
        item_tags = item_source['tags_name']

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
                if len(ingr) > 0:
                    ingrs_to_commit.ingr = db.t_ingredient.insert(f_name=ingr.lower(), f_curate=True)
                    ingrs_to_commit_list.append(ingrs_to_commit)

        # Create new recipe
        _tmp_obj.recipe_id = db.t_recipe.insert(f_name=item_source.name.lower() + '_recipe')
        item_source.desc = "" if item_source.desc is None else item_source.desc

        if item_source.change_factor == 'add':
            # Create new Item
            _tmp_obj.item_id = db.t_item.insert(f_cal=_tmp_obj.cal, f_name=item_source.name.lower(),
                                                f_weight=item_source.weight,
                                                f_unit=item_source.unit, f_recipe=_tmp_obj.recipe_id,
                                                f_desc=item_source.desc, f_tags=_new_tags)

            stich_portions_to_prices(_tmp_obj, item_source)

            _tmp_obj._new_menu_item_id = db.t_menu_item.insert(t_menu=item_source.m_id,
                                                               t_item=_tmp_obj.item_id)


        elif item_source.change_factor == 'edit':
            # lets get recipe for this item
            # Let's change t_item fields
            # Add tags
            db(db.t_item.id == int(item_source.id.encode('utf-8'))).update(f_name=item_source.name.encode('utf-8'),
                                                                           f_desc=item_source.desc.encode('utf-8'),
                                                                           f_cal=item_source.cal.encode('utf-8'),
                                                                           f_tags=find_item_tags_id(
                                                                               item_source.tags_name),
                                                                           f_weight=int(
                                                                               item_source.weight.encode('utf-8')),
                                                                           f_recipe=_tmp_obj.recipe_id,
                                                                           f_unit=item_source.unit)
            # change portions
            _tmp_obj.item_id = item_source.id.encode('utf-8')
            stich_portions_to_prices(_tmp_obj, item_source)
        else:
            logger.error('Failed to save item ' + logUser_and_request())
            return ajax_error("We failed to save item :(")

        # ATTACH ALL INGRS TO ITEM
        stich_ingrs_to_item(_tmp_obj, ingrs_to_commit_list, item_source)

        db.commit()

        end = datetime.datetime.now() - start
        logger.info('item saved in ' + str(end))
        return ajax_success("Job done")

    return {}


def stich_ingrs_to_item(_tmp_obj, ingrs_to_commit_list, item_source):
    for step in ingrs_to_commit_list:
        # create new step
        _tmp_obj._new_step_id = db.t_step.insert(f_ingr=step.ingr, f_unit=item_source.unit)
        # create new M-t-M
        _tmp_obj._t_step_ing_new_id = \
            db.t_step_ing.update_or_insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)


def stich_portions_to_prices(_tmp_obj, item_source):
    # TODO:redesign
    ## search for all ows with this item and move to archive
    ## try to get stale records
    try:
        stale_rec = db.t_item_prices(db.t_item_prices.f_item == _tmp_obj.item_id).as_dict()
        ## Copy entire record stale record from current db to archive
        db.t_item_price_archive.insert(**stale_rec)
        # remove stale record
        db(db.t_item_prices.f_item == _tmp_obj.item_id).delete()
    except AttributeError:
        # its ok nothing todo
        pass
    for step in item_source.portions:
        # create new
        _tmp_obj.t_item_prices_id = db.t_item_prices.insert(
            f_price=int(step['portion_price'].encode('utf-8')),
            f_portion=int(step['portion_size'].encode('utf-8')),
            f_item=_tmp_obj.item_id)
