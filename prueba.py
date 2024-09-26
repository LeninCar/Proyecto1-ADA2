import time

# Definimos una función simple que realice muchas operaciones (sumar números)
def operacion_prueba():
    total = 0
    for i in range(10**6):  # 1 millón de operaciones (suma simple)
        total += i
    return total

# Medir el tiempo de ejecución de estas operaciones
inicio = time.time()

# Ejecutar varias veces para obtener una mejor muestra
for _ in range(100):  # 100 ejecuciones de 1 millón de operaciones
    operacion_prueba()

fin = time.time()

# Calcular el tiempo total
tiempo_total = fin - inicio

# Calcular cuántas operaciones se realizaron
total_operaciones = 100 * (10**6)  # 100 ejecuciones con 1 millón de operaciones cada una

# Calcular las operaciones por segundo
operaciones_por_segundo = total_operaciones / tiempo_total

# Convertir a operaciones por minuto
operaciones_por_minuto = operaciones_por_segundo * 60

print(f"Tu máquina puede realizar aproximadamente {operaciones_por_minuto:.2e} operaciones por minuto.")
