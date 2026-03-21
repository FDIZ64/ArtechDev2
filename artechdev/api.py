# apps/artechcustom/artechcustom/api.py
import frappe 
from frappe.utils import now_datetime

def audit_salary_backlog(doc, method=None):
    """
    Guarda una versión con fecha y hora exacta del documento.
    """
    ignored = {"modified", "modified_by", "creation", "owner", "docstatus", "idx", "name", "naming_series"}
    ahora = now_datetime()

    # 1. Extraer valores actuales
    current_snapshot = {}
    for df in doc.meta.fields:
        if df.fieldname not in ignored and df.fieldtype not in ["Table", "Section Break", "Column Break", "HTML"]:
            val = doc.get(df.fieldname)
            current_snapshot[df.fieldname] = str(val) if val is not None else ""

    # 2. Buscar la versión vigente (sin fecha_hasta o con fecha muy lejana)
    # Usamos una fecha lejana para identificar el registro 'actual'
    last_version = frappe.get_all("Salary Version History", 
        filters={
            "ref_name": doc.name, 
            "ref_doctype": doc.doctype, 
            "fecha_hasta": [">", "2099-01-01 00:00:00"]
        },
        fields=["name"], limit=1)

    if not last_version:
        # Primera vez que se registra este documento
        create_new_version(doc, current_snapshot, ahora)
    else:
        # Comparar con la versión anterior
        last_details = {d.field_name: d.value for d in frappe.get_all("Salary Version Detail", 
                        filters={"parent": last_version[0].name}, fields=["field_name", "value"])}
        
        hay_cambios = any(current_snapshot.get(f) != last_details.get(f) for f in current_snapshot)
        
        if hay_cambios:
            # Sincronismo exacto: cerramos el viejo ahora y abrimos el nuevo ahora
            frappe.db.set_value("Salary Version History", last_version[0].name, "fecha_hasta", ahora)
            create_new_version(doc, current_snapshot, ahora)

def create_new_version(doc, values, timestamp):
    """Inserta el registro padre y sus hijos con Datetime"""
    emp = doc.get("employee") or (doc.name if doc.doctype == "Employee" else None)
    
    new_v = frappe.get_doc({
        "doctype": "Salary Version History",
        "ref_doctype": doc.doctype,
        "ref_name": doc.name,
        "employee": emp,
        "fecha_desde": timestamp,
        "fecha_hasta": "2099-12-31 23:59:59",
        "details": [{"field_name": k, "value": v} for k, v in values.items()]
    })
    new_v.insert(ignore_permissions=True)
    frappe.db.commit()