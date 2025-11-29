import os
import sys

print("🔍 DEBUG - VARIABLES DE ENTORNO EN RENDER:")
print(f"MYSQLHOST: {os.environ.get('MYSQLHOST')}")
print(f"MYSQLDATABASE: {os.environ.get('MYSQLDATABASE')}")
print(f"MYSQLUSER: {os.environ.get('MYSQLUSER')}")
print(f"MYSQLPORT: {os.environ.get('MYSQLPORT')}")
print(f"MYSQLPASSWORD: {'*' * len(os.environ.get('MYSQLPASSWORD', ''))}")

# Verificar si las variables existen
missing_vars = []
for var in ['MYSQLHOST', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD', 'MYSQLPORT']:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ VARIABLES FALTANTES: {missing_vars}")
    sys.exit(1)
else:
    print("✅ TODAS LAS VARIABLES ESTÁN PRESENTES")
    sys.exit(0)
