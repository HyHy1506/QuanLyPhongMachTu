import enum


class FunctionUserPatientEnum(enum.Enum):
    REGISTER_EXAMINATION = "REGISTER_EXAMINATION"
    HISTORY_REGISTER = "HISTORY_REGISTER"
    HISTORY_EXAMINATION = "HISTORY_EXAMINATION"
    NOTIFICATION = "NOTIFICATION"

def format_number(number):
    return "{:,.0f}".format(number)