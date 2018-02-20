from gluon.contrib import simplejson


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
    return simplejson.dumps("{'status':'ERR'}")

@auth.requires_login()
def save_item():
    # Create storage class for item
    item = Storage()
    #lets get our item from request
    item_source = request.vars.get('item')
    if item_source != None:
        item_source = Storage(item_source)
        _tmp_obj = Storage()
        # Lets gather stones
        if item_source.change_factor == 'add':

            # Create new recipe
            _tmp_obj.recipe_id = db.t_recipe.insert(f_name=item_source.name +  '_recipe')
            item_source.desc = "" if item_source.desc == None else item_source.desc
            # Create new Item
            _tmp_obj.item_id = db.t_item.insert(f_name=item_source.name,
                                                f_weight=item_source.weight,
                                                f_price=item_source.price,
                                                f_unit=item_source.unit, f_recipe=_tmp_obj.recipe_id, f_desc=item_source.desc)

            _tmp_obj.item_unit_id = item_source.unit
            _tmp_obj._new_menu_item_id = db.t_menu_item.insert(t_menu=item_source.m_id,
                                                       t_item=_tmp_obj.item_id)
        else:
            _tmp_obj.recipe_id = item_source.recipe_id
        return ajax_success()
      ####################### ADD INGREDIENTS #####################################


    return {}