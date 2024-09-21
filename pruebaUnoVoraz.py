import tkinter as tk
from tkinter import filedialog, messagebox
import math
from itertools import product
import time

# Función para leer el archivo de la red social
def leer_red_social(archivo):
    try:
        with open(archivo, 'r') as f:
            n = int(f.readline().strip())  # Número de agentes
            agentes = []
            for _ in range(n):
                linea = f.readline().strip()
                if not linea:
                    continue  # Salta líneas vacías
                opinion, receptividad = map(float, linea.split(','))
                agentes.append((opinion, receptividad))
            esfuerzo_max = int(f.readline().strip())  # Esfuerzo máximo
        return agentes, esfuerzo_max
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return None, None

# Función para calcular el nivel de extremismo
def calcular_extremismo(agentes):
    if not agentes:
        return 0  # Evitar división por cero
    return math.sqrt(sum(opinion ** 2 for opinion, _ in agentes)) / len(agentes)

# Función para calcular el esfuerzo de moderar las opiniones
def calcular_esfuerzo(agentes, estrategia):
    esfuerzo = 0
    for i, (opinion, receptividad) in enumerate(agentes):
        if estrategia[i] == 1:
            esfuerzo += abs(opinion) * (1 - receptividad)
    return esfuerzo

# Algoritmo de fuerza bruta
def fuerza_bruta_modex(agentes, R_max):
    n = len(agentes)
    mejor_estrategia = None
    mejor_extremismo = float('inf')
    mejor_red = None

    for estrategia in product([0, 1], repeat=n):
        nueva_red = [(0 if estrategia[i] == 1 else opinion, receptividad) 
                      for i, (opinion, receptividad) in enumerate(agentes)]
        
        esfuerzo = calcular_esfuerzo(agentes, estrategia)
        if esfuerzo <= R_max:
            extremismo = calcular_extremismo(nueva_red)
            if extremismo < mejor_extremismo:
                mejor_extremismo = extremismo
                mejor_estrategia = estrategia
                mejor_red = nueva_red  # Guardar la nueva red con la mejor estrategia

    return mejor_estrategia, mejor_extremismo, mejor_red, calcular_esfuerzo(agentes, mejor_estrategia)

# Algoritmo de Programación Dinámica
def calcular_esfuerzo_individual(opinion, receptividad):
    return math.ceil(abs(opinion) * (1 - receptividad))  # Calcular el esfuerzo usando la receptividad

def programacion_dinamica_modex(agentes, R_max):
    n = len(agentes)
    # ME[i][j] = suma mínima de los cuadrados de las opiniones usando los primeros i agentes con esfuerzo j
    ME = [[float('inf')] * (R_max + 1) for _ in range(n + 1)]
    # Inicialización: sin agentes, la suma de cuadrados es 0
    for j in range(R_max + 1):
        ME[0][j] = 0

    # Llenar la matriz ME
    for i in range(1, n + 1):
        opinion_i, receptividad_i = agentes[i - 1]
        esfuerzo_i = calcular_esfuerzo_individual(opinion_i, receptividad_i)
        opinion_i_cuadrado = opinion_i ** 2
        for j in range(R_max + 1):
            # Opción 1: No moderar al agente i
            no_moderar = ME[i - 1][j] + opinion_i_cuadrado
            ME[i][j] = no_moderar
            # Opción 2: Moderar al agente i (si hay suficiente esfuerzo)
            if j >= esfuerzo_i:
                moderar = ME[i - 1][j - esfuerzo_i]  # La opinión moderada es 0, su cuadrado es 0
                ME[i][j] = min(ME[i][j], moderar)

    # Reconstruir la estrategia óptima
    estrategia_optima = [0] * n
    j = R_max
    for i in range(n, 0, -1):
        opinion_i, receptividad_i = agentes[i - 1]
        esfuerzo_i = calcular_esfuerzo_individual(opinion_i, receptividad_i)
        opinion_i_cuadrado = opinion_i ** 2
        # Verificar si el agente fue moderado
        if j >= esfuerzo_i and ME[i][j] == ME[i - 1][j - esfuerzo_i]:
            estrategia_optima[i - 1] = 1  # Moderar al agente
            j -= esfuerzo_i
        else:
            estrategia_optima[i - 1] = 0  # No moderar al agente

    # Crear la nueva red con las opiniones actualizadas
    nueva_red = [(0 if estrategia_optima[i] == 1 else opinion, receptividad) 
                  for i, (opinion, receptividad) in enumerate(agentes)]

    # Calcular el menor extremismo alcanzado
    suma_cuadrados = ME[n][R_max]
    menor_extremismo = math.sqrt(suma_cuadrados) / n

    return estrategia_optima, menor_extremismo, nueva_red





