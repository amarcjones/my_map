from flask import Flask, render_template, request, url_for, redirect, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import UserForm

from sqlalchemy.exc import IntegrityError
# from sqlalchemy import func
# import os


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/my-map-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super secret'
db = SQLAlchemy(app)

# Timing matters - the User class, can't be imported from models.py before that file has access to db and bcrypt from this file.
from models import User

# Class(es) ------------------------------
# Moved classes to models.py


# Routes ------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            new_user = User(form.data['username'], form.data['password'])
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as e:
        	flash("Invalid submission.  Please try again.")
        	return render_template('signup.html', form=form)
        return redirect(url_for('users.login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods = ["GET", "POST"])
def login():
    form = UserForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.authenticate(form.data['username'], form.data['password'])
        if user:
                session['user_id'] = user.id
                flash("You've successfully logged in!")
                return redirect(url_for('users.welcome'))
        flash("Invalid credentials. Please try again.")
    return render_template('login.html', form=form)


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


# Environment (Production or Development) ------------------------------
# if os.environ.get('ENV') == 'production':
#     app.config.from_object('config.ProductionConfig')
#     # notice here that we are configuring from a file called "config" and a class inside called "ProductionConfig"
# else:
#     app.config.from_object('config.DevelopmentConfig')

# Run ------------------------------
if __name__ == '__main__':
	app.run(debug=True)

