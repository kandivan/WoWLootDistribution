from flask_wtf import FlaskForm
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from wtforms  import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from database import Database, User

# Setup Flask-Login
login_manager = LoginManager()
db = Database()
session = db.get_session()

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login hook to load a User instance from ID
    :param user_id: User ID to query
    :return: User instance or None
    """
    return session.query(User).get(user_id)

def get_user(username):
    """Get a User instance from username
    :param username: Username to query
    :return: User instance or None
    """
    return session.query(User).filter_by(username=username).first()

def register_user(username: str, email: str, hashed_password: str):
    """Register a new user in the database
    :param username: Username to register
    :param email: Email to register
    :param hashed_password: Hashed password to register
    :return: None"""
    new_user = User(username=username, email=email, password=hashed_password)
    session.add(new_user)
    session.commit()

def change_password(bcrypt: Bcrypt, user: User, old_password: str, new_password: str):
    """Change a user's password
    :param bcrypt: Bcrypt instance
    :param user: User instance
    :param old_password: Old password
    :param new_password: New password
    :return: None
    """
    if user.check_password(bcrypt, old_password):
        user.set_password(bcrypt, new_password)
        session.commit()
        return True
    else:
        raise ValidationError("Incorrect password.")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField('Change Password')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)],
                            render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[InputRequired()],
                         render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)],
                              render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        existing_user_username = session.query(User).filter_by(username=username.data.lower()).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")
            
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)],
                            render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)],
                              render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


