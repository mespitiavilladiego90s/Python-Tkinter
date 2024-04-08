import mysql.connector
from tkinter import messagebox

def connectDB():
    config = {
        "user": "root",
        "password": "root",
        "host": "localhost",
        "database": "catalogo"
    }

    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as e:
        print("Error en la conexión a la base de datos:", e)
        return None
    
def attemptToPushIntoDB(conexion, idCatalogo, nombreCatalogo, proceso_id, nombreProceso, usuario, descripcion, cpu_usage, memoria_usage, prioridad):
    if conexion is not None:
        cursor = conexion.cursor()
        try:
            # Crear la consulta SQL parametrizada
            query = """
                INSERT INTO catalogos (ID_Catalogo, Nombre_Catalogo, Proceso_Id, Nombre_Proceso, Usuario, Descripcion, CPU_usage, Memoria_usage, Prioridad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Ejecutar la consulta SQL con los parámetros
            cursor.execute(query, (idCatalogo, nombreCatalogo, proceso_id, nombreProceso, usuario, descripcion, cpu_usage, memoria_usage, prioridad))

            conexion.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Error al insertar en la base de datos:", e)
        finally:
            cursor.close()
    else:
        messagebox.showerror("Error", "No se pudo establecer una conexión a la base de datos.")

def checkName(conexion, nombreCatalogo):
    if conexion is not None:
        cursor = conexion.cursor()
        try:
            # Crear la consulta SQL parametrizada para llamar a la función checkName
            query = "SELECT checkName(%s)"

            # Ejecutar la consulta SQL con el parámetro
            cursor.execute(query, (nombreCatalogo,))
            
            result = cursor.fetchone()
            if result:
                return bool(result[0])  # Convertir el resultado a un valor booleano
            else:
                messagebox.showerror("Error", "No se obtuvo ningún resultado.")
                return None

        except mysql.connector.Error as e:
            messagebox.showerror("Error al llamar a la función checkName:", e)
            return None
        finally:
            cursor.close()
    else:
        messagebox.showerror("Error", "No se pudo establecer una conexión a la base de datos.")


def checkId(conexion):
    if conexion is not None:
        cursor = conexion.cursor()
        try:
            # Crear la consulta SQL parametrizada para llamar a la función checkId
            query = "SELECT checkId()"

            # Ejecutar la consulta SQL
            cursor.execute(query)

            result = cursor.fetchone()
            if result:
                return int(result[0])  # Convertir el resultado a un entero
            else:
                messagebox.showerror("Error", "No se obtuvo ningún resultado.")
                return None

        except mysql.connector.Error as e:
            messagebox.showerror("Error al llamar a la función checkId:", e)
            return None
        finally:
            cursor.close()
    else:
        messagebox.showerror("Error", "No se pudo establecer una conexión a la base de datos.")