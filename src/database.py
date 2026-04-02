from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    price = db.Column(db.Integer)
    description = db.Column(db.Text)
    impact = db.Column(db.Integer)
    image = db.Column(db.String(16))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32))
    username = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(64))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def signup(username, password):
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return new_user


INVENTORY = [
    {
        "name": "Bitcoin",
        "price": 6123456,
        "description": "This is just bitcoin.",
        "impact": 11,
        "image": "bitcoin.png",
    },
    {
        "name": "Ethereum",
        "price": 307996,
        "description": "This is just ethereum.",
        "impact": 8,
        "image": "ethereum.png",
    },
    {
        "name": "BNB",
        "price": 59595,
        "description": "This is just BNB.",
        "impact": 3,
        "image": "bnb.png",
    },
    {
        "name": "Solana",
        "price": 12442,
        "description": "This is just solana.",
        "impact": 6,
        "image": "solana.png",
    },
    {
        "name": "Quant",
        "price": 9800,
        "description": "This is just quant.",
        "impact": 4,
        "image": "quant.png",
    },
]

USERS = [
    {
        "id": 0,
        "email": "admin@admin.com",
        "username": "admin",
        "password_hash": generate_password_hash("admin"),
    }
]
