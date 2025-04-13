# permissions.py

class Permissions:
    def __init__(self, role):
        self.role = role
        self.permissions = self._get_permissions()

    def _get_permissions(self):
        # Define permissions based on the JSON data
        roles_permissions = {
            "Technician": {"read": 1, "write": 0, "create": 0, "delete": 0},
            "Stores Manager": {"read": 1, "write": 1, "create": 1, "delete": 1},
            "Inspector": {"read": 1, "write": 0, "create": 0, "delete": 0},
        }
        return roles_permissions.get(self.role, {"read": 0, "write": 0, "create": 0, "delete": 0})

    def can_read(self):
        return self.permissions.get("read", 0) == 1

    def can_write(self):
        return self.permissions.get("write", 0) == 1

    def can_create(self):
        return self.permissions.get("create", 0) == 1

    def can_delete(self):
        return self.permissions.get("delete", 0) == 1


# Example usage
if __name__ == "__main__":
    technician = Permissions("Technician")
    print("Technician Permissions:")
    print("Read:", technician.can_read())
    print("Write:", technician.can_write())
    print("Create:", technician.can_create())
    print("Delete:", technician.can_delete())

    manager = Permissions("Stores Manager")
    print("\nStores Manager Permissions:")
    print("Read:", manager.can_read())
    print("Write:", manager.can_write())
    print("Create:", manager.can_create())
    print("Delete:", manager.can_delete())

    inspector = Permissions("Inspector")
    print("\nInspector Permissions:")
    print("Read:", inspector.can_read())
    print("Write:", inspector.can_write())
    print("Create:", inspector.can_create())
    print("Delete:", inspector.can_delete())