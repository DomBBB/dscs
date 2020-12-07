import requests
from flask import *
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from forms import RegistrationForm, LoginForm, ContactForm, HelpForm
import psycopg2
from passwords2 import psql_user, psql_pw, psql_host, psql_port, psql_database, email_auth, email_data

app = Flask(__name__)
app.config["SECRET_KEY"] = "enter-a-hard-to-guess-string"

bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(username):
    res = query("SELECT * FROM users WHERE username = '{}'".format(username))
    return User(res[0])


class User(UserMixin):
    def __init__(self, res_row):
        self.id = res_row[0]
        self.user_handle = res_row[0]
        self.password_hash = res_row[1]


###############################################################################
#                                                             Accessible Routes                                                                #
###############################################################################
@app.route('/', methods=["GET", "POST"])
def index():
    """ Index Page with a Search Bar that allows partial reloading by Jquery. """
    search = [1, ""]  # default id for search to enable partial Jquery reloading
    form = HelpForm()
    if form.validate_on_submit():
        help_name = form.help_name.data
        help_email = form.help_email.data
        help_comment = form.help_comment.data
        send_help_email(help_name, help_email, help_comment)
        return redirect(url_for('index'))
    return render_template("index.html", search=search, form = form)


@app.route('/query')
@login_required
def query():
    """ Query Page with a Search Bar that allows partial reloading by Jquery and an overview of all saved queries that allow partial reloading as well. """
    search = [1, ""]  # default id for search to enable partial Jquery reloading
    saved = query("SELECT id, words, che FROM search_words WHERE username='{}'".format(current_user.user_handle))
    matched = query("SELECT che FROM search_words WHERE EXISTS (SELECT che FROM liquidations WHERE liquidations.che = search_words.che AND username='{}')".format(current_user.user_handle))
    matches = []
    matches_liq_detail = []
    for match in matched:
        matches.append(match[0])
    if current_user.is_authenticated:
        matched_liq_detail = query("SELECT * FROM liquidations WHERE EXISTS (SELECT che FROM search_words WHERE search_words.che = liquidations.che AND username='{}')".format(current_user.user_handle))
        for match1 in matched_liq_detail:
            matches_liq_detail.append(match1)
    return render_template("query.html", search=search, matches=matches, saved=saved, matches_liq_detail = matches_liq_detail)


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    """ Contact Page with all entered contacts that allows adding a new contact or edit/delete existing contacts (partial reloading). """
    form = ContactForm()
    if form.validate_on_submit():
        if form.new_sms_contact.data == "" and form.new_email_contact.data == "":
            flash("You need to enter at least one sms or email address")
        else:
            query_no_fetch("INSERT INTO contacts VALUES (default, '{}', '{}', '{}', '{}')".format(current_user.user_handle, make_safe(str(form.new_sms_contact.data)),make_safe(form.new_email_contact.data), make_safe(form.new_role_contact.data)))
            contacts = query("SELECT * FROM contacts WHERE username='{}'".format(current_user.user_handle))
            return redirect(url_for("contact"))
    contacts = query("SELECT * FROM contacts WHERE username='{}'".format(current_user.user_handle))
    return render_template("contact.html", form=form, contacts = contacts)


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
        return redirect(url_for("query"))
    form = LoginForm()
    if form.validate_on_submit():
        if is_login_successful(form) == "correct_credentials":
            return redirect(url_for("query"))
        elif is_login_successful(form) == "username_not_found":
            flash("Username not found!")
        elif is_login_successful(form) == "wrong_password":
            flash("Wrong password!")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/impressum")
def impressum():
    return render_template("impressum.html")


###############################################################################
#                                                    Inaccessible Helper Routes                                                          #
###############################################################################
@app.route("/newquerysearch", methods=['POST'])
def newquerysearch():
    """ Helper route for partial reloading of a new company search (section 3.html).
    Uses zefix.ch to match the entry and then reads CHE from the response to query in the liquidation page. """
    id = request.form["id"]
    search = request.form["search"]
    if (len(search) >= 2):
        results = []
        res2 = []
        try:
            r = requests.post("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json", json={"name": search,"languageKey":"de","maxEntries":4})
            x = r.json()["list"]
            for y in x:
                name = y["name"]
                uid = y["uid"]
                che = uid[0:3] + "-" + uid[3:6] + "." + uid[6:9] + "." + uid[9:12]
                if len(res2) < 1:
                    res = query("SELECT * FROM liquidations WHERE che='{}'".format(che))
                    if len(res) > 0:
                        res2.append(res)
                    else:
                        results.append([name, che])
                else:
                    results.append([name, che])
        except:
            pass
        if len(res2) > 0:
            results.append(res2[0])
        if len(results) == 0:
            search = [id, search, [], False, 0]
            return render_template("section3.html", search=search)
        if isinstance(results[-1][0], str):
            r = False
        else:
            r = True
        search = [id, search, results, r, len(results)]
    else:
        search = [id, search, [], False, 0]
    return render_template("section3.html", search=search)


