import tkinter as tk
from tkinter import ttk,filedialog, messagebox
import math
from itertools import product
import time  # Importar el módulo time para medir el tiempo de ejecución


# Función para leer el archivo de la red social
def leer_red_social(archivo):
    """
    Lee un archivo que describe una red social y extrae la información de los agentes y el esfuerzo máximo.

    Args:
        archivo (str): La ruta del archivo que contiene la información de la red social.

    Returns:
        tuple: Una tupla que contiene:
            - agentes (list of tuple): Una lista de tuplas donde cada tupla representa un agente con su esfuerzo.
            - esfuerzo_max (int): El esfuerzo máximo permitido.

    Raises:
        Exception: Si ocurre un error al leer el archivo, se muestra un mensaje de error y se retorna None.
    """
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
    """
    Calcula el nivel de extremismo de una red de agentes.

    Args:
        agentes (list of tuple): Una lista de tuplas donde cada tupla representa un agente con su opinión y esfuerzo.

    Returns:
        float: El nivel de extremismo calculado como la raíz cuadrada de la suma de los cuadrados de las opiniones, 
               dividido entre el número total de agentes. Si la lista está vacía, retorna 0 para evitar división por cero.

    Raises:
        ValueError: Si el formato de los agentes no es válido.
    """
    if not agentes:
        return 0  # Evitar división por cero
    
    try:
        return math.sqrt(sum(opinion ** 2 for opinion, _ in agentes)) / len(agentes)
    except Exception as e:
        raise ValueError(f"Error al calcular extremismo: {e}")


# Función para calcular el esfuerzo de moderar las opiniones
def calcular_esfuerzo(agentes, estrategia):
    """
    Calcula el esfuerzo necesario para moderar las opiniones de una red de agentes, basado en la estrategia dada.

    Args:
        agentes (list of tuple): Una lista de tuplas donde cada tupla representa un agente con su opinión y receptividad.
        estrategia (list of int): Una lista de enteros (0 o 1) que indica qué agentes deben ser moderados (1 para moderar, 0 para no moderar).

    Returns:
        float: El esfuerzo total calculado como la suma del valor absoluto de la opinión multiplicado por 
               (1 - receptividad) para cada agente cuya estrategia sea moderar (estrategia[i] == 1).
    """
    esfuerzo = 0
    for i, (opinion, receptividad) in enumerate(agentes):
        if estrategia[i] == 1:
            esfuerzo += abs(opinion) * (1 - receptividad)
    return esfuerzo

# Algoritmo de fuerza bruta
def fuerza_bruta_modex(agentes, R_max):
    """
    Algoritmo de fuerza bruta para encontrar la mejor estrategia de moderación
    que minimice el extremismo dentro de un límite de esfuerzo máximo (R_max).

    :param agentes: Lista de tuplas donde cada agente tiene una opinión y receptividad.
    :param R_max: Esfuerzo máximo permitido.
    :return: Mejor estrategia de moderación, menor extremismo, nueva red y el esfuerzo utilizado.
    """
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
    """
    Calcula el esfuerzo requerido para moderar un agente basado en su opinión y receptividad.
    
    :param opinion: Opinión del agente.
    :param receptividad: Receptividad del agente.
    :return: Esfuerzo necesario para moderar al agente.
    """
    return math.ceil(abs(opinion) * (1 - receptividad))  # Calcular el esfuerzo usando la receptividad

def programacion_dinamica_modex(agentes, R_max):
    """
    Algoritmo de programación dinámica para encontrar la estrategia óptima que minimice
    el extremismo en la red dentro del esfuerzo máximo permitido.

    :param agentes: Lista de agentes donde cada agente tiene una opinión y receptividad.
    :param R_max: Esfuerzo máximo permitido.
    :return: Estrategia óptima, menor extremismo, nueva red.
    """
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

