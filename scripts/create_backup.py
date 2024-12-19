import subprocess


model_references = [
    # Usuarios
    ("users", "user"),
    ("profiles", "userprofile"),
    # Productos
    ("base", "productkind"),
    # Organizaciones
    ("organizations", "organization"),
    ("profiles", "organizationprofile"),
    ("organizations", "organizationuser"),
    ("organizations", "organizationowner"),
]

def dump_data(index, application, model):
    """
    Funcion para hacer el dumpdata de cada modelo.
    """
    try:
        model_reference = application + '.' + model
        filename = f"{index :03d}_{application}_{model}.json"
        with open(filename, 'w') as f:
            subprocess.run(['python', 'manage.py',
                            'dumpdata', '--indent=4', '--natural-primary', '--natural-foreign',
                            model_reference], stdout=f, check=True)
        print(f"Backup realizado para: {model_reference}")
    except subprocess.CalledProcessError as e:
        print(f"Error al hacer el backup de {model_reference}: {e}")


# Ejecutar el script
if __name__ == '__main__':

    for index, (application, model) in enumerate(model_references):
        dump_data(index, application, model)
