from enum import Enum

class Role(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class RecordType(str, Enum):
    income = "income"
    expense = "expense"
