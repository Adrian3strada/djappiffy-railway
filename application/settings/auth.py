import ast
import os
import logging

auth_logger = logging.getLogger(__name__)
auth_logger.info("Mostrando log de auth settings")

# Firebase authentication settings projects with service account data per project
FIREBASE_AUTH_PROJECTS = ast.literal_eval(os.getenv("FIREBASE_AUTH_PROJECTS", "[]"))
if len(FIREBASE_AUTH_PROJECTS) == 0:
    auth_logger.error("No se encontraron FIREBASE_AUTH_PROJECTS en las variables de entorno")
