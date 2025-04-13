import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class CustomStockEntry(Document): # Or inherit from ERPNext's StockEntry

    def validate(self):
        self.validate_mro_details()

    def on_submit(self):
        self.update_mro_data()

    def on_cancel(self):
        self.reverse_mro_updates()

    def validate_mro_details(self):
        for item in self.items:
            if not item.item_code:
                frappe.throw("Item Code is missing in one of the rows. Please provide a valid Item Code.")
            is_aviation_part = frappe.db.get_value("Item", item.item_code, "is_aviation_part")
            if not is_aviation_part: continue

            # 1. Check Condition Code is provided for Serialized/Batched items
            if item.serial_no or item.batch_no:
                 # Get serial nos/batches involved in this transaction item row
                 s_nos = self.get_serial_nos(item) # Assumes standard method or custom one
                 b_nos = self.get_batch_nos(item) # Assumes standard method or custom one

                 for sn in s_nos:
                     sn_doc = frappe.get_doc("Serial No", sn)
                     if not sn_doc.condition:
                         frappe.throw(f"Serial No {sn} for Item {item.item_code} must have a Condition Code selected.")
                     # Check if condition is appropriate for the movement type
                     # e.g., cannot issue 'US' (Unserviceable) to a Work Order
                     if self.mro_purpose == "Issue to WO" and not frappe.db.get_value("Condition Code", sn_doc.condition, "is_serviceable"):
                          frappe.throw(f"Cannot issue Serial No {sn} (Item: {item.item_code}) with non-serviceable condition '{sn_doc.condition}' to a Work Order.")

                 for bn in b_nos:
                     bn_doc = frappe.get_doc("Batch", bn)
                     if not bn_doc.condition:
                          frappe.throw(f"Batch No {bn} for Item {item.item_code} must have a Condition Code selected.")
                     # Add similar check for batch condition appropriateness


            # 2. Shelf Life Check (for issues/shipments)
            has_shelf_life = frappe.db.get_value("Item", item.item_code, "has_shelf_life")
            if has_shelf_life and self.purpose in ["Material Issue", "Send to Customer", "Material Transfer"]: # Add MRO purposes too
                batches = self.get_batch_nos(item)
                for bn in batches:
                    expiry = frappe.db.get_value("Batch", bn, "shelf_life_expiry_date")
                    if expiry and expiry < nowdate():
                        frappe.throw(f"Batch {bn} for Item {item.item_code} has expired on {expiry}.")

            # 3. LLP Checks (e.g., cannot issue if life expired)
            is_llp = frappe.db.get_value("Item", item.item_code, "is_llp")
            if is_llp and self.purpose in ["Material Issue", "Send to Customer"]: # Add relevant MRO purposes
                 s_nos = self.get_serial_nos(item)
                 for sn in s_nos:
                     sn_doc = frappe.get_doc("Serial No", sn)
                     # Add logic here to check if sn_doc.current_hours/cycles > item.life_limit_hours/cycles
                     # Access limits from Item master
                     # Throw error if expired


    def update_mro_data(self):
        """ Update Serial No life, locations, Core Tracking etc. on submit """
        for item in self.items:
            is_aviation_part = frappe.db.get_value("Item", item.item_code, "is_aviation_part")
            if not is_aviation_part: continue

            s_nos = self.get_serial_nos(item)
            b_nos = self.get_batch_nos(item) # Assuming available

            # 1. Update Serial No / Batch Details
            for sn in s_nos:
                sn_doc = frappe.get_doc("Serial No", sn)
                # Update condition based on certain MRO purposes? (e.g., Receive from Repair sets to SV/OH)
                # Update location details
                sn_doc.current_location_type = "Warehouse" # Simplified
                sn_doc.current_location_name = self.target_warehouse if self.purpose == "Material Receipt" else self.source_warehouse
                # Add logic for Aircraft/Workshop locations based on mro_purpose or linked WO/Aircraft

                # If LLP and being issued/installed, update life (needs more context like hours/cycles from WO)
                # This might be better handled by the Work Order DocType on completion
                # if self.mro_purpose == "Issue to WO":
                #    # Get usage data from Work Order (requires linking)
                #    usage_hours = ...
                #    usage_cycles = ...
                #    sn_doc.update_life_data(hours_added=usage_hours, cycles_added=usage_cycles, work_order=self.work_order)

                sn_doc.save(ignore_permissions=True) # Use with caution

            # Add similar logic for Batch updates if needed (e.g., condition changes)

            # 2. Handle Core Tracking
            is_core_tracked = frappe.db.get_value("Item", item.item_code, "is_core_tracked")
            if is_core_tracked:
                if self.mro_purpose == "Ship to Customer": # Assuming shipment triggers core expectation
                     # Create/Update Core Tracking Doc
                     core_doc = frappe.new_doc("Core Tracking")
                     core_doc.item_code = item.item_code
                     core_doc.serial_no = s_nos[0] if s_nos else None # Link specific SN if applicable
                     core_doc.customer = self.customer # Assuming Delivery Note source
                     core_doc.delivery_note = self.name  # Link back to the Delivery Note
                     core_doc.core_due_date = (nowdate(), 30) # Example due date
                     core_doc.status = "Awaiting Return"
                     core_doc.core_value = frappe.db.get_value("Item", item.item_code, "core_charge")
                     core_doc.insert(ignore_permissions=True)
                elif self.mro_purpose == "Receive Core Return":
                     # Find related Core Tracking Doc and update status to 'Returned', set received condition etc.
                     # ... Core Tracking update logic ...
                     pass

            # 3. Handle Rental Tracking
            # ... Logic for creating/updating Rental Agreement on shipment/receipt ...

    def reverse_mro_updates(self):
        """ Reverse changes made during on_submit """
        # Important: Need robust logic to revert Serial No life, status, location, Core Tracking status etc.
        # This can be complex, especially for life data.
        pass

    # Helper to get serial numbers involved in a Stock Entry Detail row
    # Note: Frappe's default SE might already provide ways to get this depending on version
    def get_serial_nos(self, item_row):
        if item_row.serial_no:
            # For multi-SN rows (textarea), split by newline
            return [sn.strip() for sn in item_row.serial_no.split('\n') if sn.strip()]
        # If SNs are managed differently (e.g., child table), adapt this logic
        return []

    # Helper to get batch numbers involved
    def get_batch_nos(self, item_row):
         if item_row.batch_no:
             return [item_row.batch_no] # Simple case, adapt if needed
         # Logic if batches are in child tables etc.
         return []