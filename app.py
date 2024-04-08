import psutil
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from db import connectDB
from db import attemptToPushIntoDB
from db import checkName
from db import checkId
root = tk.Tk()

# Llamamos a la función para conectar nuestra base de datos.
conexion = connectDB()


# El simpledialog hace las bases de lo que sería un JDialog en Java.
def openDialog():
    result = simpledialog.askstring("Nombre de Catálogo", "Ingrese el nombre del catálogo que desea guardar para todos los procesos mostrados")
    return result
    
def showErrorMessage(error):
    messagebox.showerror("Error", error)

idcounter = checkId(conexion)  # Declara la variable fuera de la función

#Función que se ejecutará al presionar el botón de exportar
def ExportProcess(process_list):
    global idcounter  # Indica que estás usando la variable global

    procesosExportados = openDialog()
    if procesosExportados == '':
        showErrorMessage('Debes ingresar un nombre de Catálogo.')
    else:
        try:
            procesosExportados = str(procesosExportados)
            resultado = checkName(conexion, procesosExportados)

            if resultado is not None:
                if resultado:
                    showErrorMessage("El nombre de catálogo ya existe en la base de datos.")
                else:
                    idcounter = checkId(conexion) + 1
                    for info in process_list:
                        value1 = int(info["Proceso_Id"])
                        value2 = str(info["Nombre_Proceso"])
                        value3 = str(info["Usuario"])
                        value4 = str(info["Descripcion"])
                        value5 = int(info["CPU_usage"])
                        value6 = int(info["Memoria_usage"])
                        value7 = int(info["Prioridad"])
                        attemptToPushIntoDB(conexion, idcounter, procesosExportados, value1, value2, value3, value4, value5, value6, value7)
        except ValueError:
            showErrorMessage('Invalid argument: Debes ingresar una cadena válida.')


 
# Función que se ejecutará al presionar el botón de importar
def ImportProcess():
    procesosImportados = getInputBoxValue()
    if procesosImportados == '':
        showErrorMessage('Debes ingresar un número.')
    else:
        try:
            procesosImportados = int(procesosImportados)
            main(procesosImportados)
        except ValueError:
            showErrorMessage('Invalid argument: Debes ingresar un número válido.')

# Esta función obtiene lo que el usuario haya puesto en el inputBox
def getInputBoxValue():
    userInput = procesos.get()
    return userInput



# Creamos la ventana principal
root.geometry('802x490')
root.configure(background='#458B74')
root.title('Process Catalog Generator')

# Creamos el label que va arriba del botón
Label(root, text='Ingrese la cantidad de procesos a importar!', bg='#458B74', font=('courier', 20, 'bold')).place(x=311, y=12)

# Creamos el botón de importe
Button(root, text='Importar Procesos!', bg='#00FFFF', font=('courier', 20, 'bold'), command=ImportProcess).place(x=681, y=81)

# Creamos el inputBox de texto
procesos = Entry(root)
procesos.place(x=485, y=98)

# Creamos una tabla (Treeview)
tabla = ttk.Treeview(root, columns=("PID", "Name", "UserName", "Description", "CPU", "Memory", "Priority"))
tabla.place(x=300, y=200)
tabla.pack(fill=tk.X, expand=True)

def configureTable(tabla):
    # Configura el ancho de las columnas
    tabla.column("#1", width=50)
    tabla.column("#2", width=150)
    tabla.column("#3", width=100)
    tabla.column("#4", width=200)
    tabla.column("#5", width=70)
    tabla.column("#6", width=100)
    tabla.column("#7", width=80)

    # Configura la alineación del contenido de las columnas usando la opción "anchor"
    tabla.heading("#1", text="PID", anchor='center')
    tabla.heading("#2", text="Name", anchor='center')
    tabla.heading("#3", text="UserName", anchor='center')
    tabla.heading("#4", text="Description", anchor='center')
    tabla.heading("#5", text="CPU", anchor='center')
    tabla.heading("#6", text="Memory (MB)", anchor='center')
    tabla.heading("#7", text="Priority", anchor='center')

