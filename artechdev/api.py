# apps/artechdev/artechdev/api.py
import frappe
from frappe.utils import add_days, today, now_datetime

def audit_salary_backlog(doc, method=None):
    """
    Guarda una versión completa del DocType en tablas Padre-Hijo
    cuando detecta cambios en cualquier campo de valor.
    """
    # Campos que no queremos trackear en la tabla hija
    ignored_fields = {
        "modified", "modified_by", "creation", "owner", "docstatus", 
        "idx", "name", "naming_series", "lft", "rgt"
    }

    fecha_hoy = today()

    # 1. Obtener los valores actuales del documento
    current_values = {}
    for df in doc.meta.fields:
        if df.fieldname not in ignored_fields and df.fieldtype not in ["Table", "Section Break", "Column Break", "HTML", "Button"]:
            val = doc.get(df.fieldname)
            current_values[df.fieldname] = str(val) if val is not None else ""

    # 2. Buscar la última versión vigente en el historial
    last_history = frappe.get_all("Salary Version History", 
        filters={
            "ref_name": doc.name, 
            "ref_doctype": doc.doctype,
            "fecha_hasta": "2099-12-31"
        },
        fields=["name"], 
        limit=1
    )

    if not last_history:
        # ESCENARIO: Registro nuevo -> Grabamos la primera foto
        create_version_record(doc, current_values, fecha_hoy)
    else:
        # ESCENARIO: Existe historial -> Comparamos contra los hijos del registro vigente
        last_details = {d.field_name: d.value for d in frappe.get_all("Salary Version Detail", 
                        filters={"parent": last_history[0].name}, 
                        fields=["field_name", "value"])}
        
        # Verificar si hay alguna diferencia entre la foto vieja y la nueva
        has_changes = False
        for field, value in current_values.items():
            if str(value) != str(last_details.get(field, "")):
                has_changes = True
                break
        
        if has_changes:
            # Cerramos la vigencia del registro anterior hoy
            frappe.db.set_value("Salary Version History", last_history[0].name, "fecha_hasta", fecha_hoy)
            # Creamos la nueva foto vigente desde mañana
            create_version_record(doc, current_values, add_days(fecha_hoy, 1))

def create_version_record(doc, values_dict, f_desde):
    """Inserta el registro Padre con sus filas Hijas"""
    
    # Intentamos obtener el empleado (para filtrar fácil después)666
    employee = doc.get("employee")
    if not employee and doc.doctype == "Employee":
        employee = doc.name
 
    new_version = frappe.get_doc({
        "doctype": "Salary Version History",
        "ref_doctype": doc.doctype,
        "ref_name": doc.name,
        "employee": employee,
        "fecha_desde": f_desde,
        "fecha_hasta": "9999-12-31",
        "details": [
            {"field_name": field, "value": val} 
            for field, val in values_dict.items()
        ]
    })
    
    # El naming se construye: {ref_doctype}-{ref_name}-{fecha_desde}
    new_version.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()