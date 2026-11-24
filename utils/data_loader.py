import json
import os


def load_incidents():
    """Load all simulated 911 incidents from data/incidents.json"""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "incidents.json")
    with open(os.path.normpath(path), "r") as f:
        return json.load(f)


def load_resources():
    """Load all simulated emergency resources from data/resources.json"""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "resources.json")
    with open(os.path.normpath(path), "r") as f:
        return json.load(f)