@app.route("/savequery", methods=["POST"])
def savequery():
    """ Helper route for new company save. After saving the values in psql the page is reloaded. """
    id = request.form["id"]
    cheAndEntry = request.form["cheAndEntry"]
    cE = cheAndEntry.split("*,-&")
    che = cE[0]
    search_entry = cE[1]
    query_no_fetch("INSERT INTO search_words VALUES (default, '{}', '{}', '{}')".format(current_user.user_handle, make_safe(search_entry), che))
    return render_template("reload.html")


@app.route("/deletequery", methods=["POST"])
def deletequery():
    """ Helper route to delete a company save with partial reloading (empty part from section2.html). """
    id = request.form["id"]
    query_no_fetch("DELETE FROM search_words  WHERE id='{}'".format(id))
    saved_del = [False]
    return render_template("section2.html", contact=saved_del)


@app.route("/editcontact", methods=["POST"])
def editcontact():
    """ Helper route to edit a contact with partial reloading (section2.html). """
    id = request.form["id"]
    phone = request.form["phone"]
    email = request.form["email"]
    role = request.form["role"]
    query_no_fetch("UPDATE contacts SET phone='{}', email='{}', role='{}' WHERE id='{}'".format(make_safe(str(phone)), make_safe(email), make_safe(role), id))
    contact = [id, current_user.user_handle, phone, email, role]
    return render_template("section2.html", contact=contact)


@app.route("/deletecontact", methods=["POST"])
def deletecontact():
    """ Helper route to delete a contact with partial reloading (empty part from section2.html). """
    id = request.form["id"]
    query_no_fetch("DELETE FROM contacts  WHERE id='{}'".format(id))
    contact = [False]
    return render_template("section2.html", contact=contact)


###############################################################################
#                                                    Helper Functions for accessible Routes                                        #
###############################################################################
def register_user(form_data):
    def user_handle_already_taken(user_handle):
        res = query("SELECT COUNT(*) FROM users WHERE username='{}'".format(make_safe(user_handle)))
        if res[0][0] > 0:
            return True
        else:
            return False
    if user_handle_already_taken(form_data.user_handle.data):
        flash("That user handle is already taken!")
        return False
    hashed_password = bcrypt.generate_password_hash(form_data.password.data).decode('utf-8')
    query_no_fetch("INSERT INTO users VALUES ('{}', '{}')".format(make_safe(form_data.user_handle.data), make_safe(hashed_password)))
    return True


def is_login_successful(form_data):
    username = form_data.user_handle.data
    password = form_data.password.data
    res = query("SELECT * FROM users where username='{}'".format(make_safe(username)))
    if len(res) == 0:
        return "username_not_found"
    if bcrypt.check_password_hash(res[0][1].encode('utf-8'), password.encode('utf-8')):
        user = User(res[0])
        login_user(user)
        return "correct_credentials"
    return "wrong_password"


def send_help_email(help_name, help_email, help_comment):
    who = f"{help_name} <{help_email}>"
    result = requests.post("https://api.eu.mailgun.net/v3/mail.schuldenrufe.ch/messages",
                           auth=("api", email_auth),
                           data={"from": who, "text": help_comment, "to": email_data, "subject": "Contact request Schuldenrufe.ch",})
    return result
###############################################################################
#                                                   Helper Functions for PSQL                                                           #
###############################################################################
def make_safe(s):
    if s == None:
        return "null"
    return s.replace("'", "''")


def get_psql_connection():
    return psycopg2.connect(
        user = psql_user,
        password = psql_pw,
        host = psql_host,
        port = psql_port,
        database = psql_database
    )


def query(cmd):
    return _query(cmd, True)


def query_no_fetch(cmd):
    _query(cmd, False)


def _query(cmd, fetch):
    connection = get_psql_connection()
    cursor = connection.cursor()
    cursor.execute(cmd)
    connection.commit()
    if(fetch):
        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res
    cursor.close()
    connection.close()
    return


###############################################################################
#                                                                         Run                                                                           #
###############################################################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
