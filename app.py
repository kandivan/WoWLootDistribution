from flask import Flask, request, jsonify, abort, render_template, redirect, url_for, redirect
from flask_login import login_required, logout_user, login_user
from flask_bcrypt import Bcrypt
from auth import db, login_manager, LoginForm, RegisterForm, get_user, register_user, change_password, ChangePasswordForm
from events import EventSystem
from telemetry import Telemetry
from dashboard import Dashboard
from cache import redis_cache
from rate_limiter import rate_limit

app = Flask(__name__)
app.secret_key = 'this_is_a_secret_key'  # Secret key for Flask-Login sessions

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize event system
event_system = EventSystem()

# Initialize telemetry
telemetry = Telemetry(db, event_system)

# Initialize dashboard
dashboard = Dashboard(db)

# Routes
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        register_user(form.username.data.lower(), form.email.data.lower(), bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
        return redirect(url_for('login'))
    
    return render_template('registration.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.username.data.lower())
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return "Invalid login credentials."
    
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('templates/dashboard.html')

@app.route('/password_change', methods=['GET', 'POST'])
@login_required
def password_change():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if change_password(bcrypt, current_user, form.old_password.data, form.new_password.data):
            return redirect(url_for('dashboard'))
        else:
            return "Invalid old password.", 400
    return render_template('change_password.html', form=form)

# Error handlers...
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "message": str(e)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Unauthorized", "message": str(e)}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden", "message": str(e)}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": str(e)}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500
    

if __name__ == "__main__":
    app.run(port=5001, debug=True)
