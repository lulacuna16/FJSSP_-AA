import tkinter as tk
from tkinter import *  # El modulo tkinter permite crear la interfaz grafica
from tkinter import ttk  # Modulo ttk para crear tabla de tiempos con la treeview

import matplotlib.pyplot as plt  # Módulo que permite crear la gráfica


# Clase para crear un globo de información, indicando al usuario qué debe realizar.
# Obtenido en https://stackoverrun.com/es/q/719686
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info'):
        self.waittime = 500  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


numOp = 0  # Variable global para controlar el número de operaciones que ingrese el usuario
numMaq = 0  # Variable global para manipular el número de maquinas que estan disponibles
numJob = 0  # Variable global para controlar el número de trabajos
TOperaciones = []  # los tiempos de las operaciones en cada máquina, es un arreglo bidimensional
# El tamaño de TOperaciones es igual al numero de Operaciones, el tamaño de todos los subarreglos es el mismo dado que
# es el número de máquinas que existen
Jobs = []  # Arreglo global que contiene los trabajos y sus operaciones, es bidimensional.
# El tamaño del arreglo Jobs es el número de trabajos, y el tamaño de cada subarreglo (trabajo) varía de acuerdo al
# número de operaciones que tenga
S = []  # Conjunto que contiene la solución como secuencia ordenada. Es bidimensional, y cada subsecuencia será una triada
# de la forma (i,j,k) donde i es el trabajo, j es la operación, k es la máquina en la que se asignó.
M = []  # Conjunto tridimensional con las secuencias por máquina. Cada secuencia tiene un par de datos (i,j),


# donde i es el trabajo y j es la operación
def crearContenedor():
    global numOp, numMaq, contenedor
    root = tk.Tk()  # La función Tk del módulo tkinter crea el contenedor de la interfaz
    root.title("Job-Shop Scheduling Problem")

    # Agregamos los campos donde el usuario ingresar el numero de operaciones, de máquinas y de trabajos
    # Utilizamos un canvas, para poder agregar una scrollbar para navegar por la interfaz
    container = ttk.Frame(root, width=800, height=600)
    canvas = tk.Canvas(container, width=800, height=600)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    contenedor = ttk.Frame(canvas, width=2000, height=800)

    contenedor.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=contenedor, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.configure(xscrollcommand=scrollbar2.set)
    container.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    scrollbar2.pack(side="bottom", fill="x")

    Op = ttk.Entry(contenedor, justify="center", width=10, background="lightblue1")
    Op.config(foreground="black")  # Color de la letra del texto que se introduce
    Op.config(font="Helvetica")  # Fuente de la letra del texto que se introduce

    Op.place(x=250, y=21)  # Coordenadas de posiconamiento del Entry
    Maq = ttk.Entry(contenedor, justify="center", width=10)
    Maq.config(foreground="black")  # Color de la letra del texto que se introduce
    Maq.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
    Maq.config(background="lightblue1")  # Color de fondo del Entry
    Maq.place(x=250, y=86)  # Coordenadas de posiconamiento del Entry
    Job = ttk.Entry(contenedor, justify="center", width=10)
    Job.config(foreground="black")  # Color de la letra del texto que se introduce
    Job.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
    Job.config(background="lightblue1")  # Color de fondo del Entry
    Job.place(x=250, y=150)  # Coordenadas de posiconamiento del Entry
    # Agregamos los botones que permiten recoger las operaciones y las máquinas ingresadas
    # El argumento command permite manipular la acción en el programa cuando el botón es presionado
    # Ambos botones llaman a las funciones que permiten establecer el número de operaciones, de máquinas y de
    # trabajos que ingreso el usuario
    botonOp = tk.Button(contenedor, text='Núm. de Operaciones', command=lambda: setOperaciones(Op.get(), contenedor))
    botonOp.configure(background="dodgerblue2")  # Color de fondo del botón
    botonOp.configure(foreground="white")  # Color de la letra del texto que se introduce
    botonOp.configure(font="Constantia")  # Fuente de la letra del texto que se introduce
    botonOp.configure(width=20)  # Tamaño del botón
    botonOp.place(x=15, y=15)  # Coordenadas de posiconamiento del botón
    botonMaq = tk.Button(contenedor, text='Núm. de Máquinas', command=lambda: setMaquinas(Maq.get(), contenedor))
    botonMaq.configure(background="dodgerblue2")  # Color de fondo del botón
    botonMaq.configure(foreground="white")  # Fuente de la letra del texto que se introduce
    botonMaq.configure(font="Constantia")  # Fuente de la letra del texto que se introduce
    botonMaq.configure(width=20)  # Tamaño del botón
    botonMaq.place(x=15, y=80)  # Coordenadas de posiconamiento del botón
    botonJob = tk.Button(contenedor, text='Núm. de Trabajos', command=lambda: setTrabajos(Job.get(), contenedor))
    botonJob.configure(background="dodgerblue2")  # Color de fondo del botón
    botonJob.configure(foreground="white")  # Fuente de la letra del texto que se introduce
    botonJob.configure(font="Constantia")  # Fuente de la letra del texto que se introduce
    botonJob.configure(width=20)  # Tamaño del botón
    botonJob.place(x=15, y=145)  # Coordenadas de posiconamiento del botón

    root.mainloop()  # Función que permite ver en pantalla la interfaz

