from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from database import db as database, Product, User, INVENTORY, USERS
from views import views


def load_default_database(app, database):
    with app.app_context():
        database.create_all()

        for id, product in enumerate(INVENTORY):
            if Product.query.filter_by(id=id).first() is None:
                database.session.add(
                    Product(
                        id=id,
                        name=product["name"],
                        price=product["price"],
                        description=product["description"],
                        impact=product["impact"],
                        image=product["image"],
                    )
                )

        for id, user in enumerate(USERS):
            if User.query.filter_by(id=id).first() is None:
                database.session.add(
                    User(
                        id=id,
                        email=user["email"],
                        username=user["username"],
                        password_hash=user["password_hash"],
                    )
                )

        database.session.commit()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "i need this for forms to work"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.sqlite3"
    app.register_blueprint(views, url_prefix="/")

    Bootstrap(app)

    database.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "views.login"

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    load_default_database(app, database)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")
else:
    app = create_app()
