from flask import *
from flask import g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import sqlite3
RETRIEVE_ENTRIES = "SELECT * FROM Post"
def retrieve_entries():
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(RETRIEVE_ENTRIES)
        return cursor.fetchall()
#Directory Database
dbdir = "sqlite:///"+os.path.abspath(os.getcwd()) + "/database.db"

#The name of the app
app = Flask('ALIENBLOCK')
app.secret_key="K0ky1ePw2aELxUrBmM6by7n9TVDrlPKHrFZXNQf5Z3EpX9860m"
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#Model USER
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
#Model POST
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    content = db.Column(db.Text)
@app.route('/home', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        new_post = Post(content=request.form["content"], date=datetime.datetime.today().strftime("%b %d"))
        db.session.add(new_post)
        db.session.commit()
    return render_template("home.html", entries=retrieve_entries())
#This is index
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for("login"))

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            return redirect(url_for("home"))
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"], method="sha256") 
        new_user = Users(username=request.form["username"], email=request.form["email"], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template('register.html')

#If the path or url is not correct return a personalized page for error 404
@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['home']:
        return redirect(url_for("login"))

@app.errorhandler(404)
def error(errorparam):
    return render_template('404.html'), 404

#Run the server with port especific and mode debug
if __name__ == "__main__":
    db.create_all()
    app.run(port=80, debug=True)