# Funciones para establecer el número de operaciones, máquinas y trabajos
def setOperaciones(Op, contenedor):
    global numOp
    numOp = int(Op)
    # print(numOp,type(numOp),numMaq)
    if numMaq > 0:  # Verifica que los campos de operaciones y máquinas se hayan ingresado para crear la tabla de tiempos
        ingresarOperaciones(contenedor)
    if numJob > 0:  # Si hay trabajos y operaciones crear tabla para declarar las operaciones que pertenecen a cada trabajo
        ingresaTrabajos(contenedor)


def setMaquinas(Maq, contenedor):
    global numMaq
    numMaq = int(Maq)
    # print(numMaq, type(numMaq),numOp)
    if numOp > 0:  # Verifica que los campos de operaciones y máquinas se hayan ingresado para crear la tabla de tiempos
        ingresarOperaciones(contenedor)


def setTrabajos(Job, contenedor):
    global numJob
    numJob = int(Job)
    # print(numJob, type(numJob),numOp)
    if numOp > 0:  # Si hay trabajos y operaciones crear tabla para declarar las operaciones que pertenecen a cada trabajo
        ingresaTrabajos(contenedor)


# Función que crea una tabla donde el usuario coloca el tiempo de cada operación en cada máquina
def ingresarOperaciones(contenedor):
    global numOp, numMaq
    operacionesAux = []  # Entradas de los usuarios
    Operaciones = Frame(contenedor)  # Crea un frame para colocar la tabla
    Operaciones.config(bg="thistle")  # Color de fondo del frame
    Operaciones.place(x=15, y=220)  # Coordenadas de posicionamiento del frame
    # Crea el globo de información
    CreateToolTip(Operaciones, "Agrega el tiempo correspondiente de una operacion en cada máquina. Al terminar presione"
                               "\n'Agregar Operaciones'")
    # Habrá una fila y columna extra para colocar el nombre de cada máquina y de cada operación
    for i in range(numOp + 1):  # Filas: Operación
        ope = []  # guarda los tiempos de una sola operación en cada máquina
        for j in range(numMaq + 1):  # Columnas: Máquina
            if i == 0 and j > 0:
                C = Label(Operaciones, text="m" + str(j))  # Colocar nombre de la máquina
                C.config(bg="plum3")  # Color de fondo del Entry
                C.config(foreground="white")  # Fuente de la letra del texto que se introduce
                C.config(font="Constantia")  # Fuente de la letra del texto que se introduce
                C.grid(row=i, column=j)
            elif i > 0 and j == 0:
                F = Label(Operaciones, text="o" + str(i))  # Colocar nombre de la operación
                F.config(bg="plum3")  # Color de fondo del Entry
                F.config(foreground="white")  # Fuente de la letra del texto que se introduce
                F.config(font="Constantia")  # Fuente de la letra del texto que se introduce
                F.grid(row=i, column=j)
            elif i > 0 and j > 0:
                b = Entry(Operaciones, justify="center", text="", width=4)  # Crea campo de entrada
                b.config(bg="plum3")  # Color de fondo del Entry
                b.config(foreground="white")  # Fuente de la letra del texto que se introduce
                b.grid(row=i, column=j)
                ope.append(b)  # Agrega el campo de tiempo de esa operación al arreglo de la misma
        operacionesAux.append(ope)  # Una vez que se crean todos los campos
        # se agregan al arreglo que contiene a todas las operaciones
    botonOp = Button(Operaciones, text='Agregar Operaciones', command=lambda: setTiempoOpe(operacionesAux))
    botonOp.config(bg="blue violet")  # Color de fondo del botón
    botonOp.config(foreground="white")  # Fuente de la letra del texto que se introduce
    botonOp.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
    botonOp.grid(row=i + 1, column=0)
    # Una vez que se pulsa el botón, se recuperan los datos ingresados para guardarlos en la variable global TOperaciones


