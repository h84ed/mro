def version_control(doc, method):
    doc.version = int(doc.version or 0) + 1
    frappe.msgprint(f"New version {doc.version} created for {doc.file_name}")