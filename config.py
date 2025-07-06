import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONSTANTS_FILE = os.path.join(BASE_DIR, "constants.json")
LEVELS_DIR = os.path.join(BASE_DIR,"src", "levels")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

CONSTANTS = load_json(CONSTANTS_FILE)