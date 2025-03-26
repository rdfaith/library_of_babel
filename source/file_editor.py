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