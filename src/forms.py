from flask_wtf import FlaskForm
from datetime import date
from wtforms import EmailField, IntegerField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from wtforms.validators import ValidationError


def card_number_with_separators(number_split):
    if len(number_split) != 4:
        return False

    for split in number_split:
        if len(split) != 4 or not split.isnumeric():
            return False

    return True


def card_number(form, field):
    number = field.data

    if len(number) == 19:
        number_split_dash = number.split("-")
        number_split_space = number.split(" ")

        check1 = card_number_with_separators(number_split_dash)
        check2 = card_number_with_separators(number_split_space)

        if not (check1 or check2):
            raise ValidationError("Invalid card number")
    elif len(number) == 16:
        if not number.isnumeric():
            raise ValidationError("Invalid card number")
    else:
        raise ValidationError("Invalid card number")


def expiry_month(form, field):
    month = field.data

    if len(month) != 2:
        raise ValidationError("Invalid month")

    if month[0] == "0":
        month = month[1]

    if not month.isnumeric():
        raise ValidationError("Invalid month")


def expiry_year(form, field):
    year = field.data

    if len(year) != 2:
        raise ValidationError("Invalid year")

    if year[0] == "0":
        year = year[1]

    if not year.isnumeric():
        raise ValidationError("Invalid year")

    if int(year) + 2000 < date.today().year:
        raise ValidationError("Invalid year")


def cvv(form, field):
    number = field.data

    if len(number) != 3 or not number.isnumeric():
        raise ValidationError("Invalid cvv")


class ProductForm(FlaskForm):
    amount = IntegerField("", validators=[NumberRange(min=1)])
    submit = SubmitField("Add to basket")


class BasketForm(FlaskForm):
    increase = SubmitField("Add 1")
    decrease = SubmitField("Remove 1")
    remove = SubmitField("Remove all")


class SignupForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Length(1, 32)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 32)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CheckoutForm(FlaskForm):
    number = StringField("Card number", validators=[card_number])
    expiry_month = StringField("Expiry month", validators=[expiry_month])
    expiry_year = StringField("Expiry year", validators=[expiry_year])
    cvv = StringField("CVC", validators=[cvv])
    pay = SubmitField("Pay")
