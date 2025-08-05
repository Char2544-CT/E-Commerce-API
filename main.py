#Import all frameworks/dependencies here
from __future__ import annotations
from datetime import datetime
from flask import Flask, request, jsonify, app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, select, DateTime, Float
from marshmallow import ValidationError
from typing import List
import os

#Init Flask app
app = Flask(__name__)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Cadi11ac2544!@localhost/ecommerce_api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating our Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base, metadata=Base.metadata)
db.init_app(app)
ma = Marshmallow(app)

'''
Creating Tables
'''
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(70))
    address: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    #Creates a one-to-many relationship
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Many-to-one with user and many-to-many with products
    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(
        secondary="order_products",
        back_populates="orders"
    )


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)

    orders: Mapped[List["Order"]] = relationship(
        secondary="order_products",
        back_populates="products"
    )

#Association Table
class OrderProduct(Base):
    __tablename__ = 'order_products'

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)

'''
Use Marshmallow for Schemas and Serialization
'''
#UserSchema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

#Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True

#Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_fk = True

#Init Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True) #Can serialize many User Objects (Like a list)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

'''
Next We Implement CRUD Endpoints
'''

#User Endpoints

#GET/users: Retrieve all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

#GET user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)

    return user_schema.jsonify(user), 200

#POST new user
@app.route('/users', methods=['POST'])
def new_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    create_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email'])
    db.session.add(create_user)
    db.session.commit()

    return user_schema.jsonify(create_user), 201

#PUT/update user by id
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200

#DELETE user by id
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({'message': 'Invalid user id'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted user {id}'}), 200

#Product Endpoints

#GET all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200

#GET products by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)

    return product_schema.jsonify(product), 200

#POST new product
@app.route('/products', methods=['POST'])
def new_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    create_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(create_product)
    db.session.commit()

    return product_schema.jsonify(create_product), 201

#PUT/update product by id
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']

    db.session.commit()
    return product_schema.jsonify(product), 200

#DELETE product by id
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({'message': 'Invalid product id'}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted product {id}'}), 200

#Order Endpoints

#POST/Create new order - MAYBE
@app.route('/orders', methods=['POST'])
def new_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    create_order = Order(order_date=order_data['order_date'], user_id=['user_id'])
    db.session.add(create_order)
    db.session.commit()

    return order_schema.jsonify(create_order), 201

#PUT Add an existing product to an existing order (prevent duplicates)
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    #Code Here
    pass

#DELETE remove an existing product from an existing order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>')
def remove_product():
    #Code Here
    pass

#GET all orders for a user - WRONG
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def orders_for_user(user_id):
    orders_by_user = db.session.get(Order, user_id)

    #return orders_schema.jsonify(orders_by_user), 200
    pass

#GET all products for an order - WRONG
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def products_for_order(order_id):
    query = select(Order, order_id)
    products_in_order = db.session.execute(query).scalars().all()

    #return orders_schema.jsonify(products_in_order), 200
    pass

#Init Database
if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
    app.run(debug=True)