# Función para cargar el archivo y ejecutar el algoritmo seleccionado
def cargar_archivo():
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de red social",
        filetypes=(("Archivos de texto", ".txt"), ("Todos los archivos", "."))
    )
    if archivo:
        agentes, esfuerzo_max = leer_red_social(archivo)
        if agentes is not None:
            # Elegir el algoritmo a usar y medir el tiempo de ejecución
            if metodo.get() == "Fuerza Bruta":
                start_time = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final, esfuerzo_total = fuerza_bruta_modex(agentes, esfuerzo_max)
                end_time = time.time()
            elif metodo.get() == "Programación Dinámica":
                start_time = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final = programacion_dinamica_modex(agentes, esfuerzo_max)
                end_time = time.time()
                esfuerzo_total = sum(calcular_esfuerzo_individual(agentes[i][0], agentes[i][1]) for i in range(len(agentes)) if mejor_estrategia[i] == 1)
            else:  # Algoritmo Voraz
                start_time = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final, esfuerzo_total = greedy_modex(agentes, esfuerzo_max)
                end_time = time.time()
            
            tiempo_ejecucion = end_time - start_time  # Calcular el tiempo de ejecución en segundos
            
            # Mostrar detalles del archivo y resultados en el área de texto principal
            texto_principal.delete(1.0, tk.END)  # Limpiar área de texto principal
            texto_principal.insert(tk.END, f"Archivo Cargado: {archivo}\n")
            texto_principal.insert(tk.END, f"Número de Agentes: {len(agentes)}\n")
            texto_principal.insert(tk.END, f"Esfuerzo Máximo: {esfuerzo_max}\n\n")
            texto_principal.insert(tk.END, "Detalles de los Agentes:\n")
            for idx, (op, rec) in enumerate(agentes):
                texto_principal.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec}\n")
            
            # Mostrar la mejor estrategia y resultados de la moderación en el área de texto de resultados
            texto_resultados.delete(1.0, tk.END)  # Limpiar área de texto de resultados
            texto_resultados.insert(tk.END, "Mejor Estrategia:\n")
            texto_resultados.insert(tk.END, f"{mejor_estrategia}\n")
            texto_resultados.insert(tk.END, f"Menor Extremismo Alcanzado: {menor_extremismo:.3f}\n")
            texto_resultados.insert(tk.END, f"Esfuerzo Utilizado: {esfuerzo_total}\n")
            texto_resultados.insert(tk.END, f"Tiempo de Ejecución: {tiempo_ejecucion:.6f} segundos\n\n")

            texto_resultados.insert(tk.END, "Agentes Moderados:\n")
            for idx, (op, rec) in enumerate(agentes_moderados_final):
                estado = "Moderado" if mejor_estrategia[idx] else "No moderado"
                texto_resultados.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec} ({estado})\n")

                
#agregando el algoritmo voraz
def greedy_modex(agentes, R_max):
    n = len(agentes)
    # Calcular el beneficio por unidad de esfuerzo para cada agente
    agentes_beneficio = []
    for i, (opinion, receptividad) in enumerate(agentes):
        esfuerzo = calcular_esfuerzo_individual(opinion, receptividad)
        if esfuerzo == 0:
            beneficio_por_esfuerzo = float('inf')  # Evitar división por cero
        else:
            # Beneficio: reducción en el extremismo al moderar al agente
            beneficio = opinion ** 2
            beneficio_por_esfuerzo = beneficio / esfuerzo
        agentes_beneficio.append((beneficio_por_esfuerzo, i))

    # Ordenar los agentes por beneficio por unidad de esfuerzo de mayor a menor
    agentes_beneficio.sort(reverse=True)

    estrategia = [0] * n  # Inicialmente, no moderamos a ningún agente
    esfuerzo_total = 0

    for beneficio_por_esfuerzo, i in agentes_beneficio:
        opinion, receptividad = agentes[i]
        esfuerzo = calcular_esfuerzo_individual(opinion, receptividad)
        if esfuerzo_total + esfuerzo <= R_max:
            estrategia[i] = 1  # Moderar al agente
            esfuerzo_total += esfuerzo
        else:
            continue  # No hay suficiente esfuerzo restante

    # Crear la nueva red con las opiniones actualizadas
    nueva_red = [(0 if estrategia[i] == 1 else opinion, receptividad) 
                  for i, (opinion, receptividad) in enumerate(agentes)]

    # Calcular el extremismo alcanzado
    extremismo = calcular_extremismo(nueva_red)

    return estrategia, extremismo, nueva_red, esfuerzo_total


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Moderación de Extremismo en Redes Sociales (ModEx)")
ventana.geometry("800x600")
ventana.resizable(True, True)

# Crear un marco para el botón y el selector de método
frame_boton = tk.Frame(ventana)
frame_boton.pack(pady=20)

# Opción para seleccionar método de resolución
metodo = tk.StringVar(value="Programación Dinámica")  # Valor por defecto
opciones_metodo = tk.OptionMenu(frame_boton, metodo, "Fuerza Bruta", "Programación Dinámica", "Programación Voraz")
opciones_metodo.pack(side=tk.LEFT, padx=10)

# Botón para cargar el archivo
boton_cargar = tk.Button(frame_boton, text="Cargar Archivo", command=cargar_archivo, width=20, height=2)
boton_cargar.pack(side=tk.LEFT, padx=10)

# Área de texto para mostrar el contenido del archivo y resultados
texto_principal = tk.Text(ventana, wrap=tk.WORD, width=80, height=15)
texto_principal.pack(pady=10)

# Área de texto para mostrar los resultados de la moderación
texto_resultados = tk.Text(ventana, wrap=tk.WORD, width=80, height=15)
texto_resultados.pack(pady=10)

# Iniciar el bucle de la interfaz
ventana.mainloop()
