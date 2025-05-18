import os
import subprocess
from tqdm import tqdm


def load_fixtures():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(current_dir, "__fixtures")
    print("Fixtures directory: {}".format(fixtures_dir))
    pattern = "0"

    # Obtiene todos los archivos que coincidan con el patrón
    fixtures = [f for f in os.listdir(fixtures_dir) if f.startswith(pattern)]
    print(f"Fixtures found: {fixtures}")
    print("Loading fixtures...")

    # Carga cada fixture usando manage.py loaddata
    for fixture in tqdm(fixtures):
        fixture_path = os.path.join(fixtures_dir, fixture)
        print(f"Loading fixture: {fixture_path}")
        subprocess.run(["python", "manage.py", "loaddata", fixture_path])


if __name__ == "__main__":
    load_fixtures()
