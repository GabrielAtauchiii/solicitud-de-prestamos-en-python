
# SISTEMA DE CONTROL Y SEGUIMIENTO DE PRÉSTAMOS BIBLIOGRÁFICOS (UPN)

import os
from datetime import datetime, timedelta

# --- CONSTANTES GLOBALES ---
MAX_RENOVACIONES = 3             # Límite máximo de renovaciones permitidas por el reglamento
ARCHIVO_DATOS = "prestamos.txt"  # Nombre del archivo para la persistencia de datos

def cargar_prestamos():
    """
    Función para cargar los registros de préstamos desde un archivo de texto plano.
    Lee línea por línea el archivo 'prestamos.txt' y los almacena en una lista de listas.
    Retorna:
        - lista (list): Contiene todos los registros recuperados.
    """
    lista = []
    # Verificamos si el archivo de almacenamiento existe en el directorio
    if os.path.exists(ARCHIVO_DATOS):
        # Abrimos el archivo en modo lectura ('r') con codificación utf-8
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip() # Limpiamos espacios o saltos de línea sobrantes
                if linea:
                    partes = linea.split(",") # Separamos los campos por comas
                    # Estructura esperada: [codigo, libro, usuario, fecha_prestamo, fecha_vencimiento, renovaciones]
                    if len(partes) == 6:
                        partes[5] = int(partes[5]) # Convertimos el número de renovaciones a entero
                        lista.append(partes)
    return lista

def guardar_prestamos(lista):
    """
    Procedimiento para guardar de forma permanente todos los registros en el archivo de texto.
    Recorre la lista principal y escribe cada elemento separado por comas.
    Parámetros:
        - lista (list): Lista actual de préstamos en memoria.
    """
    # Abrimos el archivo en modo escritura ('rescribir'), lo que actualiza la información
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
        for p in lista:
            # Unimos los elementos de la lista convirtiéndolos a texto plano
            linea = ",".join(str(x) for x in p)
            archivo.write(linea + "\n")

def validar_fecha(texto):
    """
    Función para validar el formato correcto de una fecha ingresada por el usuario.
    Parámetros:
        - texto (str): Cadena de texto ingresada con formato de fecha.
    Retorna:
        - bool: True si el formato es válido (DD/MM/AAAA), False en caso contrario.
    """
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def buscar_prestamo(lista, codigo):
    """
    Función de búsqueda secuencial para localizar un préstamo mediante el código del estudiante.
    Parámetros:
        - lista (list): Lista donde se realiza la búsqueda.
        - codigo (str): Código institucional del estudiante a buscar.
    Retorna:
        - int: La posición (índice) si lo encuentra, o -1 si no existe.
    """
    for i in range(len(lista)):
        if lista[i][0] == codigo:
            return i # Retorna el índice exacto dentro de la lista
    return -1 # Retorna -1 si no se encuentra el registro

def registrar_prestamo(lista):
    """
    Procedimiento para registrar un nuevo préstamo bibliográfico.
    Solicita datos por consola, valida duplicados, verifica formatos de fecha 
    e inserta el nuevo registro con 0 renovaciones iniciales.
    """
    print("\n--- REGISTRAR NUEVO PRÉSTAMO ---")
    codigo = input("Ingrese el código institucional del estudiante: ").strip()
    
    # Validamos que el código no exista previamente en los registros activos
    if buscar_prestamo(lista, codigo) != -1:
        print("Error: Ya existe un registro activo con ese código institucional.")
        return

    libro = input("Ingrese el título o código del material bibliográfico: ").strip()
    usuario = input("Ingrese el nombre completo del estudiante: ").strip()
    
    # Ingreso y validación de la fecha de préstamo
    fecha_prestamo = input("Ingrese la fecha de préstamo (DD/MM/AAAA): ").strip()
    if not validar_fecha(fecha_prestamo):
        print("Error: El formato de la fecha de préstamo es inválido.")
        return

    # Ingreso y validación de la fecha de vencimiento límite
    fecha_vencimiento = input("Ingrese la fecha de vencimiento (DD/MM/AAAA): ").strip()
    if not validar_fecha(fecha_vencimiento):
        print("Error: El formato de la fecha de vencimiento es inválido.")
        return

    # Agregamos la nueva fila a la lista principal (el último valor '0' representa las renovaciones iniciales)
    lista.append([codigo, libro, usuario, fecha_prestamo, fecha_vencimiento, 0])
    print("¡Préstamo registrado exitosamente en el sistema!")

def ordenar_por_vencimiento(lista):
    """
    Procedimiento que aplica el algoritmo de ordenamiento por método Burbuja 
    para organizar los registros basándose en sus fechas de vencimiento.
    Parámetros:
        - lista (list): Lista de préstamos a ordenar.
    """
    n = len(lista)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            # Convertimos las cadenas de texto de las fechas a objetos datetime para realizar la comparación cronológica
            fecha_j = datetime.strptime(lista[j][4], "%d/%m/%Y")
            fecha_siguiente = datetime.strptime(lista[j+1][4], "%d/%m/%Y")
            
            # Si la fecha actual es mayor (posterior) a la siguiente, intercambiamos posiciones
            if fecha_j > fecha_siguiente:
                lista[j], lista[j+1] = lista[j+1], lista[j]
    print("\nRegistros ordenados exitosamente por fecha de vencimiento.")

