import pymysql
import hashlib
import os
import time
import sys

def setup_database():
    print("🚀 INICIANDO CONFIGURACIÓN DE BASE DE DATOS...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔌 Intento de conexión {attempt + 1}/{max_retries}...")
            
            connection = pymysql.connect(
                host=os.environ.get('MYSQLHOST'),
                database=os.environ.get('MYSQLDATABASE'),
                user=os.environ.get('MYSQLUSER'),
                password=os.environ.get('MYSQLPASSWORD'),
                port=int(os.environ.get('MYSQLPORT', 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            print("✅ Conexión exitosa a MySQL!")
            
            with connection.cursor() as cursor:
                # Crear tablas
                tables = [
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
                
                for i, table in enumerate(tables, 1):
                    cursor.execute(table)
                    print(f"✅ Tabla {i} creada/verificada")
                
                # Crear usuarios
                usuarios = [
                    ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'),
                    ('responsable', hashlib.sha256('resp123'.encode()).hexdigest(), 'responsable'),
                    ('visor', hashlib.sha256('visor123'.encode()).hexdigest(), 'visor')
                ]
                
                for username, password_hash, rol in usuarios:
                    cursor.execute("DELETE FROM usuarios_sistema WHERE username = %s", (username,))
                    cursor.execute(
                        "INSERT INTO usuarios_sistema (username, password_hash, rol) VALUES (%s, %s, %s)",
                        (username, password_hash, rol)
                    )
                    print(f"✅ Usuario {username} creado")
            
            connection.commit()
            connection.close()
            
            print("🎉 BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
            print("")
            print("🔑 CREDENCIALES PARA INICIAR SESIÓN:")
            print("   👑 Administrador:    usuario=admin       contraseña=admin123")
            print("   👥 Responsable:      usuario=responsable contraseña=resp123")  
            print("   👀 Visor:            usuario=visor       contraseña=visor123")
            print("")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                wait_time = 5
                print(f"🔄 Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                print("🚨 TODOS LOS INTENTOS FALLARON")
                return False
    
    return False

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 EJECUTANDO SETUP DE BASE DE DATOS")
    print("=" * 60)
    
    success = setup_database()
    
    print("=" * 60)
    if success:
        print("✅ SETUP COMPLETADO EXITOSAMENTE")
        sys.exit(0)
    else:
        print("❌ SETUP FALLÓ")
        sys.exit(1)
