import frappe
from frappe import _

def get_salary_assignments():
    # Buscamos todos los registros del DocType
    # Nota: El nombre técnico es "Salary Structure Assignment"
    assignments = frappe.get_all(
        "Salary Structure Assignment", 
        fields=["employee", "employee_name", "salary_structure", "from_date", "base"],
        filters={"docstatus": ["<", 2]}  # Filtra para no mostrar los cancelados
    )

    if not assignments:
        print("\n[!] No se encontraron registros en Asignación Salarial.\n")
        return

    print(f"\n{'EMPLEADO':<15} | {'NOMBRE':<25} | {'ESTRUCTURA':<20} | {'DESDE':<12} | {'SUELDO BASE':<10}")
    print("-" * 90)

    for d in assignments:
        print(f"{d.employee:<15} | {d.employee_name or 'N/A':<25} | {d.salary_structure:<20} | {str(d.from_date):<12} | {d.base:>10,.2f}")
    
    print("-" * 90)
    print(f"Total de registros: {len(assignments)}\n")

# Ejecutar la función
get_salary_assignments()