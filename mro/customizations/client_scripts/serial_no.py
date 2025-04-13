import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, flt

class CustomSerialNo(Document): # Or inherit from ERPNext's SerialNo if extending directly
    # --- On Update / Save ---
    def validate(self):
        self.set_defaults()
        self.validate_condition()
        self.update_status_based_on_location() # Example helper

    def on_update_after_submit(self):
        # Potentially trigger updates elsewhere if needed after submission
        pass

    def set_defaults(self):
        if not self.condition and self.item_code:
            default_condition = frappe.db.get_value("Item", self.item_code, "default_condition")
            if default_condition:
                self.condition = default_condition

        # Calculate expiry based on received date/mfg date if not set manually
        # ... (Add logic based on Batch info or Stock Entry info if available)

    def validate_condition(self):
        if not self.condition:
            # Maybe allow saving without condition initially, but require it before specific stock moves?
            # frappe.throw("Condition Code is mandatory for Aviation Part Serial Numbers.")
            pass # Decide on strictness

    def update_status_based_on_location(self):
        # Example: automatically set status based on warehouse type or custom location fields
        # if self.warehouse and frappe.db.get_value("Warehouse", self.warehouse, "warehouse_type") == "Quarantine":
        #     self.status = "Inactive" # Or a custom MRO status
        # else:
        #      self.status = "Active"
        pass

    # --- LLP Logic ---
    def update_life_data(self, hours_added=0, cycles_added=0, transaction_date=None, aircraft=None, work_order=None, movement_type="Usage"):
        """
        Call this method from Stock Entry or Work Order completion
        to update the life used on an LLP.
        """
        if not frappe.db.get_value("Item", self.item_code, "is_llp"):
            return # Only applies to LLPs

        transaction_date = transaction_date or nowdate()

        self.current_hours = flt(self.current_hours) + flt(hours_added)
        self.current_cycles = flt(self.current_cycles) + flt(cycles_added)

        # Update TSN/CSN or TSO/CSO based on logic (e.g., if movement was overhaul)
        self.tsn = flt(self.tsn) + flt(hours_added) # Simplified example
        self.csn = flt(self.csn) + flt(cycles_added) # Simplified example

        # Create Part Life Log entry
        log_entry = frappe.new_doc("Part Life Log")
        log_entry.serial_no = self.name
        log_entry.item_code = self.item_code
        log_entry.transaction_date = transaction_date
        log_entry.movement_type = movement_type
        log_entry.hours_added = hours_added
        log_entry.cycles_added = cycles_added
        log_entry.cumulative_hours = self.current_hours
        log_entry.cumulative_cycles = self.current_cycles
        log_entry.aircraft = aircraft # Link to Aircraft DocType if exists
        log_entry.work_order = work_order # Link to Work Order DocType if exists
        # Add more relevant fields
        log_entry.insert(ignore_permissions=True) # Use with caution

        # Check against limits
        self.check_life_limits()
        self.save(ignore_permissions=True) # Save changes to Serial No

    def check_life_limits(self):
        limits = frappe.db.get_value("Item", self.item_code,
                                     ["life_limit_hours", "life_limit_cycles", "life_limit_days"])
        if not limits: return

        limit_hours, limit_cycles, limit_days = limits

        if limit_hours and flt(self.current_hours) >= flt(limit_hours):
            frappe.msgprint(f"Serial No {self.name} has reached its Hour limit.", indicator="orange", alert=True)
            # Potentially set condition to Unserviceable or Requires Inspection
            # self.condition = "US" # Find the correct Condition Code name

        if limit_cycles and flt(self.current_cycles) >= flt(limit_cycles):
             frappe.msgprint(f"Serial No {self.name} has reached its Cycle limit.", indicator="orange", alert=True)
             # self.condition = "US"

        # Calendar limit check needs installation date stored on Serial No or via Life Log
        # ... add calendar check logic ...
