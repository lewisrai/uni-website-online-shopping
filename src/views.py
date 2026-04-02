from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from database import Product, User
from forms import BasketForm, CheckoutForm, LoginForm, ProductForm, SignupForm


def create_session_basket():
    if "basket" not in session:
        session["basket"] = dict()


def format_price(price):
    return f"£{price / 100:.2f}"


def create_product_with_form(product):
    product.price = format_price(product.price)
    form = ProductForm(prefix=product.name)

    return {"info": product, "form": form}


def update_product_form(product):
    if not product["form"].submit.data:
        return

    if not product["form"].validate_on_submit():
        return

    if product["info"].name not in session["basket"]:
        session["basket"][product["info"].name] = 0

    session["basket"][product["info"].name] += product["form"].amount.data
    session.modified = True


def generate_basket_info():
    basket_info = []

    for item, amount in session["basket"].copy().items():
        product = Product.query.filter_by(name=item).first()
        product = {
            "info": product,
            "amount": amount,
            "price": 0,
            "form": None,
        }

        basket_info.append(product)

    return basket_info


def calculate_cost_basket(detailed_basket):
    total_cost = 0

    for product in detailed_basket:
        product["price"] = product["info"].price * product["amount"]
        total_cost += product["price"]

        product["price"] = format_price(product["price"])

    return total_cost


views = Blueprint(__name__, "views")


@views.route("/", methods=["GET", "POST"])
def index():
    create_session_basket()

    order = request.args.get("order", default="name")

    products = []

    for product in Product.query.all():
        products.append(create_product_with_form(product))

    match order:
        case "price":
            products = sorted(products, key=lambda x: x["info"].price)
        case "impact":
            products = sorted(products, key=lambda x: x["info"].impact_degree)
        case _:
            products = sorted(products, key=lambda x: x["info"].name)

    for product in products:
        update_product_form(product)

    return render_template("index.html", products=products)


@views.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    create_session_basket()

    product_query = Product.query.filter_by(id=product_id).first()

    if product_query is None:
        return render_template("product_null.html")

    product = create_product_with_form(product_query)
    update_product_form(product)

    return render_template("product.html", product=product)


@views.route("/basket", methods=["GET", "POST"])
def basket():
    create_session_basket()

    basket_info_temp = generate_basket_info()
    basket_info = []

    for product in basket_info_temp:
        name = product["info"].name
        product["form"] = BasketForm(prefix=name)

        if product["form"].increase.data:
            session["basket"][name] += 1
            product["amount"] += 1
            basket_info.append(product)
        elif product["form"].decrease.data:
            if product["amount"] - 1 > 0:
                session["basket"][name] -= 1
                product["amount"] -= 1
                basket_info.append(product)
            else:
                session["basket"].pop(name)
        elif product["form"].remove.data:
            session["basket"].pop(name)
        else:
            basket_info.append(product)

    total_cost = calculate_cost_basket(basket_info)
    total_cost = format_price(total_cost)

    session.modified = True

    return render_template("basket.html", basket=basket_info, cost=total_cost)


@views.route("/signup", methods=["GET", "POST"])
def signup():
    signup_form = SignupForm()

    if not signup_form.validate_on_submit():
        return render_template("signup.html", form=signup_form, error="")

    user_check = User.query.filter_by(username=signup_form.username.data).first()

    if user_check is not None:
        return render_template("signup.html", form=signup_form, error="Username exists")

    user = User.signup(signup_form.username.data, signup_form.confirm.data)

    login_user(user, True)

    return redirect(url_for("views.index"))


@views.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if not login_form.validate_on_submit():
        return render_template("login.html", form=login_form, error="")

    user = User.query.filter_by(username=login_form.username.data).first()

    if user is None or not user.verify_password(login_form.password.data):
        return render_template("login.html", form=login_form, error="Incorrect details")

    login_user(user, True)

    destination = request.args.get("next", default=url_for("views.index"))

    return redirect(destination)


@views.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    checkout_form = CheckoutForm()

    basket_info = generate_basket_info()
    total_cost = calculate_cost_basket(basket_info)
    total_cost = format_price(total_cost)

    if not checkout_form.validate_on_submit():
        return render_template("checkout.html", form=checkout_form, cost=total_cost)

    session["basket"].clear()
    return render_template("checkout_success.html", basket=basket_info, cost=total_cost)


@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))
