from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class RegistrationForm(FlaskForm):
    user_handle = StringField("User Handle", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    legal_disclosure = BooleanField("Legal Disclosure", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class LoginForm(FlaskForm):
    user_handle = StringField("User Handle", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class ContactForm(FlaskForm):
    new_role_contact = StringField("Role")
    new_sms_contact = StringField("SMS Contact")
    new_email_contact = StringField("Email Contact")
    submit_button = SubmitField("Submit")


class HelpForm(FlaskForm):
    help_name = StringField("", validators=[DataRequired()])
    help_email = StringField("", validators=[DataRequired()])
    help_comment = TextAreaField("", validators=[DataRequired()])
    submit_button = SubmitField("Submit")
