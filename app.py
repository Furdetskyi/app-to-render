import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Конфігурація для JWT
app.config["JWT_SECRET_KEY"] = "12345"  # Замініть на реальний секретний ключ
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Термін дії токену (в секундах)

# Ініціалізація JWT
jwt = JWTManager(app)

# Простий список користувачів для демонстрації
users = []

# Логін та отримання токена
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Простий приклад перевірки
    user = next((user for user in users if user['username'] == data['username'] and user['password'] == data['password']), None)
    if user:
        access_token = create_access_token(identity=user['username'])
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Створення нового користувача
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = {
        'username': data['username'],
        'password': data['password']
    }
    users.append(new_user)
    return jsonify({"message": "User added successfully"}), 201

# Отримання всіх користувачів (захищено)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    return jsonify({"users": users})

# Отримання користувача за username (захищено)
@app.route('/users/<string:username>', methods=['GET'])
@jwt_required()
def get_user(username):
    user = next((user for user in users if user['username'] == username), None)
    if user:
        return jsonify({"username": user['username']})
    return jsonify({"message": "User not found"}), 404

# Запуск додатку
if __name__ == "__main__":
    port = os.getenv("PORT", 5000)  # Встановлює порт з середовища, якщо є
    print(f"Running app on port {port}")  # Лог для перевірки
    app.run(debug=True, host="0.0.0.0", port=int(port))  # Прив'язка до всіх інтерфейсів
