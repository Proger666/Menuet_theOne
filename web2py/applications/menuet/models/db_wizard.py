### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

########################################
db.define_table('t_bot_user_context',
                Field('f_user_id', type='integer',
                      label=T('user id from Telegram')),
                Field('f_username', type='string',
                      label=T('Username')),
                Field('f_last_name', type='string',
                      label=T('user last name')),
                Field('f_first_name', type='string',
                      label=T('user first name')),
                Field('f_last_loc', type='string',
                      label=T('User location')),
                auth.signature, format='%(f_username)s',
                migrate=settings.migrate)
########################################


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

db.define_table('t_network',
                Field('f_name', type='string',
                      label=T('Network Name')),
                Field('f_syn', type='list:string',
                      label=T('synonyms')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_rest_tag',
                Field('f_name', type='string',
                      label=T('Tag Name')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_restaraunt',
                Field('f_q_id', type='string',
                      label=T('q_id')),
                Field('f_f4sqr', type='string',
                      default="https://ru.foursquare.com/v/%D1%88%D0%B8%D0%BA%D0%B0%D1%80%D0%B8/5852d5d10a3d540a0d7aa7a5"
                      ,
                      label=T('f4sqr')),
                Field('f_rating', type='string',
                      label=T('Restaraunt rating')),
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_public_phone', type='list:string',
                      label=T('Phone')),
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
                Field('f_locked_by', 'reference:auth_user',
                      label=T('Locked by')),
                Field('f_coordinateX', type='string',
                      label=T('Coord X')),
                Field('f_coordinateY', type='string',
                      label=T('Coord Y')),
                Field('f_is_network', type='boolean',
                      label=T('Is Network?')),
                Field('f_network_name', 'reference:t_network', default=5,
                      label=T('Network_Name')),
                Field('f_image', 'upload'),
                Field('f_tags', 'list:reference t_rest_tag',
                      label=T('Rest tags')),
                Field('f_img', type='blob',
                      label=T('img')),
                Field('f_md5hash', type='string',
                      label=T('hash')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################
db.define_table('t_item_tag',
                Field('f_name'),
                auth.signature,
                format='%(f_name)s')
########################################
db.define_table('t_menu_tag',
                Field('f_name'),
                auth.signature,
                format='%(f_name)s')
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
                Field('f_normal_form', type='string',
                      label=T('Name')),
                Field('f_curate', type='boolean',
                      label=T('Curate')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_step',
                Field('f_ingr', 'reference:t_ingredient', required=True,
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
                Field('t_step', 'reference:t_step', required=True, notnull=True,
                      label=T('step link')),
                Field('t_recipe', 'reference:t_recipe', required=True, notnull=True,
                      label=T('recipe link')),
                auth.signature,
                migrate=settings.migrate)
########################################

db.define_table('t_portion',
                Field('f_name', type='string',
                      label=T('Name')),
                auth.signature,
                format='%(f_name)s',
                migrate=settings.migrate)
########################################


db.define_table('t_item',
                Field('f_name', type='string',
                      label=T('Item Name')),
                Field('f_rating', type='string',
                      label=T('Item rating')),
                Field('f_desc', type='string',
                      label=T('Item desc')),
                Field('f_cal', type='integer', default=0,
                      label=T('Calories')),
                Field('f_t_start', type='time', default='00:00:00',
                      label=T('work from ....')),
                Field('f_t_end', type='time', default='00:00:00',
                      label=T('work till ....')),
                Field('f_recipe', 'reference:t_recipe',
                      label=T('recipe link')),
                Field('f_weight', type='integer', default=0,
                      label=T('Weight')),
                Field('f_unit', 'reference:t_unit', default=1,
                      label=T('Unit')),

                Field('f_tags', 'list:reference t_item_tag', label=T('Tags')),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################
db.define_table('t_item_prices',
                Field('f_price', type='string',
                      label=T('Price')),
                Field('f_item', 'reference:t_item',
                      label=T('Item')),
                Field('f_portion', 'reference:t_portion',
                      label=T('Linked portion')),
                auth.signature, format='%(f_portion)s',
                migrate=settings.migrate)
########################################
db.define_table('t_item_price_archive',
                Field('f_price', type='string',
                      label=T('Price')),
                Field('f_item', 'reference:t_item',
                      label=T('Item')),
                Field('f_portion', 'reference:t_portion',
                      label=T('Linked portion archive')),
                auth.signature, format='%(f_portion)s',
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
                Field('f_tags', 'list:reference t_menu_tag', label=T('Tags')),
                Field('f_network', 'reference:t_network',
                      label=T('Network if is networks menu'), default=5),
                auth.signature, format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_rest_menu',
                Field('t_menu', 'reference:t_menu', notnull=True,
                      label=T('Menu link')),
                Field('t_rest', 'reference:t_restaraunt', notnull=True,
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
