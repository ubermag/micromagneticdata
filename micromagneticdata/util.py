import os
import re

def drives_number(name):
    dirs = os.listdir(name)
    numbers = [int(re.findall('[0-9]+', d)[0]) for d in dirs]
    return sorted(numbers)