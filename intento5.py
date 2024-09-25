import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
                    continue
                opinion, receptividad = map(float, linea.split(','))
                agentes.append((opinion, receptividad))
            esfuerzo_max = int(f.readline().strip())  # Esfuerzo máximo
        return agentes, esfuerzo_max
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return None, None

def calcular_extremismo(agentes):
    if not agentes:
        return 0  
    return math.sqrt(sum(opinion ** 2 for opinion, _ in agentes)) / len(agentes)

def calcular_esfuerzo(agentes, estrategia):
    esfuerzo = 0
    for i, (opinion, receptividad) in enumerate(agentes):
        if estrategia[i] == 1:
            esfuerzo += abs(opinion) * (1 - receptividad)
    return esfuerzo

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
                mejor_red = nueva_red

    return mejor_estrategia, mejor_extremismo, mejor_red, calcular_esfuerzo(agentes, mejor_estrategia)

def calcular_esfuerzo_individual(opinion, receptividad):
    return math.ceil(abs(opinion) * (1 - receptividad))

def programacion_dinamica_modex(agentes, R_max):
    n = len(agentes)
    ME = [[float('inf')] * (R_max + 1) for _ in range(n + 1)]
    for j in range(R_max + 1):
        ME[0][j] = 0

    for i in range(1, n + 1):
        opinion_i, receptividad_i = agentes[i - 1]
        esfuerzo_i = calcular_esfuerzo_individual(opinion_i, receptividad_i)
        opinion_i_cuadrado = opinion_i ** 2
        for j in range(R_max + 1):
            no_moderar = ME[i - 1][j] + opinion_i_cuadrado
            ME[i][j] = no_moderar
            if j >= esfuerzo_i:
                moderar = ME[i - 1][j - esfuerzo_i]
                ME[i][j] = min(ME[i][j], moderar)

    estrategia_optima = [0] * n
    j = R_max
    for i in range(n, 0, -1):
        opinion_i, receptividad_i = agentes[i - 1]
        esfuerzo_i = calcular_esfuerzo_individual(opinion_i, receptividad_i)
        if j >= esfuerzo_i and ME[i][j] == ME[i - 1][j - esfuerzo_i]:
            estrategia_optima[i - 1] = 1
            j -= esfuerzo_i
        else:
            estrategia_optima[i - 1] = 0

    nueva_red = [(0 if estrategia_optima[i] == 1 else opinion, receptividad) 
                  for i, (opinion, receptividad) in enumerate(agentes)]

    suma_cuadrados = ME[n][R_max]
    menor_extremismo = math.sqrt(suma_cuadrados) / n

    return estrategia_optima, menor_extremismo, nueva_red

def voraz_modex(agentes, R_max):
    n = len(agentes)
    impacto_por_esfuerzo = []
    for i, (opinion, receptividad) in enumerate(agentes):
        esfuerzo = calcular_esfuerzo_individual(opinion, receptividad)
        impacto = opinion ** 2
        if esfuerzo > 0:
            impacto_por_esfuerzo.append((impacto / esfuerzo, esfuerzo, impacto, i))
    
    impacto_por_esfuerzo.sort(reverse=True, key=lambda x: x[0])
    
    esfuerzo_usado = 0
    suma_cuadrados = 0
    estrategia_optima = [0] * n
    
    for impacto_por_esf, esfuerzo, impacto, i in impacto_por_esfuerzo:
        if esfuerzo_usado + esfuerzo <= R_max:
            estrategia_optima[i] = 1
            esfuerzo_usado += esfuerzo
        else:
            suma_cuadrados += impacto
    
    nueva_red = [(0 if estrategia_optima[i] == 1 else opinion, receptividad) 
                  for i, (opinion, receptividad) in enumerate(agentes)]
    
    menor_extremismo = math.sqrt(suma_cuadrados) / n
    
    return estrategia_optima, menor_extremismo, nueva_red