# Función que crea una tabla de checkbox, donde el usuario elige cuales operaciones pertenecen a cada trabajo
def ingresaTrabajos(contenedor):
    global numOp, numJob
    trabajosAux = []  # Entradas de los usuarios
    Trabajos = Frame(contenedor)  # Crea un frame para colocar la tabla
    Trabajos.config(bg="thistle")  # Color de fondo del frame
    Trabajos.place(x=500, y=220)  # Coordenadas de posicionamiento del frame
    # Crea el globo de información
    CreateToolTip(Trabajos, "Selecciona las operaciones de cada trabajo. Al terminar presione \n'Agregar trabajos'")
    # Habrá una fila y columna extra para colocar el nombre de cada trabajo y de cada operación
    for i in range(numJob + 1):  # Filas: Trabajo
        ope = []  # guarda las operaciones de un solo trabajo
        for j in range(numOp + 1):  # Columnas: operaciones
            if i == 0 and j > 0:
                C = Label(Trabajos, text="o" + str(j))  # Colocar nombre de la operación en las columnas
                C.config(bg="plum3")  # Color de fondo del Entry
                C.config(foreground="white")  # Fuente de la letra del texto que se introduce
                C.config(font="Constantia")  # Fuente de la letra del texto que se introduce
                C.grid(row=i, column=j)
            elif i > 0 and j == 0:
                F = Label(Trabajos, text="j" + str(i))  # Colocar nombre del trabajo en las filas
                F.config(bg="plum3")  # Color de fondo del Entry
                F.config(foreground="white")  # Fuente de la letra del texto que se introduce
                F.config(font="Constantia")  # Fuente de la letra del texto que se introduce
                F.grid(row=i, column=j)
            elif i > 0 and j > 0:
                b = tk.BooleanVar()  # Variable booleana, true si es seleccionada de lo contrario toma valor false
                check = Checkbutton(Trabajos, text="", width=4,
                                    var=b)  # Crea checkbox de entrada, se le asocia el booleano b
                check.config(bg="thistle")
                check.grid(row=i, column=j)
                ope.append(b)  # Agrega el booleano de esa operacion al arreglo de la misma
        trabajosAux.append(ope)  # Una vez que se crean todos los campos
        # se agregan al arreglo que contiene a todas las operaciones

    botonJob = Button(Trabajos, text='Agregar Trabajos', command=lambda: setOpeJob(trabajosAux))
    botonJob.config(bg="blue violet")  # Color de fondo del botón
    botonJob.config(foreground="white")  # Fuente de la letra del texto que se introduce
    botonJob.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
    botonJob.grid(row=i + 1, column=j - j)
    # Una vez que se pulsa el botón, se recuperan los datos ingresados para guardarlos en la variable global Jobs


# Función que crea el conjunto de los tiempos de las operaciones en cada máquina a partir de la tabla
def setTiempoOpe(operacionesAux):
    global TOperaciones, contenedor  # Modificar la variable global
    for i in range(len(operacionesAux)):  # Recorrer los arreglos que contiene a los campos de entrada
        Operacion = []  # Arreglo aux para guardar los valores y anexarlos a la variable global
        for j in range(len(operacionesAux[i])):  # Recorre cada subarreglo
            Operacion.append(int(operacionesAux[i][j].get()))  # Recuperamos el valor ingresado
        TOperaciones.append(Operacion)  # Se anexan los tiempos de la operación al arreglo global
    if len(Jobs) > 0:  # Cuando ya estan definidos el conjunto de trabajos y operaciones, crea el boton para
        # iniciar simulación
        IniciarJSSP = Button(contenedor, text='Iniciar Simulación', command=JSSP)
        IniciarJSSP.config(bg="orange2")  # Color de fondo del botón
        IniciarJSSP.config(foreground="black")  # Color de la letra del texto que se introduce
        IniciarJSSP.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
        IniciarJSSP.place(x=530, y=50)
        IniciarJSSP.config(width=15, height=3)


# Función que crea el conjunto de los trabajos con sus operaciones desde la tabla

