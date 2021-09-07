def validate_site_name(site_name: str):
    for char in site_name:
        ascii_char = ord(char)

        if ascii_char < 65:
            return False
        elif ascii_char > 122:
            return False
        elif 90 < ascii_char < 97:
            return False

    return True