def centrar_ventana(ventana, ancho, alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

def cargar_archivo():
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de red social",
        filetypes=(("Archivos de texto", ".txt"), ("Todos los archivos", ".")))
    
    if archivo:
        agentes, esfuerzo_max = leer_red_social(archivo)
        if agentes is not None:
            # Guardamos los datos cargados en la ventana para usarlos después al ejecutar
            ventana.agentes = agentes
            ventana.esfuerzo_max = esfuerzo_max

            texto_principal.delete(1.0, tk.END)
            texto_principal.insert(tk.END, f"Archivo Cargado: {archivo}\n")
            texto_principal.insert(tk.END, f"Número de Agentes: {len(agentes)}\n")
            texto_principal.insert(tk.END, f"Esfuerzo Máximo: {esfuerzo_max}\n\n")
            texto_principal.insert(tk.END, "Detalles de los Agentes:\n")
            for idx, (op, rec) in enumerate(agentes):
                texto_principal.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec}\n")
            
            # Habilitar el botón de ejecutar después de cargar el archivo
            boton_ejecutar.config(state=tk.NORMAL)

def ejecutar_algoritmo():
    if hasattr(ventana, 'agentes') and hasattr(ventana, 'esfuerzo_max'):
        agentes = ventana.agentes
        esfuerzo_max = ventana.esfuerzo_max

        # Definir el nombre del algoritmo para mostrarlo en la salida
        algoritmo_ejecutado = ""

        if metodo.get() == "Fuerza Bruta":
            algoritmo_ejecutado = "Fuerza Bruta"
            tiempo_inicio = time.time()
            mejor_estrategia, menor_extremismo, agentes_moderados_final, esfuerzo_total = fuerza_bruta_modex(agentes, esfuerzo_max)
        elif metodo.get() == "Programación Dinámica":
            algoritmo_ejecutado = "Programación Dinámica"
            tiempo_inicio = time.time()
            mejor_estrategia, menor_extremismo, agentes_moderados_final = programacion_dinamica_modex(agentes, esfuerzo_max)
            esfuerzo_total = sum(
                calcular_esfuerzo_individual(agentes[i][0], agentes[i][1]) for i in range(len(agentes)) if mejor_estrategia[i] == 1
            )
        elif metodo.get() == "Voraz":
            algoritmo_ejecutado = "Algoritmo Voraz"
            tiempo_inicio = time.time()
            mejor_estrategia, menor_extremismo, agentes_moderados_final = voraz_modex(agentes, esfuerzo_max)
            esfuerzo_total = sum(
                calcular_esfuerzo_individual(agentes[i][0], agentes[i][1]) for i in range(len(agentes)) if mejor_estrategia[i] == 1
            )

        tiempo_fin = time.time()
        tiempo_ejecucion = tiempo_fin - tiempo_inicio

        # Limpiar la ventana de resultados antes de mostrar los nuevos
        texto_resultados.delete(1.0, tk.END)

        # Insertar el nombre del algoritmo ejecutado en la salida
        texto_resultados.insert(tk.END, f"Algoritmo Ejecutado: {algoritmo_ejecutado}\n")
        texto_resultados.insert(tk.END, f"Tiempo de Ejecución: {tiempo_ejecucion:.15f} segundos\n")
        texto_resultados.insert(tk.END, f"Menor Extremismo Alcanzado: {menor_extremismo:.3f}\n")
        texto_resultados.insert(tk.END, f"Esfuerzo Utilizado: {esfuerzo_total}\n\n")
        
        texto_resultados.insert(tk.END, "Mejor Estrategia:\n")
        texto_resultados.insert(tk.END, f"{mejor_estrategia}\n")

        texto_resultados.insert(tk.END, f"\nAgentes Moderados:\n")
        for idx, (op, rec) in enumerate(agentes_moderados_final):
            estado = "Moderado" if mejor_estrategia[idx] else "No moderado"
            texto_resultados.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec} ({estado})\n")

        # Actualizar variables para la exportación
        ventana.agentes_moderados_final = agentes_moderados_final
        ventana.mejor_estrategia = mejor_estrategia

        # Habilitar el botón de exportación
        boton_exportar.config(state=tk.NORMAL)


def exportar_txt(agentes_moderados_final, mejor_estrategia):
    archivo_guardado = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
    
    if archivo_guardado:
        try:
            with open(archivo_guardado, 'w') as f:
                f.write("Agentes Moderados y Estrategia Óptima\n")
                f.write("--------------------------------------\n")
                for idx, (op, rec) in enumerate(agentes_moderados_final):
                    estado = "Moderado" if mejor_estrategia[idx] == 1 else "No moderado"
                    f.write(f"Agente {idx}: Opinión = {op}, Receptividad = {rec}, Estado = {estado}\n")
            messagebox.showinfo("Exportación exitosa", f"El archivo ha sido guardado en: {archivo_guardado}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar el archivo: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Moderación de Extremismo en Redes Sociales (ModEx)")
