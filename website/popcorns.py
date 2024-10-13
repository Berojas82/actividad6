from flask import Flask, Blueprint, render_template
popcorns = Blueprint("popcorn", __name__)

@popcorns.route("/popcorn")
def popcorn():
    return render_template("popcorn.html")