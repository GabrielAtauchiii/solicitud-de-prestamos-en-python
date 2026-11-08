# SISTEMA DE CONTROL Y SEGUIMIENTO DE PRÉSTAMOS BIBLIOGRÁFICOS (UPN - CHORRILLOS)

import os
from datetime import datetime, timedelta

# --- CONSTANTES GLOBALES ---
MAX_RENOVACIONES = 3             # Límite máximo de renovaciones permitidas
ARCHIVO_DATOS = "prestamos.txt"  # Archivo para la persistencia de datos

def cargar_prestamos():
    """Carga los registros de préstamos desde el archivo de texto plano."""
    lista = []
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    # Estructura: [codigo, libro, usuario, fecha_entrega, fecha_vencimiento, renovaciones, encargado]
                    if len(partes) >= 6:
                        partes[5] = int(partes[5]) # Convertir renovaciones a entero
                        lista.append(partes)
    return lista

def guardar_prestamos(lista):
    """Guarda de forma permanente todos los registros en el archivo de texto."""
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
        for p in lista:
            linea = ",".join(str(x) for x in p)
            archivo.write(linea + "\n")

def validar_fecha(texto):
    """Valida el formato correcto de una fecha ingresada (DD/MM/AAAA)."""
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def buscar_prestamo(lista, codigo):
    """Busca un préstamo mediante el código del estudiante. Retorna el índice o -1."""
    for i in range(len(lista)):
        if lista[i][0] == codigo:
            return i
    return -1

def registrar_prestamo(lista):
    """Registra el préstamo a cargo del personal y calcula 1 semana automática de vencimiento."""
    print("\n--- REGISTRAR NUEVO PRÉSTAMO (PERSONAL ENCARGADO) ---")
    encargado = input("Ingrese el nombre del personal encargado: ").strip()
    codigo = input("Ingrese el código institucional del estudiante: ").strip()
    
    if buscar_prestamo(lista, codigo) != -1:
        print("Error: El estudiante ya cuenta con un préstamo activo en el sistema.")
        return

    libro = input("Ingrese el título o código del material bibliográfico: ").strip()
    usuario = input("Ingrese el nombre completo del estudiante: ").strip()
    
    # Fecha en que se entregó el material
    fecha_entrega = input("Ingrese la fecha de entrega (DD/MM/AAAA): ").strip()
    if not validar_fecha(fecha_entrega):
        print("Error: El formato de la fecha de entrega es inválido.")
        return

    # El sistema calcula la fecha de vencimiento automáticamente sumando 1 semana (7 días)
    fecha_entrega_dt = datetime.strptime(fecha_entrega, "%d/%m/%Y")
    fecha_vencimiento_dt = fecha_entrega_dt + timedelta(days=7)
    fecha_vencimiento = fecha_vencimiento_dt.strftime("%d/%m/%Y")

    # Guardamos en la lista
    lista.append([codigo, libro, usuario, fecha_entrega, fecha_vencimiento, 0, encargado])
    print(f"¡Préstamo registrado exitosamente por {encargado}!")
    print(f"Fecha de entrega: {fecha_entrega}")
    print(f"Vencimiento calculado automáticamente (1 semana): {fecha_vencimiento}")

def registrar_devolucion(lista):
    """Registra la devolución cerrando y eliminando el préstamo activo."""
    print("\n--- REGISTRAR DEVOLUCIÓN DE MATERIAL ---")
    codigo = input("Ingrese el código del estudiante que devuelve el libro: ").strip()
    pos = buscar_prestamo(lista, codigo)
    
    if pos == -1:
        print("Resultado: No se encontró ningún préstamo activo con ese código.")
    else:
        prestamo = lista.pop(pos)
        print("¡Devolución registrada con éxito!")
        print(f"Estudiante: {prestamo[2]} | Material devuelto: {prestamo[1]}")
        print("El registro ha sido cerrado y retirado del sistema.")

def ordenar_por_vencimiento(lista):
    """Ordena los registros mediante el método Burbuja por fecha de vencimiento."""
    n = len(lista)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            fecha_j = datetime.strptime(lista[j][4], "%d/%m/%Y")
            fecha_siguiente = datetime.strptime(lista[j+1][4], "%d/%m/%Y")
            
            if fecha_j > fecha_siguiente:
                lista[j], lista[j+1] = lista[j+1], lista[j]
    print("\nRegistros ordenados exitosamente por fecha de vencimiento.")

def consultar_estado(lista):
    """Consulta el estado del préstamo mostrando la fecha de entrega y si está vigente o vencido."""
    print("\n--- CONSULTAR ESTADO DE PRÉSTAMO ---")
    codigo = input("Ingrese el código del estudiante a consultar: ").strip()
    pos = buscar_prestamo(lista, codigo)
    
    if pos == -1:
        print("Resultado: No encontrado en el sistema.")
    else:
        fecha_entrega = lista[pos][3]
        fecha_venc = datetime.strptime(lista[pos][4], "%d/%m/%Y")
        fecha_actual = datetime.now()
        
        print(f"\nEstudiante: {lista[pos][2]} | Material: {lista[pos][1]}")
        print(f"Fecha en que se entregó: {fecha_entrega}")
        print(f"Fecha de vencimiento: {lista[pos][4]}")
        if len(lista[pos]) > 6:
            print(f"Encargado: {lista[pos][6]}")
            
        if fecha_actual.date() > fecha_venc.date():
            print("Estado del préstamo: ⚠️ [VENCIDO]")
        else:
            print("Estado del préstamo: ✅ [VIGENTE]")

