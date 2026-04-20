# app/utils/validators.py

def validate_request(data):
    if not data:
        return False, "JSON vazio"

    if "info" not in data:
        return False, "Campo 'info' ausente"

    if "orders" not in data:
        return False, "Campo 'orders' ausente"

    if not isinstance(data["orders"], list):
        return False, "'orders' deve ser uma lista"

    return True, None