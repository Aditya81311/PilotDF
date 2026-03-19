from flask import Flask , render_template, Blueprint, redirect, url_for

index_bp = Blueprint('index',__name__)

@index_bp.route("/")
def dashboard():
    return render_template("index.html")