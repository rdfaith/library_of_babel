import os
import pathlib


def get_path(file_name: str):
    ROOT_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
    print(ROOT_DIR)
    full_path = os.path.join(ROOT_DIR, pathlib.Path(file_name))
    print(full_path)
    return full_path
