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
