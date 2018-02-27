#!flask/bin/python
from flask import (
    Flask,
    jsonify,
    abort,
    make_response,
    request,
)
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
# import sys

items = [
    {
        'title': 'Milk',
        'description': '',
        'done': False
    },
    {
        'title': 'Cheese',
        'description': 'for pizza',
        'done': False
    },
    {
        "title": "Pizza",
        "description": "pepperoni",
        "done": False,
    },
    {
        "title": "Fruit",
        "description": "apple",
        "done": False,
    },
    {
        "title": "Meat",
        "description": "beef",
        "done": False,
    }
]


app = Flask(__name__)


@app.route('/shopping/setup', methods=['GET'])
def home_page():
    ids = []
    try:
        for item in items:
            ids.append(str(shopping_list.insert(item)))
    except DuplicateKeyError as e:
        abort(400)
    finally:
        return jsonify({'result': ids})


@app.route('/shopping/list', methods=['GET'])
def get_list():
    result = []
    for item in shopping_list.find():
        result.append({
            '_id': str(item['_id']),
            'title': item['title'],
            'description': item['description'],
            'done': item['done']
        })
    return jsonify({'item': result})


@app.route('/shopping/list/<string:item_id>', methods=['GET'])
def get_item(item_id):
    item = dict(shopping_list.find_one_or_404({'_id': ObjectId(item_id)}))
    # print(item, file=sys.stderr)
    output = {
            'title': item['title'],
            'description': item['description'],
            'done': item['done']
        }
    return jsonify({'item': output})


@app.route('/shopping/list', methods=['POST'])
def create_item():
    if not request.json or 'title' not in request.json:
        abort(400)
    item = {
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    _id = str(shopping_list.insert(item))
    return jsonify({'items': _id}), 201


@app.route('/shopping/list/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    item = dict(shopping_list.find_one_or_404({'_id': ObjectId(item_id)}))
    if not request.json:
        abort(400)
    if 'title' not in request.json:
        abort(400)
    if 'description' not in request.json:
        abort(400)
    if 'done' not in request.json:
        abort(400)

    shopping_list.replace_one(
        {'_id': ObjectId(item_id)},
        {
            'title': request.json.get('title', item['title']),
            'description': request.json.get('description', item['description']),
            'done': request.json.get('done', item['done'])
        }
    )
    return jsonify({'items': 'OK'})


@app.route('/shopping/list/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    shopping_list = mongo.db.shopping_list
    shopping_list.find_one_or_404({'_id': ObjectId(item_id)})
    shopping_list.delete_one({'_id': ObjectId(item_id)})
    return jsonify({'result': True})


@app.route('/shopping/list/drop', methods=['DELETE'])
def drop_collection():
    shopping_list.drop()
    return jsonify({'result': 'OK'})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)


if __name__ == '__main__':
    with app.app_context():
        # Config mongodb
        app.config['MONGO_DBNAME'] = 'shopping_list'
        app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/shopping_list'

        mongo = PyMongo(app)
        shopping_list = mongo.db.shopping_list
        try:
            shopping_list.create_index('name', unique=True)
        except DuplicateKeyError as e:
            pass

    app.run(debug=True)
