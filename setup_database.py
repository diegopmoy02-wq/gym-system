import mysql.connector
from mysql.connector import Error
import hashlib
import os
import time

def setup_database():
    print("🚀 INICIANDO CONFIGURACIÓN DE BASE DE DATOS...")
    
    # Mostrar variables de entorno (para debug)
    print("🔍 Variables de entorno:")
    print(f"   MYSQLHOST: {os.environ.get('MYSQLHOST')}")
    print(f"   MYSQLDATABASE: {os.environ.get('MYSQLDATABASE')}")
    print(f"   MYSQLUSER: {os.environ.get('MYSQLUSER')}")
    print(f"   MYSQLPORT: {os.environ.get('MYSQLPORT')}")
    
    # Esperar para que la DB esté lista
    time.sleep(3)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔌 Intento de conexión {attempt + 1}...")
            
            # Convertir puerto a entero
            port = int(os.environ.get('MYSQLPORT', 3306))
            
            connection = mysql.connector.connect(
                host=os.environ.get('MYSQLHOST'),
                database=os.environ.get('MYSQLDATABASE'),
                user=os.environ.get('MYSQLUSER'),
                password=os.environ.get('MYSQLPASSWORD'),
                port=port,
                connect_timeout=30
            )
            
            print("✅ Conexión exitosa a MySQL!")
            
            cursor = connection.cursor()
            
            # Crear tablas
            tables_sql = [
                """CREATE TABLE IF NOT EXISTS usuarios_sistema (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    rol ENUM('admin', 'responsable', 'visor') NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS miembros (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    telefono VARCHAR(15),
                    fecha_inscripcion DATE NOT NULL,
                    fecha_nacimiento DATE,
                    direccion TEXT,
                    estado ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS membresias (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    miembro_id INT NOT NULL,
                    tipo_membresia ENUM('basica', 'premium', 'vip') NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    precio DECIMAL(10,2) NOT NULL,
                    estado ENUM('activa', 'vencida', 'cancelada') DEFAULT 'activa'
                )""",
                """CREATE TABLE IF NOT EXISTS pagos (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    miembro_id INT NOT NULL,
                    membresia_id INT NOT NULL,
                    monto DECIMAL(10,2) NOT NULL,
                    fecha_pago DATE NOT NULL,
                    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
                    referencia VARCHAR(100)
                )""",
                """CREATE TABLE IF NOT EXISTS clases (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    instructor VARCHAR(100) NOT NULL,
                    horario TIME NOT NULL,
                    duracion_minutos INT NOT NULL,
                    capacidad_maxima INT NOT NULL,
                    dias_semana VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE IF NOT EXISTS logs_sistema (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    usuario_id INT NOT NULL,
                    accion VARCHAR(255) NOT NULL,
                    tabla_afectada VARCHAR(50),
                    registro_id INT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            ]
            
            for i, sql in enumerate(tables_sql, 1):
                cursor.execute(sql)
                print(f"✅ Tabla {i} creada/verificada")
            
            # Crear usuarios
            usuarios = [
                ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'),
                ('responsable', hashlib.sha256('resp123'.encode()).hexdigest(), 'responsable'),
                ('visor', hashlib.sha256('visor123'.encode()).hexdigest(), 'visor')
            ]
            
            for username, password_hash, rol in usuarios:
                # Eliminar si existe y recrear
                cursor.execute("DELETE FROM usuarios_sistema WHERE username = %s", (username,))
                cursor.execute(
                    "INSERT INTO usuarios_sistema (username, password_hash, rol) VALUES (%s, %s, %s)",
                    (username, password_hash, rol)
                )
                print(f"✅ Usuario {username} creado")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("🎉 BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
            print("📋 CREDENCIALES:")
            print("   👑 Admin: usuario=admin, contraseña=admin123")
            print("   👥 Responsable: usuario=responsable, contraseña=resp123")  
            print("   👀 Visor: usuario=visor, contraseña=visor123")
            
            return True
            
        except Error as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("🔄 Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print("🚨 Todos los intentos fallaron")
                return False

if __name__ == '__main__':
    setup_database()
