# user_functions.py
import pickle
import os

SAVE_DIR = "saved_vars"

os.makedirs(SAVE_DIR, exist_ok=True)


def save_var(var, name):
    path = os.path.join(SAVE_DIR, f"{name}.pkl")
    
    if os.path.exists(path):
        print(f"Soubor '{name}.pkl' už existuje. Uložení bylo zrušeno.")
        return

    with open(path, "wb") as f:
        pickle.dump(var, f)
    print(f"Uloženo do {path}")
    
    
def load_var(name):
    path = os.path.join(SAVE_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        print(f"Soubor {path} neexistuje.")
        return None
    with open(path, "rb") as f:
        var = pickle.load(f)
    print(f"Načteno ze souboru {path}")
    return var

def delete_var(name):
    path = os.path.join(SAVE_DIR, f"{name}.pkl")

    if os.path.exists(path):
        os.remove(path)
        print(f"Proměnná '{name}' byla smazána.")
    else:
        print(f"Proměnná '{name}' neexistuje.")
        
        
def list_saved_vars(_):
    if not os.path.exists(SAVE_DIR):
        print("Složka s proměnnými neexistuje.")
        return

    files = [f[:-4] for f in os.listdir(SAVE_DIR) if f.endswith(".pkl")]
    if files:
        print("Uložené proměnné:")
        for f in files:
            print(f" - {f}")
    else:
        print("Žádné proměnné nejsou uložené.")


def append(lst, val):
    lst.append(val)
    return lst

def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def unique(lst):
    return list(dict.fromkeys(lst))

def my_print(list):
    for item in list:
        print(item)
        print()
        print()


def print_head(data, n=1000):
    if hasattr(data, "data"):
        data = data.data

    for i, row in enumerate(data):
        if i >= n:
            print(f"... (zobrazeno prvních {n} řádků z celkem {len(data)})")
            break
        print(row)
