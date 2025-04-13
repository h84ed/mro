import frappe
from frappe.model.document import Document

class MROWorkOrder(Document):
    def on_submit(self):
        # Link parts, labor logs, certifications, etc.
        pass
    
@frappe.whitelist()
def generate_work_order_number():
    return f"WO-{frappe.utils.now_datetime().strftime('%Y%m%d-%H%M%S')}"