# Llama a esta función antes de utilizar la tabla
configureTable(tabla)

#Creamos el comboBox y el label que va arriba
Label(root, text='Seleccione el filtro que desea aplicar a los procesos encontrados', bg='#458B74', font=('courier', 8, 'bold')).place(x=200, y=165)
comboOneTwoPunch= ttk.Combobox(root, values=['All', 'CPU', 'Memory'], font=('courier', 12, 'normal'), width=10)
comboOneTwoPunch.place(x=750, y=160)
comboOneTwoPunch.current(0)
comboOneTwoPunch.state(["readonly"])

def insertIntoTable(value1, value2, value3, value4, value5, value6, value7):
    tabla.insert("", "end", values=(value1, value2, value3, value4, value5, value6, value7))
    tabla.pack()

def obtainProcessInformation(process):
    try:
        pid = process.pid
        name = process.name()
        username = process.username()
        cmdline = ' '.join(process.cmdline()) if process.cmdline() else ''

        #Obtenemos el uso de CPU y memoria
        cpu_usage = process.cpu_percent()
        memory_info = process.memory_info()
        memory_usage = memory_info.rss  #Uso de la memoria en Bytes

        #Determinamos la prioridad, 0 expulsivo, 1 en otro caso
        priority = 0 if ' (Sí)' in cmdline else 1

        #Limitamos los caracteres de la descripción a 100
        #description = cmdline
        description = cmdline[:100] #SI se requiere limitar los caracteres

        #Retornamos un objeto con todos los atributos que necesitamos
        return {
            "Proceso_Id": pid,
            "Nombre_Proceso": name,
            "Usuario": username,
            "Descripcion": description,
            "CPU_usage": cpu_usage,
            "Memoria_usage": memory_usage / (1024 * 1024),
            "Prioridad": 0 if priority == 0 else 1
        }

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def main(X):
    tabla.delete(*tabla.get_children())  # Eliminamos la información que se encuentre en la tabla
    ignore_count = 0  # Variable de control para contar los procesos a ignorar
    added_count = 0  # Variable de control para contar los procesos agregados a la tabla
    process_list = []  # Lista para almacenar los procesos

    for process in psutil.process_iter(attrs=['pid', 'name', 'username', 'cmdline', 'cpu_percent', 'memory_info']):
        if ignore_count < 2:
            ignore_count += 1
            continue  # Saltar los primeros 2 procesos

        if added_count >= X:
            break  # Ya hemos agregado los X procesos, salir del bucle

        info = obtainProcessInformation(process)
        if info:
            process_list.append(info)  # Agregar información del proceso a la lista
            added_count += 1
            

    if(added_count > X):
       showErrorMessage('Invalid argument: El número ingresado es mayor que la cantidad máxima de procesos disponibles.')
    else:
        unique_process_names = set()  # Utilizamos un conjunto para llevar un registro de nombres únicos
        list_sindup = []

        for proceso in process_list:
            nombre_proceso = proceso["Nombre_Proceso"]
            if nombre_proceso not in unique_process_names:
                        unique_process_names.add(nombre_proceso)
                        list_sindup.append({
            "Proceso_Id": proceso["Proceso_Id"],
            "Nombre_Proceso": proceso["Nombre_Proceso"],
            "Usuario": proceso["Usuario"],
            "Descripcion": proceso["Descripcion"],
            "CPU_usage": proceso["CPU_usage"],
            "Memoria_usage": proceso["Memoria_usage"],
            "Prioridad": proceso["Prioridad"]
                })
                    
        for info in list_sindup:
            insertIntoTable(
                info["Proceso_Id"],
                info["Nombre_Proceso"],
                info["Usuario"],
                info["Descripcion"],
                info["CPU_usage"],
                info["Memoria_usage"],
                info["Prioridad"]
                
            )

    if added_count != 0:
        # Creamos el botón de exportar
        Button(root, text='Exportar procesos', bg='#F542D7', font=('courier', 20, 'bold'), command=lambda: ExportProcess(process_list)).place(x=500, y=500)


if __name__ == "__main__":
    #Inicializamos la aplicación
    root.mainloop()






