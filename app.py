from flask import Flask, render_template, request, url_for, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from forms import UserForm
from functools import wraps

from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
bcrypt = Bcrypt(app)
modus = Modus(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/my-map-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Ill never tell'
db = SQLAlchemy(app)


login_manager.login_view = "login"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Decorators ------------------------------
def ensure_correct_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if kwargs.get('id') != current_user.id:
            flash("Not Authorized")
            return redirect(url_for('home'))
        return fn(*args, **kwargs)
    return wrapper


# Class(es) ------------------------------
# Moved classes to models.py
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('UTF-8')

    # @classmethod
    # def authenticate(cls, username, password):
    #     found_user = cls.query.filter_by(username = username).first()
    #     if found_user:
    #         authenticated_user = bcrypt.check_password_hash(found_user.password, password)
    #         if authenticated_user:
    #             return found_user 
    #     return False

# Routes ------------------------------
@app.route('/')
@login_required
def home():
    return render_template('home.html')


app.route('/signup', methods =["GET", "POST"])
def signup():
    form = UserForm(request.form)
    if form.validate():
        try:
            new_user = User(form.data['username'], form.data['password'])
            db.session.add(new_user)
            db.session.commit()
            # session['user_id'] = new_user.id
            login_user(new_user) # replaces above
        except IntegrityError as e:
            flash("Username already taken")
            return render_template('signup.html', form=form)
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


@app.route('/login', methods = ["GET", "POST"])
def login():
    form = UserForm(request.form)
    if form.validate():
        found_user = User.query.filter_by(username = form.data['username']).first()
        if found_user:
            authenticated_user = bcrypt.check_password_hash(found_user.password, form.data['password'])
            if authenticated_user:
                # session['user_id'] = found_user.id
                login_user(found_user) # replaces above
                flash("You are now logged in!")
                return redirect(url_for('home'))
    if form.is_submitted():
        flash("Invalid Credentials")
    return render_template('login.html', form=form)


@app.route('/<int:id>/edit')
@login_required
@ensure_correct_user
def edit(id):
    form = UserForm()
    return render_template('edit.html', form=form, user=User.query.get(id))


@app.route('/<int:id>', methods =["GET", "PATCH", "DELETE"])
@login_required
@ensure_correct_user
def show(id):
    found_user = User.query.get(id)
    if request.method == b"PATCH":
        form = UserForm(request.form)
        if form.validate():
            found_user.username = form.data['username']
            found_user.password = bcrypt.generate_password_hash(form.data['password']).decode('UTF-8')
            db.session.add(found_user)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('edit.html', form=form, user=found_user)
    if request.method == b"DELETE":
        db.session.delete(found_user)
        db.session.commit()
        # session.pop('user_id')
        logout_user() # replaces session.pop
        return redirect(url_for('home'))
    return render_template('show.html', user=found_user)


@app.route('/logout')
@login_required
def logout():
    flash("Logged out!")
    # session.pop('user_id') replaced by logout_user()
    logout_user()
    return redirect(url_for('login'))


# Environment (Production or Development) ------------------------------
# if os.environ.get('ENV') == 'production':
#     app.config.from_object('config.ProductionConfig')
#     # notice here that we are configuring from a file called "config" and a class inside called "ProductionConfig"
# else:
#     app.config.from_object('config.DevelopmentConfig')

# Run ------------------------------
if __name__ == '__main__':
	app.run(debug=True)

