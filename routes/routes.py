# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint
from flask import Flask, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template('home.html')

@main_bp.route("/about")
def about():
    return render_template('about.html')

@main_bp.route("/profile_creation")
def profile_creation():
    return render_template('profile_creation.html')

@main_bp.route("/my_projects")
def my_projects():
    return render_template('my_projects.html')

@main_bp.route("/profile")
def profile():
    return render_template('profile.html')

#Ideally, the functionality of this should change depening on the project itself
@main_bp.route("/project")
def project():
    return render_template('project.html')
