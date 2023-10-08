from flask import Flask, request, jsonify, abort, render_template, redirect, url_for, redirect
from flask_login import login_required, logout_user, login_user, current_user
from flask_bcrypt import Bcrypt
from auth import db, login_manager, LoginForm, RegisterForm, get_user, register_user, change_password, ChangePasswordForm
from events import EventSystem
from telemetry import Telemetry
from dashboard import Dashboard
from cache import redis_cache
from rate_limiter import rate_limit
from database import Database, Player, Item
from flask import render_template_string
import plotly
import plotly.graph_objs as go
import json
import tempfile
import subprocess

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

db_instance = Database()
db_instance.create_tables()
def apply_item_to_player(player: Player, item: Item):
    pass
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

@app.route("/simulations", methods=["GET", "POST"])
def simulations():
    session = db_instance.get_session()
    players = session.query(Player).all()
    items = session.query(Item).all()
    session.close()
    output_data = None
    selected_players_data = []
    return render_template('simulations.html', players=players, items=items, selected_players=selected_players_data, output_data=output_data)

@app.route("/plotly_dashboard", methods=["POST"])
def plotly_dashboard():
    selected_player_ids = request.form.getlist('player_checkbox')
    selected_item = None
    selected_item_id = request.form.get('item_select')
    if selected_item_id:
        selected_item = db_instance.get_session().query(Item).filter_by(id=selected_item_id).first()
    selected_players_data = []
    for player_id in selected_player_ids:
        selected_player_data = db_instance.get_player_by_id(player_id)
        if selected_player_data:
            selected_players_data.append(selected_player_data)
    result_holder = []
    for player in selected_players_data:
        holder = {"name": "",
                  "before_dps": 0,
                  "after_dps": 0,
                  "change_in_dps": 0}
        item_index = selected_item.type
        player.raid_sim_settings.get("raid").get("parties")[0].get("players")[0].get("equipment").get("items")[item_index]["id"] = selected_item.id
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode='w') as temp_input_file:
            json.dump(player.__dict__.get("raid_sim_settings"), temp_input_file)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_output_file:
            cmd = ['./wowsimcli.exe', 'sim', '--infile', temp_input_file.name, '--outfile', temp_output_file.name]
            subprocess.run(cmd)

            with open(temp_output_file.name, 'r') as out_file:
                output_data = json.load(out_file)
            player.raid_sim_results = output_data
        session = db_instance.get_session()
        db_player = session.query(Player).filter_by(id=player_id).first()
        if db_player:
            db_player = player
        session.commit()
        session.close()

    # Sort players by raidMetrics.dps.avg in descending order
    sorted_players_data = sorted(
        selected_players_data, 
        key=lambda p: p.raid_sim_results.get("raidMetrics", {}).get("dps", {}).get("avg", 0), 
        reverse=True
    )

    y_values = [round(player.raid_sim_results.get("raidMetrics").get("dps").get("avg"), 0) for player in sorted_players_data]
    
    data = [
        go.Bar(
            x=[player.in_game_name for player in sorted_players_data],
            y=y_values,
            text=y_values,   # Add values as hover text
            hoverinfo='text'
        )
    ]
    layout = go.Layout(
    title="Player Simulation Results",
    xaxis=dict(title='Player In-game Name'),
    yaxis=dict(title='Average DPS'),
)
    fig = go.Figure(data=data, layout=layout)
    graph_json = plotly.offline.plot(fig, output_type='div')

    return render_template_string("""
        <html>
            <head>
                <title>Plotly Dashboard</title>
            </head>
            <body>
                {{ graph_json|safe }}
            </body>
        </html>
    """, graph_json=graph_json)

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
