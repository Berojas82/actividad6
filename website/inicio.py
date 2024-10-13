from flask import Blueprint, render_template


inicio = Blueprint('inicio', __name__)


@inicio.route('/')
def home():
    return render_template("home.html")