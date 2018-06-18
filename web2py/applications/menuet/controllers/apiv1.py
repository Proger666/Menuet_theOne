# -*- coding:utf8 -*-
# !/usr/bin/env python

# API/rest/{ID}/_add ++
#              /_delete?
#              /_get
#


# AUTH VIA TOKEN - GET FROM DB PER USER

TEMP_TOKEN = "12345678901"


def check_token(token):
    if token is not None and len(token) > 10:
        if token == TEMP_TOKEN:
            return True
    return False

@auth.requires_login()
def new_rest(rest, auth, src):
    # dissallow direct requests
    if not src:
        return {'status': 'error', 'msg': 'forbidden'}
    try:
        # Expected structure
        rest_name = rest.get('name', None)
        rest_addr = rest.get('addr', None)
        rest_town = rest.get('town', None)
        rest_net_name = rest.get('network_name', None)
        rest_is_network = rest.get('is_network', None)
        rest_tags = rest.get('tags', None)

        # check if we have everything we need
        if rest_town == None or rest_town == "":
            logger.warn('no town in request' + ' vars were: ' + str(rest))
            return {'status': 'error', 'msg': 'ГОРОД НЕ УКАЗАН!', 'rsn': 'r_town'}
        if rest_name == None or rest_name == "":
            logger.warn('no rest name in request' + ' vars were: ' + str(rest))
            return {'status': 'error', 'msg': 'НАИМЕНОВАНИЕ НЕ УКАЗАНО!', 'rsn': 'r_name'}
        if rest_addr == None or rest_addr == "":
            logger.warn('no rest addr in request' + ' vars were: ' + str(rest))
            return {'status': 'error', 'msg': 'АДРЕС НЕ УКАЗАН!', 'rsn': 'r_addr'}

        # lets fill the tags
        if rest_tags == None:
            rest_tags = []
        else:
            rest_tags = rest_tags.split(",")
        _new_tags = []
        for tag in rest_tags:
            _r_t = db(db.t_rest_tag.f_name == tag).select().first()
            if _r_t == None and tag != "":
                _new_tags.append(db.t_rest_tag.insert(f_name=tag))
            elif _r_t != None:
                _new_tags.append(_r_t.id)

        # fill network 5 - if not a network
        if rest_net_name != u'None' and rest_net_name != None:
            _tmp_q = db(db.t_network.f_name == rest_net_name.encode('utf-8')).select(db.t_network.id).first()
            if _tmp_q is None:
                rest_network = db.t_network.insert(f_name=rest_net_name.encode('utf-8'))
            else:
                rest_network = _tmp_q.id
        else:
            rest_network = 5

        if rest_is_network and rest_network == 5:
            logger.warn('no network in request' + ' vars were: ' + str(rest))
            return {'status': 'error', 'msg': "Сеть не указана!"}

        # Check if rest already exists
        # todo: dangerous search
        rest = db((db.t_restaraunt.f_name.like(rest_name)) &
                  (db.t_restaraunt.f_town == rest_town)).select().first()
        if rest is None:
            # create new rest if nothing found
            # check if rest net is empty
            if int(rest_network):
                db.t_restaraunt.insert(f_name=rest_name, f_active=True, f_is_network=rest_is_network,
                                       f_address=rest_addr,
                                       f_town=rest_town, f_network_name=rest_network, f_tags=_new_tags,
                                       f_locked_by=None if auth.user is None else auth.user.id)
                db.commit()
                return {'status': 'OK', 'msg': 'Ресторан добавлен'}
            else:
                msg = "save rest failed!!" + ' request vars were ' + str(rest)
                logger.error(msg)
                return {'status': 'error', 'msg': msg}
    except:
        msg = 'Problem in new_rest api - Exception occurred' + str(
            Exception.message)
        logger.error(msg)
        return {'status': 'error', 'msg': msg}


@request.restful()
def api():
    # TODO: redisign
    def POST(*args, **vars):
        # lets validate authentication for request
        if request.ajax == True:
            # lets check if user authenticated
            if auth.user is None:
                logger.warn('ALARM!! someone using API ' + str(request.vars))
                return {'status': 'error', 'msg': 'action failed'}
        else:
            # TODO: add support for pure json request
            #  add user info if request is via pure json
            if not check_token(request.vars.get('token', None)):
                logger.warn('ALARM!! someone using API ' + str(request.vars))
                return {'status': 'error', 'reason': 'bastard'}
        # save rest
        if request.vars.get('action', None) is not None:
            if request.vars['action'] == 'add':
                result = new_rest(request.vars.rest, auth, True)
                if result['status'] == 'error':
                    logger.warn('error adding new rest')
                    return api_error('Failed to add new rest')
                elif result['status'] == 'OK':
                    return api_success('Rest added')
        return api_error('enf')

    def GET(*args, **vars):
        # lets validate authentication for request
        if not check_token(request.vars.get('token', None)):
            logger.warn('ALARM!! someone using API ' + str(request.vars))
            return {'status': 'error', 'reason': 'bastard'}
        return api_error('enf')

    return locals()


def api_error(msg):
    return {'status': 'error', "msg": msg}


def api_success(msg):
    return {'status': 'OK', 'msg': msg}
