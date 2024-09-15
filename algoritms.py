import tkinter as tk
from tkinter import filedialog, messagebox
import math
from itertools import product

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

# Función para cargar el archivo y ejecutar el algoritmo de fuerza bruta
def cargar_archivo():
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de red social",
        filetypes=(("Archivos de texto", ".txt"), ("Todos los archivos", ".*"))
    )
    if archivo:
        agentes, esfuerzo_max = leer_red_social(archivo)
        if agentes is not None:
            mejor_estrategia, menor_extremismo, agentes_moderados_final, _ = fuerza_bruta_modex(agentes, esfuerzo_max)
            
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
            texto_resultados.insert(tk.END, f"Menor Extremismo Alcanzado: {menor_extremismo:.3f}\n\n")

            texto_resultados.insert(tk.END, "Agentes Moderados:\n")
            for idx, (op, rec) in enumerate(agentes_moderados_final):
                estado = "Moderado" if mejor_estrategia[idx] else "No moderado"
                texto_resultados.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec} ({estado})\n")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Moderación de Extremismo en Redes Sociales (ModEx)")
ventana.geometry("800x600")
ventana.resizable(True, True)

# Crear un marco para el botón y el área de texto
frame_boton = tk.Frame(ventana)
frame_boton.pack(pady=20)

# Botón para cargar el archivo
boton_cargar = tk.Button(frame_boton, text="Cargar Archivo", command=cargar_archivo, width=20, height=2)
boton_cargar.pack()

# Área de texto para mostrar el contenido del archivo y resultados
texto_principal = tk.Text(ventana, wrap=tk.WORD, width=80, height=15)
texto_principal.pack(pady=10)

# Área de texto para mostrar los resultados de la moderación
texto_resultados = tk.Text(ventana, wrap=tk.WORD, width=80, height=15)
texto_resultados.pack(pady=10)

# Iniciar el bucle de la interfaz
ventana.mainloop()