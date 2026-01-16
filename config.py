import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_CONFIG = {
    "miz": {
        "miz_path": "miz file folder",
        "miz_url": "https://ci.appveyor.com/project/132nd-VirtualWing/trma"
    },
    "git": {
        "repo_path": "repo folder",
        "repo_url": "https://github.com/132nd-vWing/TRMA"
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
