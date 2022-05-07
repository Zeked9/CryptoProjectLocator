import yaml
import requests
import os
import json

def get_bearer_token():
    with open("../secrets.yaml", 'r') as stream:
        doc = yaml.safe_load(stream)
        bearer_token = doc['secrets']['bearer']

    return bearer_token