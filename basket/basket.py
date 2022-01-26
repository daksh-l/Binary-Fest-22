from decimal import Decimal

from store.models import Product


class Basket():  # https://docs.djangoproject.com/en/4.0/topics/http/sessions/
    def __init__(self, request):
        self.session = request.session
        basket = self.session.get('skey')  # check if they have session datas
        if 'skey' not in request.session:
            basket = self.session['skey'] = {}  # building the new session
        self.basket = basket  # basket is whatever there is in the session

    def add(self, product, qty): # Adding and updating the users basket session data
        product_id = str(product.id)

        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        else:
            self.basket[product_id] = {'price': str(product.price), 'qty': qty}

        self.save()

    def __iter__(self):   # Collect the product_id in the session data to query the database
        product_ids = self.basket.keys()
        products = Product.products.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item

    def __len__(self): # Get the basket data and count the quantity of items
        return sum(item['qty'] for item in self.basket.values())

    def update(self, product, qty): # update values
        product_id = str(product)
        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        self.save()

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['qty'] for item in self.basket.values())

    def delete(self, product):  # delete item
        product_id = str(product)

        if product_id in self.basket:
            del self.basket[product_id]
            print(product_id)
            self.save()

    def save(self):
        self.session.modified = True
