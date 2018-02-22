# -*- coding: utf-8 -*-
### required - do no delete

response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T(u'Начало'),URL('core','rest')==URL(),URL('core','rest'),[]),
]