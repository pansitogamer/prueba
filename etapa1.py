import os
from dotenv import load_dotenv
from core.orquestador import run_minutas_batch

# Cargar .env
load_dotenv()

# Mensaje inicial
print("🚀 Iniciando proceso de generación de minutas...")

# Ejecutar proceso de minutas
try:
    run_minutas_batch()
except Exception as e:
    print(f"❌ Error ejecutando el proceso de minutas: {e}")

# Mensaje final
print("✅ Proceso finalizado.")





