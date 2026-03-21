def exportador_nomina_artech():
    import csv
    import frappe
    import os

    # Configuración de opciones
    opciones = {
        "1": {"dt": "Employee", "file": "empleados.csv"},
        "2": {"dt": "Salary Component", "file": "componentes_salariales.csv"},
        "3": {"dt": "Salary Structure", "file": "estructuras_salariales.csv"},
        "4": {"dt": "Salary Structure Assignment", "file": "asignaciones_salariales.csv"}
    }

    print("\n" + "="*40)
    print(" SELECCIONA QUÉ DESEAS EXPORTAR:")
    print("="*40)
    print("1. Empleados")
    print("2. Componentes Salariales")
    print("3. Estructuras Salariales")
    print("4. Asignaciones de Estructuras")
    print("="*40)
    
    seleccion = input("Escribe el número (1-4): ")

    if seleccion not in opciones:
        print("\n[!] Opción no válida. Abortando...")
        return

    doctype = opciones[seleccion]["dt"]
    filename = opciones[seleccion]["file"]

    if not frappe.db.table_exists(doctype):
        print(f"\n[!] El DocType '{doctype}' no parece estar instalado.")
        return

    # 1. Obtener metadatos reales (excluyendo campos visuales de Frappe)
    meta = frappe.get_meta(doctype)
    campos_fisicos = [f.fieldname for f in meta.fields if f.fieldtype not in frappe.model.no_value_fields]
    columnas = ["name"] + campos_fisicos + ["creation", "docstatus"]

    # 2. Consultar datos
    print(f" Consultando {doctype}...")
    datos = frappe.get_all(doctype, fields=columnas)

    if not datos:
        print(f"[-] No se encontraron registros para {doctype}.")
        return

    # 3. Crear el CSV para Excel (UTF-8 con BOM y separador ;)
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=columnas, delimiter=';')
            writer.writeheader()
            for r in datos:
                # Limpiar valores None para que Excel no muestre la palabra "None"
                fila_limpia = {k: (v if v is not None else "") for k, v in r.items()}
                writer.writerow(fila_limpia)
        
        print(f"\n✅ ¡Éxito! Archivo generado: {os.path.abspath(filename)}")
        print(f"💡 Ahora búscalo en WinSCP y ábrelo con Excel.")

    except Exception as e:
        print(f"[-] Error al guardar el archivo: {str(e)}")

# Ejecutar el menú
exportador_nomina_artech()