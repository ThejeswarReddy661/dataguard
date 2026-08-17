def is_missing(value):
    """
    Return True when a value should be treated as missing.
    """

    return value is None or value.strip() == ""


def get_percentage(count, total):
    """
    Convert a count into a percentage.
    """

    if total == 0:
        return 0.0

    return (count / total) * 100


def get_severity(percentage):
    """
    Convert an issue percentage into a severity level.
    """

    if percentage == 0:
        return "NONE"

    elif percentage <= 5:
        return "LOW"

    elif percentage <= 20:
        return "MEDIUM"

    else:
        return "HIGH"