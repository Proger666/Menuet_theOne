@auth.requires_membership('admin')
def statistics():
    result_list = []

    result_list = (db(db.t_restaraunt).select()).as_json()

    return result_list

@auth.requires_membership('admin')
def report():
    return locals()