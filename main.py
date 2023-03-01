import os

from flask import Flask, request, jsonify, send_file
import uuid
import requests

app = Flask(__name__)

products = dict()


@app.get('/products')
def get_products():
    return jsonify(list(products.values()))


@app.get('/products/<product_id>')
def get_product(product_id):
    if product_id in products.keys():
        return products[product_id], 200

    return {'error': 'The requested product was not found'}, 404


@app.get('/products/<product_id>/image')
def get_product_image(product_id):
    if product_id in products.keys():
        return send_file('{}.jpg'.format(product_id)), 200

    return {'error': 'The requested product was not found'}, 404


@app.post('/products')
def add_product():
    if request.is_json:
        if 'name' not in request.get_json().keys() or \
           'description' not in request.get_json().keys() or \
           'url' not in request.get_json().keys() or \
           len(list(request.get_json().keys())) != 3:

            return {'error': 'Wrong format of data'}, 400

        product = {
            'id': str(uuid.uuid4()),
            'name': request.get_json()['name'],
            'description': request.get_json()['description'],
            'url': request.get_json()['url']
        }
        r = requests.get(product['url'], allow_redirects=True)
        open('{}.jpg'.format(product['id']), 'wb').write(r.content)
        products[product['id']] = product
        return product, 201

    return {'error': 'POST request must be JSON'}, 415


@app.put('/products/<product_id>')
def update_product(product_id):
    if product_id in products.keys() and request.is_json:
        if 'name' not in request.get_json().keys() or \
           'description' not in request.get_json().keys() or \
           'url' not in request.get_json().keys() or \
           len(list(request.get_json().keys())) != 3:

            return {'error': 'Wrong format of data'}, 400

        products[product_id]['name'] = request.get_json()['name']
        products[product_id]['description'] = request.get_json()['description']
        products[product_id]['url'] = request.get_json()['url']
        os.remove('{}.jpg'.format(product_id))
        r = requests.get(products[product_id]['url'], allow_redirects=True)
        open('{}.jpg'.format(products[product_id]['id']), 'wb').write(r.content)
        return products[product_id], 200
    elif product_id not in products.keys():
        return {'error': 'The requested product was not found'}, 404

    return {'error': 'PUT request must be JSON'}, 415


@app.delete('/products/<product_id>')
def delete_product(product_id):
    if product_id in products.keys():
        products.pop(product_id)
        os.remove('{}.jpg'.format(product_id))
        return {}, 204

    return {'error': 'The requested product was not found'}, 404
