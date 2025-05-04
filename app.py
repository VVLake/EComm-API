from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)
@app.route('/')
def index():
    return 'Ecommerce API is running!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:GodsGrace5@localhost/ecommerce_api'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

# Marshmallow Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# User Endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return users_schema.jsonify(users)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], address=data['address'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    data = request.get_json()
    user.name = data['name']
    user.address = data['address']
    user.email = data['email']
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

# Product Endpoints
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(product_name=data['product_name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    data = request.get_json()
    product.product_name = data['product_name']
    product.price = data['price']
    db.session.commit()
    return product_schema.jsonify(product)

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

# Order Endpoints
@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    new_order = Order(user_id=data['user_id'])
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order)

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['POST'])
def add_product_to_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    if product not in order.products:
        order.products.append(product)
        db.session.commit()
    return order_schema.jsonify(order)

@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
    return jsonify({'message': 'Product removed from order'})

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders_schema.jsonify(orders)

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_by_order(order_id):
    order = Order.query.get(order_id)
    return products_schema.jsonify(order.products)

if __name__ == '__main__':
   with app.app_context():
    db.create_all()
app.run(debug=True)
