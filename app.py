from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenwolf.db'  # Free local database
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Change this in production!
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='player')  # player, admin, developer

# Game Model
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, default=0.0)  # Free or paid

# Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

# Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity={'id': user.id, 'role': user.role}, expires_delta=datetime.timedelta(days=1))
    return jsonify({'access_token': access_token})

# Get All Games (Requires Login)
@app.route('/games', methods=['GET'])
@jwt_required()
def get_games():
    games = Game.query.all()
    return jsonify([{'id': game.id, 'title': game.title, 'price': game.price} for game in games])

if __name__ == '__main__':
    app.run(debug=True)
