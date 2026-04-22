# backend/test_db_connection.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Ajouter le chemin actuel pour s'assurer que .env est lu correctement
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("----------------------------------------")
print("🔍 TEST DE CONNEXION BASE DE DONNÉES")
print(f"URL chargée : {DATABASE_URL}")
print("----------------------------------------")

if not DATABASE_URL:
    print("❌ ERREUR : DATABASE_URL n'est pas définie dans le fichier .env")
    sys.exit(1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ SUCCÈS : Connexion établie avec succès !")
except Exception as e:
    print("❌ ÉCHEC : Impossible de se connecter.")
    print(f"Message d'erreur : {str(e)}")
    
    if "password authentication failed" in str(e):
        print("\n💡 Indication : Le mot de passe dans .env ne correspond pas à celui de Docker.")
    elif "could not connect to server" in str(e):
        print("\n💡 Indication : Docker n'est pas lancé ou Postgres ne tourne pas sur ce port.")
print("----------------------------------------")