def consultar_por_material(lista):
    """Permite al encargado buscar por material y ver qué estudiantes lo tienen y su vigencia."""
    print("\n--- CONSULTAR PRÉSTAMOS POR MATERIAL ---")
    if not lista:
        print("No hay registros disponibles en el sistema.")
        return
        
    material_buscado = input("Ingrese el título o código del material a buscar: ").strip().lower()
    
    encontrados = []
    for p in lista:
        if material_buscado in p[1].lower():
            encontrados.append(p)
            
    if not encontrados:
        print(f"No se encontraron préstamos activos para el material '{material_buscado}'.")
    else:
        print(f"\nReporte de usuarios para el material: '{material_buscado}'")
        print("=" * 70)
        for p in encontrados:
            fecha_venc = datetime.strptime(p[4], "%d/%m/%Y")
            if datetime.now() > fecha_venc:
                estado = "⚠️ [VENCIDO]"
            else:
                estado = "✅ [VIGENTE]"
                
            print(f"• Alumno: {p[2]} | Código: {p[0]} | F. Vencimiento: {p[4]} -> {estado}")
        print("=" * 70)

def renovar_prestamo(lista):
    """Gestiona la renovación: bloquea si ya está vencido, si llegó a 3, o suma 2 días."""
    print("\n--- RENOVAR PRÉSTAMO ---")
    codigo = input("Ingrese el código del estudiante para la renovación: ").strip()
    pos = buscar_prestamo(lista, codigo)
    
    if pos == -1:
        print("Resultado: No encontrado en el sistema.")
    else:
        prestamo = lista[pos]
        fecha_venc = datetime.strptime(prestamo[4], "%d/%m/%Y").date()
        hoy = datetime.now().date()
        
        # Si ya está vencido, NO se puede renovar
        if fecha_venc < hoy:
            print(f"Error: El préstamo ya se encuentra VENCIDO (venció el {prestamo[4]}).")
            print("No se puede renovar. Debe registrar la devolución o sacar un nuevo préstamo.")
            return

        # Verificar límite de 3 renovaciones
        if prestamo[5] >= MAX_RENOVACIONES:
            print(f"Resultado: Límite alcanzado (máximo {MAX_RENOVACIONES} renovaciones permitidas).")
        else:
            nueva_fecha_venc = fecha_venc + timedelta(days=2)
            prestamo[4] = nueva_fecha_venc.strftime("%d/%m/%Y")
            prestamo[5] += 1
            print(f"¡Renovación exitosa! Nueva fecha de vencimiento: {prestamo[4]}. Total renovaciones: {prestamo[5]}")

def mostrar_menu():
    print("\n==================================================")
    print("   SISTEMA DE CONTROL DE PRÉSTAMOS - UPN (CHORRILLOS)")
    print("==================================================")
    print("1. Registrar nuevo préstamo (Personal Encargado)")
    print("2. Registrar devolución de material")
    print("3. Buscar préstamo por código institucional")
    print("4. Ordenar préstamos por fecha de vencimiento")
    print("5. Consultar estado del préstamo (Vigente / Vencido)")
    print("6. Renovar préstamo bibliográfico")
    print("7. Consultar préstamos por material bibliográfico")
    print("0. Guardar y salir del sistema")
    print("==================================================")

def main():
    prestamos = cargar_prestamos()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            registrar_prestamo(prestamos)
        elif opcion == "2":
            registrar_devolucion(prestamos)
        elif opcion == "3":
            codigo = input("Ingrese el código a buscar: ").strip()
            pos = buscar_prestamo(prestamos, codigo)
            if pos != -1:
                p = prestamos[pos]
                encargado_txt = f" | Encargado: {p[6]}" if len(p) > 6 else ""
                print(f"\n[Encontrado] Código: {p[0]} | Material: {p[1]} | Alumno: {p[2]} | F. Entrega: {p[3]} | F. Vencimiento: {p[4]} | Renovaciones: {p[5]}{encargado_txt}")
            else:
                print("No se encontró ningún registro con ese código.")
        elif opcion == "4":
            if len(prestamos) > 0:
                ordenar_por_vencimiento(prestamos)
                for p in prestamos:
                    fecha_venc = datetime.strptime(p[4], "%d/%m/%Y")
                    estado_alerta = "⚠️ [VENCIDO]" if datetime.now() > fecha_venc else "✅ [VIGENTE]"
                    print(f"-> Código: {p[0]} | Alumno: {p[2]} | Vence: {p[4]} -> {estado_alerta}")
            else:
                print("No hay registros disponibles para ordenar.")
        elif opcion == "5":
            consultar_estado(prestamos)
        elif opcion == "6":
            renovar_prestamo(prestamos)
        elif opcion == "7":
            consultar_por_material(prestamos)
        elif opcion == "0":
            guardar_prestamos(prestamos)
            print("Datos guardados correctamente en 'prestamos.txt'. Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Por favor, ingrese un número del menú válido.")

if __name__ == "__main__":
    main()