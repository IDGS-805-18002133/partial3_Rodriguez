from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User

import hashlib
import os
import binascii

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def hash_password(password):
    salt = os.urandom(16)
    iterations = 100000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return f"pbkdf2:sha256:{iterations}${binascii.hexlify(salt).decode()}$"\
           f"{binascii.hexlify(key).decode()}"

def check_password(stored_hash, password):
    parts = stored_hash.split("$")
    if len(parts) != 3:
        return False
    
    algorithm_info = parts[0].split(":")
    iterations = int(algorithm_info[2])
    salt = binascii.unhexlify(parts[1])
    stored_key = binascii.unhexlify(parts[2])

    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    
    return new_key == stored_key

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password(user.password, password):
            login_user(user)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales incorrectas", "error")

    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

@app.route("/users")
@login_required
def users():
    users = User.query.all()
    print(users)
    return render_template("users.html", users=users)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/nuevo_usuario", methods=['GET', 'POST'])
def nuevo_usuario():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Usuario creado exitosamente", "success")
        return redirect(url_for('login'))
    return render_template("nuevo_usuario.html")

@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
