"""
Script para actualizar todos los archivos .http con autenticación JWT correcta
"""
import os
import re

# Directorio donde están los archivos .http
HTTP_TESTS_DIR = r"c:\Users\David\Desktop\Serviwatch\backend\core\http_tests"

# Template del bloque de autenticación correcto
AUTH_TEMPLATE = """###############################################
# AUTENTICACIÓN (EJECUTA ESTO PRIMERO)
###############################################

### Obtener Token JWT
# @name login
# Ejecuta este request primero para obtener el token de autenticación.
# Cambia el username y password según tu usuario.
POST {{base_url}}/api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}

### Guardar el token (se usa automáticamente en los siguientes requests)
@token = {{login.response.body.access}}

"""

def limpiar_auth_vieja(content):
    """Elimina bloques de autenticación antiguos/incorrectos"""
    # Eliminar todo el bloque de autenticación viejo
    # Buscar desde "# AUTENTICACIÓN" hasta el primer "### " que no sea parte de auth
    pattern = r'#{10,}\s*#\s*AUTENTICACI[ÓO]N.*?(?=#{10,}|###\s+\d+\.|\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Eliminar líneas sueltas de Authorization mal puestas
    content = re.sub(r'\nAuthorization: Bearer {{token}}Authorization: Token {{token}}', '', content)
    content = re.sub(r'\n\s*Authorization: Token {{token}}\s*\n', '\n', content)
    
    return content

def agregar_auth_headers(content):
    """Agrega headers Authorization a todos los requests que no lo tengan"""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Si es un request HTTP (GET, POST, PUT, PATCH, DELETE)
        if re.match(r'^(GET|POST|PUT|PATCH|DELETE)\s+', line):
            # Verificar si ya tiene Authorization en las siguientes 5 líneas
            tiene_auth = False
            for j in range(i+1, min(i+6, len(lines))):
                if 'Authorization:' in lines[j]:
                    tiene_auth = True
                    break
                if lines[j].strip() == '' or lines[j].strip().startswith('{'):
                    break
            
            # Si no tiene Authorization y tiene Content-Type, agregar después de Content-Type
            if not tiene_auth:
                # Buscar Content-Type en las próximas líneas
                for j in range(i+1, min(i+5, len(lines))):
                    if 'Content-Type:' in lines[j]:
                        new_lines.append(lines[j])
                        new_lines.append('Authorization: Bearer {{token}}')
                        i = j
                        break
                    elif lines[j].strip() == '':
                        # No hay Content-Type, agregar directamente
                        new_lines.append('Authorization: Bearer {{token}}')
                        break
        
        i += 1
    
    return '\n'.join(new_lines)

def actualizar_archivo(filepath):
    """Actualiza un archivo .http con la autenticación correcta"""
    print(f"Procesando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Limpiar autenticación vieja
    content = limpiar_auth_vieja(content)
    
    # 2. Buscar donde termina el bloque de variables
    lines = content.split('\n')
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('@api_url'):
            insert_index = i + 1
            break
    
    # 3. Insertar nuevo bloque de autenticación
    lines.insert(insert_index, '\n' + AUTH_TEMPLATE)
    content = '\n'.join(lines)
    
    # 4. Agregar headers Authorization donde falten
    content = agregar_auth_headers(content)
    
    # 5. Limpiar líneas vacías excesivas
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Guardar archivo actualizado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Actualizado: {filepath}")

def main():
    """Procesa todos los archivos .http en el directorio"""
    archivos_procesados = 0
    
    if not os.path.exists(HTTP_TESTS_DIR):
        print(f"❌ Directorio no encontrado: {HTTP_TESTS_DIR}")
        return
    
    for filename in os.listdir(HTTP_TESTS_DIR):
        if filename.endswith('.http') and filename != '00_autenticacion.http':
            filepath = os.path.join(HTTP_TESTS_DIR, filename)
            try:
                actualizar_archivo(filepath)
                archivos_procesados += 1
            except Exception as e:
                print(f"❌ Error procesando {filename}: {e}")
    
    print(f"\n✅ Proceso completado. {archivos_procesados} archivos actualizados.")
    print("\n📝 Próximos pasos:")
    print("1. Ejecuta el servidor: python manage.py runserver")
    print("2. Abre cualquier archivo *_test.http")
    print("3. Ejecuta el request 'Obtener Token JWT'")
    print("4. Ejecuta los demás requests (ya tendrán el header Authorization)")

if __name__ == '__main__':
    main()