def voraz_modex(agentes, R_max):
    """
    Algoritmo voraz para moderar a los agentes de manera que se minimice el extremismo
    maximizando el impacto por unidad de esfuerzo.

    :param agentes: Lista de agentes con opiniones y receptividad.
    :param R_max: Esfuerzo máximo permitido.
    :return: Estrategia óptima, menor extremismo, nueva red.
    """
    n = len(agentes)
    
    # Lista para almacenar los esfuerzos y el impacto de cada agente
    impacto_por_esfuerzo = []
    
    for i, (opinion, receptividad) in enumerate(agentes):
        esfuerzo = calcular_esfuerzo_individual(opinion, receptividad)
        impacto = opinion ** 2  # Impacto es el cuadrado de la opinión
        if esfuerzo > 0:
            impacto_por_esfuerzo.append((impacto / esfuerzo, esfuerzo, impacto, i))
    
    # Ordenar los agentes por la mejor relación impacto/esfuerzo de mayor a menor
    impacto_por_esfuerzo.sort(reverse=True, key=lambda x: x[0])
    
    esfuerzo_usado = 0
    suma_cuadrados = 0
    estrategia_optima = [0] * n  # Estrategia de moderación (1 si moderado, 0 si no)
    
    # Moderar los agentes mientras no excedamos el esfuerzo máximo
    for impacto_por_esf, esfuerzo, impacto, i in impacto_por_esfuerzo:
        if esfuerzo_usado + esfuerzo <= R_max:
            estrategia_optima[i] = 1  # Moderamos al agente
            esfuerzo_usado += esfuerzo
            # No agregamos el impacto de este agente ya que fue moderado (opinión 0)
        else:
            suma_cuadrados += impacto  # Agregamos el impacto si no fue moderado
    
    # Crear la nueva red con las opiniones actualizadas
    nueva_red = [(0 if estrategia_optima[i] == 1 else opinion, receptividad) 
                  for i, (opinion, receptividad) in enumerate(agentes)]
    
    # Calcular el menor extremismo alcanzado
    menor_extremismo = math.sqrt(suma_cuadrados) / n
    
    return estrategia_optima, menor_extremismo, nueva_red

