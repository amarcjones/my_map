from flask import Flask, render_template, request, url_for, redirect, flash
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
# login_manager.login_message = "Please log in!"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Decorators ------------------------------
def ensure_correct_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # print(current_user.id)
        if kwargs.get('id') != current_user.id:
            flash("Not Authorized")
            return redirect(url_for('home'))
        return fn(*args, **kwargs)
    return wrapper


# Class(es) ------------------------------
# Moved classes to models.py
# spots = db.Table('spots',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
#     db.Column('loc_id', db.Integer, db.ForeignKey('locations.loc_id'))
# )

spots = db.Table('spots',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('loc_id', db.Integer, db.ForeignKey('locations.id')),
    # PrimaryKeyConstraint('user_id', 'loc_id')
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    visits = db.relationship('Location', secondary=spots, backref=db.backref('visitors', lazy='joined'))

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('UTF-8')


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    addr = db.Column(db.Text)
    icon = db.Column(db.Text)
    ph_domestic = db.Column(db.Text)
    ph_intl = db.Column(db.Text)
    website = db.Column(db.Text)
    lat = db.Column(db.Numeric(12,7))
    lng = db.Column(db.Numeric(12,7))


    def __init__(self, name, addr, icon, ph_domestic, ph_intl, website, lat, lng):
        self.name = name
        self.addr = addr
        self.icon = icon
        self.ph_domestic = ph_domestic
        self.ph_intl = ph_intl
        self.website = website
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return "{} location ".format(self.name)



# class Computer(db.Model):
#     __tablename__ = "computers" # table name will default to name of the model

#     # Create the three columns for our table
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text)
#     memory_in_gb = db.Column(db.Integer)

#     # define what each instance or row in the DB will have (id is taken care of for you)
#     def __init__(self, name, memory_in_gb):
#         self.name = name
#         self.memory_in_gb = memory_in_gb

#     # this is not essential, but a valuable method to overwrite as this is what we will see when we print out an instance in a REPL.
#     def __repr__(self):
#         return "This {} has {} GB of memory".format(self.name, self.memory_in_gb)    


# Routes ------------------------------
@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/signup', methods =["GET", "POST"])
def signup():
    # print("test")
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


# @app.route('/map')
# def map():
#     marked_locations = Location.query.all()
#     locObj = {}
#     locArr = []
#     for location in marked_locations:
#         locObj["lat"] = location.lat,
#         locObj["lng"] = location.lng
#         locArr.append(locObj)
#         print(locArr)
#     return render_template('map.html', marked_locations=marked_locations)


@app.route('/new')
# @login_required
# @ensure_correct_user
def new():
    centered = Location.query.get(1)
    marked_locations = Location.query.all()
    # print(current_user.id) 
    return render_template('new.html', centered=centered, marked_locations=marked_locations, id=current_user.id)

@app.route('/<int:id>/addLocation', methods=["GET", "POST"])
@login_required
@ensure_correct_user
def addLoc(id):


    if request.method == 'POST':

        all_locations = Location.query.all()

        # #  Even though they aren't actually shown on a form, you can use the request.form function to get response values shown in the Network tab/ Headers / Form Data section.
        # #  **NOTE:  In this case, the request.form function is returning the value(s) provided by the  Google Maps API response.  As a result, numeric values may have a higher precision (aka more decimal places) than values stored in the database.  This is an important consideration when comparing  request.form["values"] and the value stored in the database, for the same location.  
        name = request.form['name']
        addr = request.form['formatted_address']
        icon = request.form['icon']
        ph_domestic = request.form['ph_domestic']
        ph_intl = request.form['ph_intl']
        website = request.form['website']

        # Convert these decimal values to a precision of 7 
        lat = format(float(request.form['latitude']),'.7f')
        lng = format(float(request.form['longitude']),'.7f')

        match = False

        # check if location is already in locations table
        for loc in all_locations:
            if format(float(loc.lat),'.7f') == lat and format(float(loc.lng),'.7f') == lng:
                match = True
                match_id = loc.id

        # if location is not in database (i.e match = False)
        if match == False: 
            newLocation = Location(name, addr, icon, ph_domestic, ph_intl, website, lat, lng)
            db.session.add(newLocation)
            db.session.commit()
            # after db.session.commit, sqlalchemy provides access to the id of the record just committed
            match_id = newLocation.id

        # add row to association table 
        user_assoc = User.query.get(current_user.id)
        location_assoc = Location.query.get(match_id)
        location_assoc.visitors.append(user_assoc)
        db.session.commit()

        
        # for now I am going to assume a user will not be enter a specific lat/lng more than once

        

        # if match == True: 
        #     print("location id:", match_id)
        #     print("user id", current_user.id)
        #         # newLocation = Location(name, addr, icon, ph_domestic, ph_intl, website, lat, lng)
        #         # db.session.add(newLocation)
        #         # db.session.commit()
        #     user_assoc = User.query.get(current_user.id)
        #     location_assoc = Location.query.get(match_id)
        #     location_assoc.visitors.append(user_assoc)

    return "Yes"
    # return render_template('new.html', centered=centered)



# Environment (Production or Development) ------------------------------
# if os.environ.get('ENV') == 'production':
#     app.config.from_object('config.ProductionConfig')
#     # notice here that we are configuring from a file called "config" and a class inside called "ProductionConfig"
# else:
#     app.config.from_object('config.DevelopmentConfig')

# Run ------------------------------
if __name__ == '__main__':
	app.run(debug=True)

