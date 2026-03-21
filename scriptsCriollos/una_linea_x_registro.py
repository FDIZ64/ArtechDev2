import frappe

def list_all_physical_fields():
    doctype = "Salary Structure Assignment"
    
    if not frappe.db.table_exists(doctype):
        print(f"\n[!] El DocType {doctype} no existe.")
        return

    # 1. Obtener los campos, filtrando los que NO están en la DB (Section Break, Column Break, HTML, etc)
    meta = frappe.get_meta(doctype)
    # Solo queremos campos que NO sean de tipo 'Break' o 'HTML' y que no sean virtuales
    physical_fields = [f.fieldname for f in meta.fields if f.fieldtype not in frappe.model.no_value_fields]
    
    # 2. Agregar campos estándar de auditoría
    all_query_fields = ["name"] + physical_fields + ["creation", "owner", "docstatus"]
    
    # 3. Consultar
    records = frappe.get_all(doctype, fields=all_query_fields)
    
    if not records:
        print("\n[!] No hay registros.")
        return

    # 4. Imprimir encabezado y datos en una sola línea
    header = " | ".join([f.upper() for f in all_query_fields])
    print(f"\n{header}\n" + "-" * len(header))

    for r in records:
        line = " | ".join([str(r.get(f) if r.get(f) is not None else "") for f in all_query_fields])
        print(line)

list_all_physical_fields()