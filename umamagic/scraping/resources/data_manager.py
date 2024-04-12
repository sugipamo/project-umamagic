import os
BASEPATH = os.path.dirname(os.path.abspath(__file__))

def save(name, content):
    path = os.path.join(BASEPATH, name)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w") as f:
        f.write(content)

def load(name):
    path = os.path.join(BASEPATH, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is not found.")
    with open(path, "r") as f:
        return f.read()
    

def delete(name):
    path = os.path.join(BASEPATH, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is not found.")
    os.remove(path)
    if not os.listdir(os.path.dirname(path)):
        os.rmdir(os.path.dirname(path))