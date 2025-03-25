from source import pg, os, pathlib

def get_path(file_name: str):
    ROOT_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
    full_path = os.path.join(ROOT_DIR, pathlib.Path(file_name))
    return full_path