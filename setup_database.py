import mysql.connector
from mysql.connector import Error
import hashlib
import os

def setup_database():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQLHOST'),
            database=os.environ.get('MYSQLDATABASE'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            port=os.environ.get('MYSQLPORT')
        )
        
        cursor = connection.cursor()
        
        # Crear tablas
        tables = [
            """
            CREATE TABLE IF NOT EXISTS usuarios_sistema (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol ENUM('admin', 'responsable', 'visor') NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS miembros (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefono VARCHAR(15),
                fecha_inscripcion DATE NOT NULL,
                fecha_nacimiento DATE,
                direccion TEXT,
                estado ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS membresias (
                id INT PRIMARY KEY AUTO_INCREMENT,
                miembro_id INT NOT NULL,
                tipo_membresia ENUM('basica', 'premium', 'vip') NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                estado ENUM('activa', 'vencida', 'cancelada') DEFAULT 'activa'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pagos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                miembro_id INT NOT NULL,
                membresia_id INT NOT NULL,
                monto DECIMAL(10,2) NOT NULL,
                fecha_pago DATE NOT NULL,
                metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
                referencia VARCHAR(100)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS clases (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                instructor VARCHAR(100) NOT NULL,
                horario TIME NOT NULL,
                duracion_minutos INT NOT NULL,
                capacidad_maxima INT NOT NULL,
                dias_semana VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logs_sistema (
                id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                accion VARCHAR(255) NOT NULL,
                tabla_afectada VARCHAR(50),
                registro_id INT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table in tables:
            cursor.execute(table)
            print(f"Tabla creada exitosamente")
        
        # Crear usuarios por defecto
        usuarios = [
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'),
            ('responsable', hashlib.sha256('resp123'.encode()).hexdigest(), 'responsable'),
            ('visor', hashlib.sha256('visor123'.encode()).hexdigest(), 'visor')
        ]
        
        for username, password_hash, rol in usuarios:
            cursor.execute(
                "INSERT IGNORE INTO usuarios_sistema (username, password_hash, rol) VALUES (%s, %s, %s)",
                (username, password_hash, rol)
            )
            print(f"Usuario {username} creado")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Base de datos configurada exitosamente!")
        print("\n📋 Credenciales para probar:")
        print("Administrador: usuario=admin, contraseña=admin123")
        print("Responsable: usuario=responsable, contraseña=resp123")
        print("Visor: usuario=visor, contraseña=visor123")
        
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    setup_database()
