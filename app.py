import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)

# Configuration for SQLAlchemy and JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://root:Valikf2005@34.79.21.6:5432/test'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "12345"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Token expiration (in seconds)

# Initialize components
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User Model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Product Model
class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id', ondelete='CASCADE'))  # Cascade delete
    user = db.relationship('UserModel', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"<Product {self.name}>"

# Create all tables in the database
with app.app_context():
    db.create_all()

# Login and getting the token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = UserModel.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:  # Simple example check
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Add User
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = UserModel(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully"}), 201

# Get User by ID (protected)
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    return jsonify({"id": user.id, "username": user.username, "password": user.password})

# Update User (protected)
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data['username']
    user.password = data['password']
    db.session.commit()
    return jsonify({"message": "User updated successfully"})

# Get all Users (protected)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = UserModel.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify({"users": users_list})

# Delete User (protected)
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})

# Add Product (protected)
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_product = ProductModel(
        name=data['name'], 
        brand=data['brand'], 
        price=data['price'], 
        user_id=current_user_id
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

# Get Product by ID (protected)
@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price
    })

# Update Product (protected)
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data['name']
    product.brand = data['brand']
    product.price = data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

# Get all Products (protected)
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = ProductModel.query.all()
    products_list = [{"id": product.id, "name": product.name, "brand": product.brand, "price": product.price} for product in products]
    return jsonify({"products": products_list})

# Delete Product (protected)
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})

# Run the app on the correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable, default to 5000
    app.run(debug=True, host="0.0.0.0", port=port)  # Bind to 0.0.0.0 for external access
Key Changes:
