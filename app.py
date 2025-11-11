import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from pymongo import MongoClient
from passlib.hash import argon2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- App Configuration ---
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Extensions Initialization ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# --- MongoDB Connection ---
# We initialize this client directly as it doesn't need a Flask extension
mongo_client = MongoClient(os.environ.get("MONGO_URI"))
mongo_db = mongo_client.get_database() # Uses the DB name from the URI

# Import models *after* db is defined to avoid circular imports
from models import User

# --- API Endpoints ---

@app.route("/")
def index():
    return jsonify(message="Trendify API is running!")

# --- Auth Endpoints (Ref: Inicio Sesión Usuarios.pdf) ---

@app.route("/auth/register", methods=["POST"])
def register():
    """
    Function: Register a new user.
    Ref: 'server_architecture.md'
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password using Argon2
    hashed_password = argon2.hash(password)
    
    new_user = User(email=email, hashed_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": f"User {email} created successfully"}), 201

@app.route("/auth/login", methods=["POST"])
def login():
    """
    Function: Authenticate a user and return a JWT.
    Ref: 'server_architecture.md'
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Verify the password using Argon2
    if argon2.verify(password, user.hashed_password):
        # Create a new access token
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# --- Trends Endpoints (Ref: Tecnologías a utilizar...pdf) ---

@app.route("/trends/fashion", methods=["GET"])
@jwt_required() # Protect this route
def get_fashion_trends():
    """
    Function: Get trends from MongoDB.
    Ref: 'server_architecture.md'
    This API only READS from MongoDB. The heavy lifting
    was already done by Celery.
    """
    current_user_id = get_jwt_identity()
    app.logger.info(f"User {current_user_id} is accessing fashion trends.")
    
    # Access the pre-processed trends collection
    trends_collection = mongo_db["processed_trends"]
    
    # Find results, sort by score, limit to 10
    results = trends_collection.find(
        {"category": "fashion"}
    ).sort("score", -1).limit(10)
    
    # Convert MongoDB docs (which include _id) to a serializable list
    output = []
    for r in results:
        output.append({
            "trend": r.get("name"),
            "score": r.get("score")
        })
        
    return jsonify(output), 200

# --- Forum Endpoints (Example) ---

@app.route("/forum/posts", methods=["POST"])
@jwt_required()
def create_post():
    """
    Function: Create a new forum post (writes to PostgreSQL).
    Ref: 'server_architecture.md'
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "Title and content are required"}), 400
        
    # Here you would create a 'Post' model, link it to the user,
    # and save it to PostgreSQL.
    # new_post = Post(title=data["title"], content=data["content"], user_id=current_user_id)
    # db.session.add(new_post)
    # db.session.commit()
    
    return jsonify({"message": "Post created successfully (endpoint placeholder)"}), 201


if __name__ == "__main__":
    # We use 'flask run' in development, not this.
    # Gunicorn will run 'app:app' in production.
    pass