# Función para centrar la ventana
def centrar_ventana(ventana, ancho, alto):
    """
    Centra la ventana de la aplicación en la pantalla del usuario.

    :param ventana: La ventana que se va a centrar.
    :param ancho: Ancho de la ventana.
    :param alto: Alto de la ventana.
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

# Función para cargar el archivo y ejecutar el algoritmo seleccionado
def cargar_archivo():
    """
    Cargar un archivo que contiene la red social y ejecutar el algoritmo seleccionado para
    moderar los agentes.
    """
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de red social",
        filetypes=(("Archivos de texto", ".txt"), ("Todos los archivos", "."))
    )
    
    if archivo:
        agentes, esfuerzo_max = leer_red_social(archivo)
        if agentes is not None:
            # Elegir el algoritmo a usar: Fuerza Bruta, Programación Dinámica o Voraz
            if metodo.get() == "Fuerza Bruta":
                # Capturar el tiempo inicial antes de ejecutar el algoritmo
                tiempo_inicio = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final, esfuerzo_total = fuerza_bruta_modex(agentes, esfuerzo_max)
            elif metodo.get() == "Programación Dinámica":
                # Capturar el tiempo inicial antes de ejecutar el algoritmo
                tiempo_inicio = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final = programacion_dinamica_modex(agentes, esfuerzo_max)
                esfuerzo_total = sum(
                    calcular_esfuerzo_individual(agentes[i][0], agentes[i][1]) for i in range(len(agentes)) if mejor_estrategia[i] == 1
                )
            elif metodo.get() == "Voraz":
                # Capturar el tiempo inicial antes de ejecutar el algoritmo
                tiempo_inicio = time.time()
                mejor_estrategia, menor_extremismo, agentes_moderados_final = voraz_modex(agentes, esfuerzo_max)
                esfuerzo_total = sum(
                    calcular_esfuerzo_individual(agentes[i][0], agentes[i][1]) for i in range(len(agentes)) if mejor_estrategia[i] == 1
                )

            # Capturar el tiempo final después de ejecutar el algoritmo
            tiempo_fin = time.time()

            # Calcular el tiempo de ejecución en segundos
            tiempo_ejecucion = tiempo_fin - tiempo_inicio
            
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
            texto_resultados.insert(tk.END, f"Tiempo de Ejecución: {tiempo_ejecucion:.15f} segundos\n")  # Mostrar el tiempo de ejecución
            texto_resultados.insert(tk.END, f"Menor Extremismo Alcanzado: {menor_extremismo:.3f}\n")
            texto_resultados.insert(tk.END, f"Esfuerzo Utilizado: {esfuerzo_total}\n\n")
            texto_resultados.insert(tk.END, "Mejor Estrategia:\n")
            texto_resultados.insert(tk.END, f"{mejor_estrategia}\n")

            texto_resultados.insert(tk.END, f"\nAgentes Moderados:\n")
            for idx, (op, rec) in enumerate(agentes_moderados_final):
                estado = "Moderado" if mejor_estrategia[idx] else "No moderado"
                texto_resultados.insert(tk.END, f"Agente {idx}: Opinión = {op}, Receptividad = {rec} ({estado})\n")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Moderación de Extremismo en Redes Sociales (ModEx)")
ancho_ventana = 800
alto_ventana = 600
centrar_ventana(ventana, ancho_ventana, alto_ventana)
ventana.resizable(True, True)
ventana.configure(bg='#f4f4f9')

# Crear un marco para el botón y el selector de método
frame_boton = tk.Frame(ventana, bg='#f4f4f9', bd=2, relief=tk.GROOVE)
frame_boton.grid(row=0, column=0, pady=20, padx=10)

# Opción para seleccionar método de resolución
metodo = tk.StringVar(value="Programación Dinámica")
etiqueta_metodo = tk.Label(frame_boton, text="Método de Resolución:", bg='#f4f4f9', font=("Arial", 12))
etiqueta_metodo.pack(side=tk.LEFT, padx=10)

opciones_metodo = ttk.Combobox(frame_boton, textvariable=metodo, 
                               values=["Fuerza Bruta", "Programación Dinámica", "Voraz"],
                               state='readonly', font=("Arial", 12), width=20)
opciones_metodo.pack(side=tk.LEFT, padx=10)

# Botón para cargar el archivo
boton_cargar = ttk.Button(frame_boton, text="Cargar Archivo", command=cargar_archivo, width=20)
boton_cargar.pack(side=tk.LEFT, padx=10)

# Crear áreas de texto escalables
ventana.grid_rowconfigure(1, weight=1)
ventana.grid_rowconfigure(2, weight=1)
ventana.grid_columnconfigure(0, weight=1)

# Área de texto para mostrar el contenido del archivo
frame_texto = tk.Frame(ventana, bg='#eaeaea', bd=2, relief=tk.GROOVE)
frame_texto.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

etiqueta_archivo = tk.Label(frame_texto, text="Contenido del Archivo:", bg='#eaeaea', font=("Arial", 12))
etiqueta_archivo.grid(row=0, column=0, sticky='w', padx=5)

texto_principal = tk.Text(frame_texto, wrap=tk.WORD, font=("Courier New", 10), bg='#ffffff')
texto_principal.grid(row=1, column=0, sticky='nsew', padx=5)

# Agregar barra de desplazamiento
scrollbar_texto = tk.Scrollbar(frame_texto, command=texto_principal.yview)
scrollbar_texto.grid(row=1, column=1, sticky='ns')
texto_principal['yscrollcommand'] = scrollbar_texto.set

frame_texto.grid_rowconfigure(1, weight=1)
frame_texto.grid_columnconfigure(0, weight=1)

# Área de texto para mostrar los resultados de la moderación
frame_resultados = tk.Frame(ventana, bg='#eaeaea', bd=2, relief=tk.GROOVE)
frame_resultados.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

etiqueta_resultados = tk.Label(frame_resultados, text="Resultados de la Moderación:", bg='#eaeaea', font=("Arial", 12))
etiqueta_resultados.grid(row=0, column=0, sticky='w', padx=5)

texto_resultados = tk.Text(frame_resultados, wrap=tk.WORD, font=("Courier New", 10), bg='#ffffff')
texto_resultados.grid(row=1, column=0, sticky='nsew', padx=5)

# Agregar barra de desplazamiento
scrollbar_resultados = tk.Scrollbar(frame_resultados, command=texto_resultados.yview)
scrollbar_resultados.grid(row=1, column=1, sticky='ns')
texto_resultados['yscrollcommand'] = scrollbar_resultados.set

frame_resultados.grid_rowconfigure(1, weight=1)
frame_resultados.grid_columnconfigure(0, weight=1)

ventana.mainloop()