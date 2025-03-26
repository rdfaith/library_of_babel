def load_file(filename: str) -> dict:
    settings = dict()

    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = value
    return settings

def update_file(filename: str, settings: dict):
    with open(filename, 'w') as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")

def reset_file(filename: str):
    current_settings = load_file(filename)
    for key in current_settings.keys():
        if key == "HEX_1.csv":
            current_settings[key] = 99.99
        else:
            current_settings[key] = False
    update_file(filename, current_settings)