def setOpeJob(trabajosAux):
    global Jobs, contenedor  # Modificar la variable global
    for i in range(len(trabajosAux)):  # Recorrer los arreglos que contiene a los campos de entrada
        Job = []  # Arreglo aux para guardar los valores y anexarlos a la variable global
        for j in range(len(trabajosAux[i])):  # Recorre cada subarreglo
            if trabajosAux[i][j].get():  # Si la operación fue seleccionada
                Job.append(j + 1)  # Agregar el índice de esa operacion al trabajo, es j+1 para tener bien claro qué
                # operación es
                # Ojo, se agrega el índice que es el que indica el número de la operación
        Jobs.append(Job)  # Se anexan los tiempos de la operación al arreglo global
    if len(TOperaciones) > 0:  # Cuando ya estan definidos el conjunto de trabajos y operaciones, crea el boton para
        # iniciar simulación
        IniciarJSSP = Button(contenedor, text='Iniciar Simulación', command=JSSP)
        IniciarJSSP.config(bg="orange2")  # Color de fondo del botón
        IniciarJSSP.config(foreground="black")  # Color de la letra del texto que se introduce
        IniciarJSSP.config(font="Helvetica")  # Fuente de la letra del texto que se introduce
        IniciarJSSP.place(x=530, y=50)
        IniciarJSSP.config(width=15, height=3)


# Crea una nueva ventana para mostrar tiempos. Esta es la declaración
def crearTabla():
    global contenedorTiempos, tree
    contenedorTiempos = Tk()  # Crea una ventana para mostrar los tiempos
    contenedorTiempos.title("Tiempos resultantes para el JSSP")

    tree = ttk.Treeview(contenedorTiempos)  # Crea un frame como vista de árbol en la ventana de tiempos
    tree["columns"] = ("one", "two", "three", "four")
    tree.column("#0", width=110, minwidth=100, stretch=tk.NO)
    tree.column("one", width=100, minwidth=100, stretch=tk.NO)
    tree.column("two", width=100, minwidth=100, stretch=tk.NO)
    tree.column("three", width=100, minwidth=100, stretch=tk.NO)
    tree.column("four", width=100, minwidth=100, stretch=tk.NO)
    tree.heading("#0", text="Máquina", anchor=tk.W)
    tree.heading("one", text="Operación (i,j)", anchor=tk.W)
    tree.heading("two", text="Tiempo Inicio", anchor=tk.W)
    tree.heading("three", text="Tiempo Final", anchor=tk.W)
    tree.heading("four", text="Tiempo Total", anchor=tk.W)


# Código recuperado de https://riptutorial.com/es/tkinter/example/31880/treeview--ejemplo-basico

# Definimos la forma de la gráfica
def crearGrafica():
    global fig, ax
    fig, ax = fig, ax = plt.subplots()
    ax.set_ylabel('Máquinas')  # Eje y
    plt.grid()  # Mostrar cuadrícula
    ax.set_xlabel('Tiempo')  # Eje x


