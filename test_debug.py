import os
import sys
import mysql.connector
from mysql.connector import Error

print("=" * 60)
print("🔍 DEBUG - PRUEBA DE CONEXIÓN MYSQL")
print("=" * 60)

# Mostrar variables de entorno
print("📋 VARIABLES DE ENTORNO:")
print(f"   MYSQLHOST: {os.environ.get('MYSQLHOST')}")
print(f"   MYSQLDATABASE: {os.environ.get('MYSQLDATABASE')}")
print(f"   MYSQLUSER: {os.environ.get('MYSQLUSER')}")
print(f"   MYSQLPORT: {os.environ.get('MYSQLPORT')}")
print(f"   MYSQLPASSWORD: {'*' * len(os.environ.get('MYSQLPASSWORD', ''))}")

# Verificar variables faltantes
missing_vars = []
for var in ['MYSQLHOST', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD', 'MYSQLPORT']:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ VARIABLES FALTANTES: {missing_vars}")
    sys.exit(1)
else:
    print("✅ TODAS LAS VARIABLES ESTÁN PRESENTES")

# Probar conexión a MySQL
print("\n🔌 PROBANDO CONEXIÓN A MYSQL...")
try:
    # Convertir puerto a entero
    port = int(os.environ.get('MYSQLPORT', 3306))
    
    print(f"   Conectando a: {os.environ.get('MYSQLHOST')}:{port}")
    
    connection = mysql.connector.connect(
        host=os.environ.get('MYSQLHOST'),
        database=os.environ.get('MYSQLDATABASE'),
        user=os.environ.get('MYSQLUSER'),
        password=os.environ.get('MYSQLPASSWORD'),
        port=port,
        connect_timeout=10
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✅ CONEXIÓN EXITOSA!")
        print(f"   MySQL Server version: {db_info}")
        
        # Probar consulta simple
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"   Consulta de prueba: {result}")
        
        cursor.close()
        connection.close()
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        sys.exit(0)
        
except ValueError as e:
    print(f"❌ ERROR: Puerto no válido - {e}")
    sys.exit(1)
except Error as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")
    sys.exit(1)

print("=" * 60)
