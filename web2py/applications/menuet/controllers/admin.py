from gluon.contrib import simplejson
from gluon.contrib.simplejson import JSONDecodeError


def parse_items_ingrs():
    '''Do various tasks with ingrs and items'''
    # Should parse ingredients from item's name and attach them to item
    if request.vars.job == 'parse_ingrs':
        from_ingr = int(request.vars.from_ingr)
        _tmp_items = db(db.t_item.id > from_ingr).select()
        for item in _tmp_items:
            ingrs = get_ingrs_for_item(item.id)
            # now we have list of ingrs
            # lets parse item name
            if item.id == 135:
                pass
            try:
                parsed_ingrs_id_list = parse_ingrs_id(item.f_name)
                if len(parsed_ingrs_id_list) > 0:
                    parsed_ingrs_id_list += [x['id'] for x in ingrs]
                    add_ingrs_item(item.id, item.f_name, set(parsed_ingrs_id_list))

            except Exception as e:
                return simplejson.dumps({'status': 'ERROR!', 'msg': str(e.message) + 'for item:' + str(item.id)})
        msg = 'We updated ' + str(len(_tmp_items)) + ' items'
        return simplejson.dumps({'status': 'OK', 'msg': msg})
    elif request.vars.job == 'ingrs_normal':
        _ingrs = db(db.t_ingredient.id > 0).select()
        try:
            for ingr in _ingrs:
                normal_form = normalize_ingr(ingr.f_name)

                db(db.t_ingredient.id == ingr.id).update(f_normal_form=normal_form, f_curate='F')
            db.commit()
        except Exception as e:
            msg = 'We FAILED at ' + str(ingr)
            return simplejson.dumps({'status': 'ERROR', 'msg': msg})
        msg = 'We updated ' + str(len(_ingrs)) + ' ingredients'
        return simplejson.dumps({'status': 'OK', 'msg': msg})


@auth.requires_membership('admin')
def statistics():
    result_list = []

    result_list = (db(db.t_restaraunt).select()).as_json()

    return result_list


@auth.requires_membership('admin')
def report():
    return locals()


@auth.requires_membership('admin')
def add_items_json():
    menu_id = request.vars.m_id
    json_data = request.vars.json_data
    if menu_id is None or len(menu_id) == 0:
        return HTTP(404)
    if json_data is not None and len(json_data) > 0:
        try:
            cat_array = simplejson.loads(json_data)
            tags = request.vars.get("tags", [])
            tags_list = []
            if tags is not None and len(tags) > 0:
                tags = tags.strip()
                tags = tags.split(",")
                for tag in tags:
                    tag_id = db(db.t_item_tag.f_name == tags).select(db.t_item_tag.id).first()
                    tags_list.append(tag_id if tag_id is not None else db.t_item_tag.insert(f_name=tag))
            for item in cat_array['categories'][0]['items']:
                _recipe = db.t_recipe.update_or_insert(f_name=item['name'] + "_recipe")
                if _recipe is None:
                    _recipe = db.t_recipe.insert(f_name=item['name'] + "_recipe")
                _tmp_item = db.t_item.update_or_insert(f_name=item['name'], f_unit=1, f_recipe=_recipe,
                                                       f_tags=tags_list)
                db.t_item_prices.insert(f_price=item['price'], f_item=_tmp_item, f_portion=1)
                db.t_menu_item.insert(t_item=_tmp_item, t_menu=menu_id)
                db.commit()
                response.flash = "Job DONE!"
        except JSONDecodeError:
            response.flash = 'Not a json!! FAILURE'

    return locals()