def consultar_estado(lista):
    """
    Procedimiento para verificar el estado actual de un préstamo (Vigente o Vencido) 
    contrastando la fecha límite de vencimiento frente a la fecha actual del sistema.
    """
    print("\n--- CONSULTAR ESTADO DE PRÉSTAMO ---")
    codigo = input("Ingrese el código del estudiante a consultar: ").strip()
    pos = buscar_prestamo(lista, codigo)
    
    if pos == -1:
        print("Resultado: No encontrado en el sistema.")
    else:
        # Extraemos la fecha de vencimiento del registro encontrado
        fecha_venc = datetime.strptime(lista[pos][4], "%d/%m/%Y")
        fecha_actual = datetime.now() # Obtenemos la fecha y hora actual del equipo
        
        print(f"Estudiante: {lista[pos][2]} | Material: {lista[pos][1]} | Vencimiento: {lista[pos][4]}")
        
        # Condicional lógicas para definir el estado
        if fecha_actual > fecha_venc:
            print("Estado del préstamo: [VENCIDO]")
        else:
            print("Estado del préstamo: [VIGENTE]")

def renovar_prestamo(lista):
    """
    Procedimiento para gestionar la renovación de un préstamo bibliográfico.
    Verifica que el préstamo exista y comprueba que no rebase el límite máximo permitido 
    de renovaciones, incrementando posteriormente la fecha de vencimiento en 2 días hábiles.
    """
    print("\n--- RENOVAR PRÉSTAMO ---")
    codigo = input("Ingrese el código del estudiante para la renovación: ").strip()
    pos = buscar_prestamo(lista, codigo)
    
    if pos == -1:
        print("Resultado: No encontrado en el sistema.")
    elif lista[pos][5] >= MAX_RENOVACIONES:
        print(f"Resultado: Límite alcanzado (máximo {MAX_RENOVACIONES} renovaciones permitidas).")
    else:
        # Convertimos la fecha actual de vencimiento y le sumamos un delta de 2 días
        fecha_actual_venc = datetime.strptime(lista[pos][4], "%d/%m/%Y")
        nueva_fecha_venc = fecha_actual_venc + timedelta(days=2)
        
        # Actualizamos los valores en la estructura de datos
        lista[pos][4] = nueva_fecha_venc.strftime("%d/%m/%Y")
        lista[pos][5] += 1
        
        print(f"¡Renovación exitosa! Nueva fecha de vencimiento: {lista[pos][4]}. Total renovaciones: {lista[pos][5]}")

def mostrar_menu():
    """
    Procedimiento auxiliar para desplegar en consola las opciones del menú principal.
    """
    print("\n==================================================")
    print("   SISTEMA DE CONTROL DE PRÉSTAMOS - UPN (CHORRILLOS)")
    print("==================================================")
    print("1. Registrar nuevo préstamo")
    print("2. Buscar préstamo por código institucional")
    print("3. Ordenar préstamos por fecha de vencimiento")
    print("4. Consultar estado del préstamo (Vigente / Vencido)")
    print("5. Renovar préstamo bibliográfico")
    print("0. Guardar y salir del sistema")
    print("==================================================")

def main():
    """
    Función principal (Main) que controla el ciclo de ejecución del programa, 
    gestionando el menú repetitivo y la respuesta según la opción elegida por el usuario.
    """
    # Cargamos los datos previos almacenados en el archivo de texto al iniciar el programa
    prestamos = cargar_prestamos()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            registrar_prestamo(prestamos)
        elif opcion == "2":
            codigo = input("Ingrese el código a buscar: ").strip()
            pos = buscar_prestamo(prestamos, codigo)
            if pos != -1:
                p = prestamos[pos]
                print(f"\n[Encontrado] Código: {p[0]} | Material: {p[1]} | Alumno: {p[2]} | F. Préstamo: {p[3]} | F. Vencimiento: {p[4]} | Renovaciones: {p[5]}")
            else:
                print("No se encontró ningún registro con ese código.")
        elif opcion == "3":
            if len(prestamos) > 0:
                ordenar_por_vencimiento(prestamos)
                for p in prestamos:
                    print(f"-> Código: {p[0]} | Alumno: {p[2]} | Vence: {p[4]}")
            else:
                print("No hay registros disponibles para ordenar.")
        elif opcion == "4":
            consultar_estado(prestamos)
        elif opcion == "5":
            renovar_prestamo(prestamos)
        elif opcion == "0":
            # Guardamos los cambios permanentemente en el archivo antes de cerrar
            guardar_prestamos(prestamos)
            print("Datos guardados correctamente en 'prestamos.txt'. Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Por favor, ingrese un número del menú válido.")

# Punto de entrada principal del script en Python
if __name__ == "__main__":
    main()