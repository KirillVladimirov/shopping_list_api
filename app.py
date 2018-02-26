#!flask/bin/python
from flask import (
    Flask,
    jsonify,
    abort,
    make_response,
    request,
)
from flask_pymongo import PyMongo

items = [
    {
        'id': 1,
        'title': 'Milk',
        'description': '',
        'done': False
    },
    {
        'id': 2,
        'title': 'Cheese',
        'description': 'for pizza',
        'done': False
    },
    {
        "id": 3,
        "title": "Pizza",
        "description": "pepperoni",
        "done": False,
    },
    {
        "id": 4,
        "title": "Fruit",
        "description": "apple",
        "done": False,
    },
    {
        "id": 5,
        "title": "Meat",
        "description": "beef",
        "done": False,
    }
]

app = Flask(__name__)
mongo = PyMongo(app)


@app.route('/shopping/admin', methods=['GET'])
def home_page():
    shopping_list = mongo.db.shopping.find({'online': True})
    return jsonify({'items': shopping_list})


@app.route('/shopping/list', methods=['GET'])
def get_list():
    return jsonify({'items': items})


@app.route('/shopping/list/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
    return jsonify({'items': item[0]})


@app.route('/shopping/list', methods=['POST'])
def create_item():
    if not request.json or 'title' not in request.json:
        abort(400)
    item = {
        'id': items[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    items.append(item)
    return jsonify({'items': item}), 201


@app.route('/shopping/list/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' not in request.json:
        abort(400)
    if 'description' not in request.json:
        abort(400)
    if 'done' not in request.json:
        abort(400)
    item[0]['title'] = request.json.get('title', item[0]['title'])
    item[0]['description'] = request.json.get('description', item[0]['description'])
    item[0]['done'] = request.json.get('done', item[0]['done'])
    return jsonify({'items': item[0]})


@app.route('/shopping/list/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
        items.remove(item[0])
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)


if __name__ == '__main__':
    app.run(debug=True)
