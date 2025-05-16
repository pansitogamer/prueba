# start.py

print("¿Qué etapa quieres ejecutar?")
print("1. Etapa 1")
print("2. Etapa 2")

# Obtener la opción del usuario
opcion = input("Elige la etapa (1 o 2): ")

if opcion == "1":
    print("Ejecutando etapa 1...")
    import etapa1  # Suponiendo que 'etapa1.py' está en el mismo directorio
elif opcion == "2":
    print("Ejecutando etapa 2...")
    import etapa2  # Suponiendo que 'etapa2.py' está en el mismo directorio
else:
    print("Opción no válida.")

