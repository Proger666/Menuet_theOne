### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_seosanal_type',
                Field('f_name', type='string',
                      label=T('Name of the type')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_menu_type',
                Field('f_name', type='string',
                      label=T('Name of the type')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_restaraunt',
                Field('f_q_id', type='string',
                      label=T('q_id')),
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_active', type='boolean', default=True,
                      label=T('Active?')),
                Field('f_address', type='string',
                      label=T('Address')),
                Field('f_town', type='string',
                      label=T('Town')),
                Field('f_latitude', type='string',
                      label=T('Latitude')),
                Field('f_longitude', type='string',
                      label=T('Longitude')),
                Field('f_type', type='string',
                      label=T('Type')),
                Field('f_coordinateX', type='string',
                      label=T('Coord X')),
                Field('f_coordinateY', type='string',
                      label=T('Coord Y')),
                Field('f_is_network', type='boolean',
                      label=T('Is Network?')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                Field('f_md5hash', type='string',
                      label=T('hash')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('tag',
                Field('name'),
                auth.signature,
                format='%(name)s')
########################################

db.define_table('t_unit',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_description', type='string', label=T('Description')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_ingredient',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_step',
                Field('f_ingr', 'reference:t_ingredient',
                      label=T('ingr link')),
                Field('f_qty', type='integer', default=0,
                      label=T('Quantity')),
                Field('f_unit', 'reference:t_unit',
                      label=T('Unit')),
                auth.signature,
                format='%(f_ingr)s',
                migrate=settings.migrate)

########################################
db.define_table('t_recipe',
                Field('f_name', type='string',
                      label=T('Name')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)

########################################

db.define_table('t_step_ing',
                Field('t_step', 'reference:t_step',
                      label=T('step link')),
                Field('t_recipe', 'reference:t_recipe',
                      label=T('recipe link')),
                auth.signature,
                migrate=settings.migrate)

########################################


db.define_table('t_item',
                Field('f_name', type='string',
                      label=T('Item Name')),
                Field('f_price', type='integer', default=0,
                      label=T('Price Name')),
                Field('f_recipe', 'reference:t_recipe',
                      label=T('recipe link')),
                Field('f_weight', type='integer', default=0,
                      label=T('Weight')),
                Field('f_unit', 'reference:t_unit',
                      label=T('Unit')),
                Field('tags', 'list:reference tag'),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################
db.define_table('t_item_price_archive',
                Field('f_price', type='integer',
                      label=T('Old price')),
                Field('f_item', 'reference:t_item',
                      label=T('Linked Item')),
                auth.signature, format='%(f_price)s',
                migrate=settings.migrate)
########################################
########################################
db.define_table('t_menu',
                Field('f_name', type='string',
                      label=T('Menu Name')),
                Field('f_comment', type='string',
                      label=T('Comment for menu')),
                Field('f_current', type='boolean', default=False,
                      label=T('Current?')),
                Field('f_seosanal', type='boolean', default=False,
                      label=T('Seosanal?')),
                Field('f_type', 'list:reference t_menu_type',
                      label=T('Menu Type')),
                Field('f_seosanal_type', 'list:reference t_seosanal_type',
                      label=T('Seosanal Type')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_rest_menu',
                Field('t_menu', 'reference:t_menu',
                      label=T('Menu link')),
                Field('t_rest', 'reference:t_restaraunt',
                      label=T('Restaraunt link')),
                auth.signature,
                migrate=settings.migrate)
########################################

db.define_table('t_menu_item',
                Field('t_menu', 'reference:t_menu',
                      label=T('menu link')),
                Field('t_item', 'reference:t_item',
                      label=T('item link')),
                auth.signature,
                migrate=settings.migrate)
########################################
