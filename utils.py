import re
from functools import lru_cache
import os


def extract_tokens(data: dict) -> str:
    pattern = re.compile(r'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response
