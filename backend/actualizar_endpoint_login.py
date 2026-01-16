"""
Script para actualizar endpoint de /api/token/ a /login/ en archivos .http
"""
import os
import re

HTTP_TESTS_DIR = r"c:\Users\David\Desktop\Serviwatch\backend\core\http_tests"

def actualizar_archivo(filepath):
    """Actualiza las URLs de autenticación en un archivo .http"""
    print(f"Procesando: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiar /api/token/ a /login/
    content = content.replace('POST {{base_url}}/api/token/', 'POST {{base_url}}/login/')
    content = content.replace('POST {{base_url}}/api/token/refresh/', 'POST {{base_url}}/login/refresh/')
    content = content.replace('POST {{base_url}}/api/token/verify/', 'POST {{base_url}}/login/verify/')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Actualizado: {os.path.basename(filepath)}")

def main():
    archivos_procesados = 0
    
    for filename in os.listdir(HTTP_TESTS_DIR):
        if filename.endswith('.http'):
            filepath = os.path.join(HTTP_TESTS_DIR, filename)
            try:
                actualizar_archivo(filepath)
                archivos_procesados += 1
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print(f"\n✅ Completado. {archivos_procesados} archivos actualizados.")
    print("\n📝 Endpoints actualizados:")
    print("   POST /login/")
    print("   POST /login/refresh/")
    print("   POST /login/verify/")

if __name__ == '__main__':
    main()
