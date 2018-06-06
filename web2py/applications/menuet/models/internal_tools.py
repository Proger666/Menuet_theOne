import datetime
import re

import pymorphy2


def checkIfExist(*args):
    '''Test if arguments are exists via len, etc None'''
    for arg in args:
        try:
            if isinstance(arg, float) or isinstance(arg, int):
                if arg == 0:
                    return False
                else:
                    return True
            elif arg is None or len(arg) == 0 or arg == '' or arg == " ":
                return False
            else:
                return True
        except TypeError:
            pass


@auth.requires_login()
def get_ingrs_for_item(item_id):
    '''Should return list of ingrs from table t_ingrs'''
    # # get recipe for item to use later on
    # item_recipe = db.t_item.f_recipe
    # # get step
    # step = db(db.t_step.id == db.t_ingredient.id).select()
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
        _ingr = db(db.t_ingredient.id == _cur_step.t_step.f_ingr).select().first()
        ingr.name = _ingr.f_name
        ingr.qty = _cur_step.t_step.f_qty
        ingr.unit = db(db.t_unit.id == _cur_step.t_step.f_unit).select().first()
        ingr.id = _ingr.id
        ingrs.append(ingr)
    return ingrs


@auth.requires_login()
def add_ingrs_item(item_id, item_name, ingrs_list):
    '''Adds all ingrs in list to item'''
    _tmp_obj = Storage()
    # Create new recipe
    _tmp_obj.recipe_id = db.t_recipe.insert(f_name=item_name.lower() + '_recipe' + str(datetime.date.today()))
    for ingr in ingrs_list:
        # create new step
        _tmp_obj._new_step_id = db.t_step.insert(f_ingr=ingr, f_unit=1)
        # create new M-t-M
        _tmp_obj._t_step_ing_new_id = \
            db.t_step_ing.insert(t_step=_tmp_obj._new_step_id, t_recipe=_tmp_obj.recipe_id)

    db(db.t_item.id == item_id).update(f_recipe=_tmp_obj.recipe_id)
    db.commit()
    return True

def api_error(msg):
    return {'status': 'error', "msg": msg}


def api_success(msg):
    return {'status': 'OK', 'msg': msg}


def query_cleanUP(query):
    '''remove bad Characters and orther shit'''
    query = re.sub(r'[,&;(quot)]', " ", query)
    return query

def normalize_ingr(ingr):
    '''Returns normal form of ingr'''
    functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP', 'ADJF'}  # function words from Pymorphy2
    # remove any excessive words and letters
    ingr = query_cleanUP(ingr)

    ingr = ingr if pos(ingr) not in functors_pos else None
    if ingr is None:
        return None
    normal_form = " ".join(normalize_words(ingr.split()))
    return normal_form

def parse_ingrs_id(query):
    '''Should return list of ingrs ID for passed query'''
    # strip by words
    # delete all trash
    # remove all adjectives https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html
    functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP', 'ADJF'}  # function words from Pymorphy2
    query = query_cleanUP(query)
    _query_list = query.split()

    ingrs = [word for word in _query_list if pos(word) not in functors_pos]
    if len(ingrs) == 0:
        return []
    # now lets normalize everything
    ingrs_normal = normalize_words(ingrs)

    # Now lets find INGRS id if we have such by their normal form
    # TODO: redesign set search
    ingrs_id = [x.id for x in db(db.t_ingredient.f_normal_form.belongs(ingrs_normal)).select()]
    # if we dont have ingrs in DB = sorry
    return ingrs_id

def normalize_words(ingrs_list):
    # Do we have ingrs list ?
    if len(ingrs_list) == 0:
        return None
    morph = pymorphy2.MorphAnalyzer()
    result = []
    for ingr in ingrs_list:
        # lets get normal form of the word
        try:
            # bad design of library it will send exception if it doesnt know word
            result.append(morph.parse(ingr)[0].normal_form)
        except AttributeError:
            result.append(ingr)
        except UnicodeDecodeError:
            result.append(morph.parse(ingr.decode('utf-8'))[0].normal_form)
    if len(result) > 0:
        return result
    return None


def pos(word, morth=pymorphy2.MorphAnalyzer()):
    try:
        r = morth.parse(word.decode('utf-8'))[0].tag.POS
    except UnicodeDecodeError:
        r = morth.parse(word.encode('utf-8'))[0].tag.POS
    return r