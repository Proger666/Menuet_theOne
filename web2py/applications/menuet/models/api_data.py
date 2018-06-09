class result_object:
    '''This objects '''

    def __init__(self,item_id,item_name,rest_id,item_price,item_rating,menu_id,item_weight,rest_name,rest_addr,rest_distance,rest_phone,f4sqr_link,item_ingrs,rest_long,rest_lat, search_score):
        self.item_id=item_id
        self.item_name=item_name
        self.rest_id=rest_id
        self.item_price=item_price
        self.item_rating=item_rating
        self.menu_id=menu_id
        self.item_weight=item_weight
        self.rest_name=rest_name
        self.rest_addr=rest_addr
        self.rest_distance=rest_distance
        self.rest_phone=rest_phone
        self.f4sqr_link=f4sqr_link
        self.item_ingrs=item_ingrs
        self.rest_long = rest_long
        self.rest_lat = rest_lat
        self.search_score = search_score

class internalSearchCache:
    def __init__(self):
        self.name = ""
