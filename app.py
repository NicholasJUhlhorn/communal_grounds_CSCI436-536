# Nicholas J Uhlhorn
# November 2025

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/profile_creation")
def profile_creation():
    return render_template('profile_creation.html')

@app.route("/my_projects")
def my_projects():
    return render_template('my_projects.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

#Ideally, the functionality of this should change depening on the project itself
@app.route("/project")
def project():
    return render_template('project.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
