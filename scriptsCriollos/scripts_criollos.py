import frappe
import json

def get_full_salary_assignments():
    # Obtenemos todos los registros con todos sus campos ("*")
    # El nombre técnico es "Salary Structure Assignment"
    records = frappe.get_all("Salary Structure Assignment", fields=["*"])

    if not records:
        print("\n[!] No se encontraron registros en Salary Structure Assignment.\n")
        return

    print(f"\n{'='*60}")
    print(f" REPORTE DETALLADO DE ASIGNACIONES SALARIALES ({len(records)} registros)")
    print(f"{'='*60}\n")

    for i, doc in enumerate(records, 1):
        print(f"--- REGISTRO #{i}: {doc.name} ---")
        
        # Iteramos sobre cada campo del diccionario
        for key, value in doc.items():
            # Formateamos la salida para que sea fácil de leer
            label = key.replace("_", " ").title()
            print(f"{label:<30}: {value}")
        
        print(f"{'-'*60}\n")

# Ejecutar el reporte completo
get_full_salary_assignments()