def JSSP():  # Se realiza la candelarización de los trabajos y operaciones
    global Jobs, TOperaciones  # Entradas
    global M, S  # Salidas
    crearTabla()  # Crea la tabla de tiempos
    crearGrafica()  # Inicializar la gráfica
    M = [[] for i in range(len(TOperaciones[1]) + 1)]  # Crea tantos subarreglos como máquinas

    print("Iniciando Simulación")
    finalJob = [0 for i in range(len(Jobs))]  # Arreglo con los tiempos de finalización de cada operación por trabajo
    finalMaq = [0 for i in range(len(TOperaciones[1]) + 1)]  # Arreglo con los tiempos de finalización de cada máquina
    lJobs = [0 for i in range(len(Jobs))]  # Array para ir guardando la cantidad de operaciones que se van completando
    # por  cada trabajo
    Tamjobs = [len(Jobs[i]) for i in
               range(len(Jobs))]  # Contiene los tamaños de cada trabajo, sirve para comparar y detener
    # el algoritmo
    Continua = True  # Variable que mientras se mantenga verdadera, el algoritmo seguirá analizando operaciones y trabajos
    while Continua:
        for i in range(1, len(Jobs)):  # Recorriendo cada trabajo
            s = []  # Crea la triada que será añadida a la secuencia solución S
            k = []  # Crea una secuencia para añadir a la máquina respectiva
            if lJobs[i] < len(Jobs[i]):  # Mientras la cantidad de operaciones completadas en el trabajo i
                # sea menor a la cantidad de operaciones que tiene ese trabajo , se debe continuar
                maqCandidatas = [0 for i in range(len(TOperaciones[1]) + 1)]  # Crea Arreglo de máquina candidatas a
                maqCandidatas[0] = 500  # Tiempo de la máquina 0
                # realizar la operación, de ahí tomará la mejor opción
                numOperacion = Jobs[i][lJobs[i]]

                # AQUI VA LA PARTE QUE HACE LAS ASIGNACIONES DE LAS OPERACIONES
                for j in range(
                        len(TOperaciones[numOperacion])):  # Recorre los tiempos en cada máquina en busca del mejor
                    t = TOperaciones[numOperacion][j]  # Escoge una máquina con para la operación
                    m = TOperaciones[numOperacion].index(t) + 1  # Busca el índice de esa máquina
                    if finalMaq[m] >= finalJob[
                        i]:  # Se verifica que el tiempo de finalización en la máquina m sea mayor o
                        # igual al tiempo de finalización de la operación anterior del trabajo i, para evitar traslape
                        maqCandidatas[m] = finalMaq[
                                               m] + t  # Añade el tiempo de finalización de la operación a la máquina ele-
                        # gida al arreglo de máquinas candidatas para la operación
                    else:
                        maqCandidatas[
                            m] = 1000  # Si la máquina m no está disponible,su tiempo tomar un valor arbitrario
                        # muy grande para evitar ser elegida

                tmin = min(maqCandidatas)  # Escoge la máquina con menor tiempo de finalicación de entre las candidatas
                # Crea el conjunto s, que está en forma de triada (i,j,k) que es subconjunto de la secuencia S
                s.append(i)
                s.append(numOperacion)
                mE = maqCandidatas.index(tmin)  # Busca el índice de la máquina elegida de entre las candidatas
                s.append(mE)
                S.append(s)

                # Agrega a la máquina m la operación correspondiente del trabajo i
                k.append(i)
                k.append(numOperacion)
                M[mE].append(k)

                # PARA LA INTERFAZ OCUPAN
                # numOperacion
                # i = numero de trabajo
                # m =numero de máquina elegida
                # finalMaq[mE] = tiempo de inicio de la operación
                # tmin =tiempo final de la operación
                tablaTiempos(numOperacion, i, mE, finalMaq[mE], tmin)  # Funcion que añade a la tabla de tiempos
                grafica(numOperacion, i, mE, finalMaq[mE], tmin)  # Funcion que crea la gráfica
                print("Para operación {} del Job{} escogí la M{} con tiempo de inicio={} y final={}".format(
                    numOperacion, i, mE, finalMaq[mE], tmin
                ))
                # Agregar el tiempo de la operacion a los arreglos de tiempos de finalización de máquina y de trabajos
                finalMaq[mE] = tmin
                finalJob[i] = tmin
                lJobs[i] += 1  # Se marca completada la operación y aumenta en 1 el arreglo que lleva el control

        if lJobs == Tamjobs:  # Si ya se completaron todas las operaciones de cada trabajo
            Continua = False  # La variable 'Continua' se torna falsa, y por lo tanto se acaba el programa

    verTabla()  # Muestra la tabla terminado el algoritmo
    verGrafica(max(finalJob))  # Muestra la grafica
    print("Conjunto S (trabajo, operación, máquina):", S)


def grafica(numOperacion, numTrabajo, maquinaElegida, tiempoIni, tiempoFin):
    global fig, ax
    colores = ["red", "lightsteelblue", "palegreen", "salmon", "sandybrown", "orchid", "khaki", "darkorange",
               "deepskyblue", "hotpink", "goldenrod", "olivedrab", "aquamarine", "turquoise", "thistle",
               "wheat", "magenta", "darkkhaki", "limegreen", "steelblue", "silver"]
    ax.barh("M" + str(maquinaElegida), tiempoFin - tiempoIni, left=tiempoIni,
            color=colores[numTrabajo])  # Añade la barra y la apila en la máquina correspondiente
    O = "O" + str(numTrabajo) + str(numOperacion)  # Crea el texto Oij
    ax.text(tiempoIni, "M" + str(maquinaElegida), O)  # Añade a la barra el texto Oij
    # Muesta el eje x de 1 en 1 para ver resultados exactos


# para crear la vista de árbol y ver tabla de tiempos ocupamos código desde
# https://riptutorial.com/es/tkinter/example/31880/treeview--ejemplo-basico
def tablaTiempos(numOperacion, numTrabajo, maquinaElegida, tiempoIni, tiempoFin):
    global tree, contenedorTiempos
    # Añade los respectivos datos de una operación a la tabla
    tree.insert("", "end", text="m" + str(maquinaElegida), values=("O" + str(numTrabajo) + str(numOperacion),
                                                                   str(tiempoIni), str(tiempoFin),
                                                                   str(tiempoFin - tiempoIni)))


def verTabla():
    global contenedorTiempos, tree  # Ocupamos la ventana que contiene a la tabla de tiempos
    tree.pack()
    Label(contenedorTiempos, text="O(i,j), donde:\ni= número de trabajo\nj=número de operación").pack()


def verGrafica(makespan):
    global fig, ax
    plt.xticks([i for i in range(makespan + 1)])
    plt.show()


def main():
    crearContenedor()
    return 0


main()
