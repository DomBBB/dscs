import pandas as pd
import datetime
import time

from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required

from forms import RegistrationForm, LoginForm, PostForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "enter-a-hard-to-guess-string"

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

###############################################################################
# Database configuration
###############################################################################
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    user_handle = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(140), nullable=False)
    posts = db.relationship("Post", backref="user", lazy=True)

    def __repr__(self):
        return f"User(id: '{self.id}', first_name: '{self.first_name}', last_name: '{self.last_name}', user_handle: '{self.user_handle}', email: '{self.email}', password: '{self.password}', description: '{self.description}')"


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(140), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post(id: '{self.id}', post: '{self.post}', length: '{self.length}', time_created: '{self.time_created}, user_id:'{self.user_id}')"


###############################################################################
# Routes
###############################################################################
@app.route("/")
@login_required
def index():
    posts, users = all_posts()
    print(posts)
    print(users)
    return render_template("index.html", posts=posts, users=users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        registration_worked = register_user(form)
        if registration_worked:
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        if is_login_successful(form) == "correct_credentials":
            return redirect(url_for("index"))
        elif is_login_successful(form) == "email_not_found":
            flash("Email not found! You were redirected.")
            return redirect(url_for("register"))
        elif is_login_successful(form) == "wrong_password":
            flash("Wrong password!")
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    form = PostForm()

    if form.validate_on_submit():
        if add_post(form) == "successful":
            return redirect(url_for("index"))
        else:
            flash("Maximum length exceded")
            return render_template("newpost.html", form=form)

    return render_template("newpost.html", form=form)


@app.route("/profile/<username>")
@login_required
def profile(username):
    user_handle, first_name, last_name, description = search_user(username)

    if user_handle is not None:
        return render_template("profilepage.html", user_handle=user_handle, first_name=first_name, last_name=last_name, description=description)

    return redirect(url_for("index"))


###############################################################################
# Helper functions
###############################################################################
def register_user(form_data):

    def email_already_taken(email):
        if User.query.filter_by(email=email).count() > 0:
            return True
        else:
            return False

    def user_handle_already_taken(user_handle):
        if User.query.filter_by(user_handle=user_handle).count() > 0:
            return True
        else:
            return False

    if email_already_taken(form_data.email.data):
        flash("That email is already taken!")
        return False

    if user_handle_already_taken(form_data.user_handle.data):
        flash("That user handle is already taken!")
        return False

    hashed_password = bcrypt.generate_password_hash(form_data.password.data)

    user = User(first_name=form_data.first_name.data,
                last_name=form_data.last_name.data,
                user_handle=form_data.user_handle.data,
                email=form_data.email.data,
                password=hashed_password,
                description=form_data.description.data)

    db.session.add(user)
    db.session.commit()
    return True


def is_login_successful(form_data):

    email = form_data.email.data
    password = form_data.password.data

    user = User.query.filter_by(email=email).first()

    if user is None:
        return "email_not_found"

    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return "correct_credentials"

    return "wrong_password"


def add_post(form_data):
    x = len(form_data.newpost.data)

    if x <= 140:
        post = Post(post=form_data.newpost.data, length=x, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return "successful"

    return False


def search_user(user_handle):
    user = User.query.filter_by(user_handle=user_handle).first()

    if user is None:
        return None, None, None, None

    return user.user_handle, user.first_name, user.last_name, user.description


def all_posts():
    posts = pd.read_sql(Post.query.order_by(desc(Post.time_created)).statement, db.session.bind)
    users = pd.read_sql(User.query.statement, db.session.bind)
    return posts, users


if __name__ == "__main__":
    app.run(debug=True)
