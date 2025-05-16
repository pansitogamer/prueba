# builders/build_prompt.py

import os

def build_prompt(nombre_archivo_prompt):
    ruta = os.path.join("prompt", nombre_archivo_prompt)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo de prompt no existe: {ruta}")
    
    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    
    return contenido
