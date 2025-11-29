from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-gym-2024')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash, rol):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
    
    def check_password(self, password):
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        return hashed_input == self.password_hash

    @staticmethod
    def get_by_username(username):
        try:
            print(f"🔍 Buscando usuario: {username}")
            
            # Convertir puerto a entero
            port = int(os.environ.get('MYSQLPORT', 3306))
            
            connection = mysql.connector.connect(
                host=os.environ.get('MYSQLHOST'),
                database=os.environ.get('MYSQLDATABASE'),
                user=os.environ.get('MYSQLUSER'),
                password=os.environ.get('MYSQLPASSWORD'),
                port=port
            )
            
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM usuarios_sistema WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                print(f"✅ Usuario encontrado: {username}")
                return User(
                    id=result['id'],
                    username=result['username'],
                    password_hash=result['password_hash'],
                    rol=result['rol']
                )
            else:
                print(f"❌ Usuario no encontrado: {username}")
                return None
                
        except Error as e:
            print(f"🚨 Error buscando usuario: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        try:
            print(f"🔍 Buscando usuario por ID: {user_id}")
            
            # Convertir puerto a entero
            port = int(os.environ.get('MYSQLPORT', 3306))
            
            connection = mysql.connector.connect(
                host=os.environ.get('MYSQLHOST'),
                database=os.environ.get('MYSQLDATABASE'),
                user=os.environ.get('MYSQLUSER'),
                password=os.environ.get('MYSQLPASSWORD'),
                port=port
            )
            
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM usuarios_sistema WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    password_hash=result['password_hash'],
                    rol=result['rol']
                )
            return None
        except Error as e:
            print(f"Error: {e}")
            return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

def get_db_connection():
    try:
        # Convertir puerto a entero
        port = int(os.environ.get('MYSQLPORT', 3306))
        
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQLHOST'),
            database=os.environ.get('MYSQLDATABASE'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            port=port
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def log_action(accion):
    usuario = current_user.username if current_user.is_authenticated else 'Sistema'
    logging.info(f"Usuario: {usuario} - Acción: {accion}")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔐 Intento de login: {username}")
        
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            log_action(f"Login exitoso")
            flash(f'Bienvenido {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            print(f"❌ Login fallido para: {username}")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM miembros")
        total_miembros = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM membresias WHERE estado = 'activa'")
        membresias_activas = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM clases")
        total_clases = cursor.fetchone()['total']
        
        cursor.close()
        connection.close()
        
        stats = {
            'total_miembros': total_miembros,
            'membresias_activas': membresias_activas,
            'total_clases': total_clases,
            'pagos_mes': 0
        }
    else:
        stats = {'total_miembros': 0, 'membresias_activas': 0, 'total_clases': 0, 'pagos_mes': 0}
    
    return render_template('dashboard.html', stats=stats)

@app.route('/miembros')
@login_required
def miembros():
    if current_user.rol not in ['admin', 'responsable']:
        flash('No tienes permisos para esta sección', 'error')
        return redirect(url_for('dashboard'))
    
    connection = get_db_connection()
    miembros = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM miembros ORDER BY created_at DESC")
        miembros = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('miembros.html', miembros=miembros)

@app.route('/miembros/agregar', methods=['GET', 'POST'])
@login_required
def agregar_miembro():
    if current_user.rol not in ['admin', 'responsable']:
        flash('No tienes permisos', 'error')
        return redirect(url_for('miembros'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_inscripcion = request.form['fecha_inscripcion']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO miembros (nombre, email, telefono, fecha_inscripcion) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, email, telefono, fecha_inscripcion))
            connection.commit()
            cursor.close()
            connection.close()
            
            flash('Miembro agregado exitosamente', 'success')
            log_action(f"Agregó miembro: {nombre}")
            return redirect(url_for('miembros'))
        else:
            flash('Error de conexión', 'error')
    
    return render_template('agregar_miembro.html')

@app.route('/consultas')
@login_required
def consultas():
    resultado = None
    tipo_consulta = request.args.get('tipo')
    
    connection = get_db_connection()
    if connection and tipo_consulta:
        cursor = connection.cursor(dictionary=True)
        
        if tipo_consulta == 'miembros_activos':
            cursor.execute("SELECT * FROM miembros WHERE estado = 'activo'")
            resultado = cursor.fetchall()
        elif tipo_consulta == 'clases_hoy':
            cursor.execute("SELECT * FROM clases")
            resultado = cursor.fetchall()
        
        cursor.close()
        connection.close()
    
    return render_template('consultas.html', resultado=resultado, tipo_consulta=tipo_consulta)

@app.route('/logout')
@login_required
def logout():
    log_action("Cerró sesión")
    logout_user()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
