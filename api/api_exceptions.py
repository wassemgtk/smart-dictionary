class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class SchemaError(Exception):
    """Raised when an schema is missing or invalid"""
    pass