ancho_ventana = 1100
alto_ventana = 600
centrar_ventana(ventana, ancho_ventana, alto_ventana)
ventana.resizable(True, True)
ventana.configure(bg='#ffffff')

# Crear un estilo común para los botones usando ttk
estilo_botones = ttk.Style()
estilo_botones.configure("TButton", font=("Arial", 12), padding=10)

frame_boton = tk.Frame(ventana, bg='#f4f4f9', bd=2, relief=tk.GROOVE)
frame_boton.grid(row=0, column=0, pady=20, padx=10)

metodo = tk.StringVar(value="Programación Dinámica")
etiqueta_metodo = tk.Label(frame_boton, text="Método de Resolución:", bg='#f4f4f9', font=("Arial", 12))
etiqueta_metodo.pack(side=tk.LEFT, padx=10)

opciones_metodo = ttk.Combobox(frame_boton, textvariable=metodo, 
                               values=["Fuerza Bruta", "Programación Dinámica", "Voraz"],
                               state='readonly', font=("Arial", 12), width=20)
opciones_metodo.pack(side=tk.LEFT, padx=10)

boton_cargar = ttk.Button(frame_boton, text="Cargar Archivo", command=cargar_archivo, width=20, style="TButton")
boton_cargar.pack(side=tk.LEFT, padx=10)

boton_ejecutar = ttk.Button(frame_boton, text="Ejecutar", command=ejecutar_algoritmo, width=20, style="TButton", state=tk.DISABLED)
boton_ejecutar.pack(side=tk.LEFT, padx=10)

boton_exportar = ttk.Button(frame_boton, text="Exportar a TXT", command=lambda: exportar_txt(ventana.agentes_moderados_final, ventana.mejor_estrategia), width=20, style="TButton", state=tk.DISABLED)
boton_exportar.pack(side=tk.LEFT, padx=10)

ventana.grid_rowconfigure(1, weight=1)
ventana.grid_rowconfigure(2, weight=1)
ventana.grid_columnconfigure(0, weight=1)

frame_texto = tk.Frame(ventana, bg='#5d83d3', bd=2, relief=tk.GROOVE)
frame_texto.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

etiqueta_archivo = tk.Label(frame_texto, text="Contenido del Archivo:", bg='#5d83d3', font=("Arial", 12))
etiqueta_archivo.grid(row=0, column=0, sticky='w', padx=5)

texto_principal = tk.Text(frame_texto, wrap=tk.WORD, font=("Courier New", 10), bg='#ffffff')
texto_principal.grid(row=1, column=0, sticky='nsew', padx=5)

scrollbar_texto = tk.Scrollbar(frame_texto, command=texto_principal.yview)
scrollbar_texto.grid(row=1, column=1, sticky='ns')
texto_principal['yscrollcommand'] = scrollbar_texto.set

frame_texto.grid_rowconfigure(1, weight=1)
frame_texto.grid_columnconfigure(0, weight=1)

frame_resultados = tk.Frame(ventana, bg='#5d83d3', bd=2, relief=tk.GROOVE)
frame_resultados.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

etiqueta_resultados = tk.Label(frame_resultados, text="Resultados de la Moderación:", bg='#5d83d3', font=("Arial", 12))
etiqueta_resultados.grid(row=0, column=0, sticky='w', padx=5)

texto_resultados = tk.Text(frame_resultados, wrap=tk.WORD, font=("Courier New", 10), bg='#ffffff')
texto_resultados.grid(row=1, column=0, sticky='nsew', padx=5)

scrollbar_resultados = tk.Scrollbar(frame_resultados, command=texto_resultados.yview)
scrollbar_resultados.grid(row=1, column=1, sticky='ns')
texto_resultados['yscrollcommand'] = scrollbar_resultados.set

frame_resultados.grid_rowconfigure(1, weight=1)
frame_resultados.grid_columnconfigure(0, weight=1)

ventana.mainloop()
