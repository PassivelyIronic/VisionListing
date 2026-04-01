import os
from google import genai
from dotenv import load_dotenv

# Wczytuje .env z obecnego katalogu
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Brak klucza API. Sprawdź ścieżkę do pliku .env!")
else:
    # Wyświetlamy tylko początek klucza dla bezpieczeństwa
    print(f"Pomyślnie załadowano klucz zaczynający się od: {api_key[:8]}...")
    print("Łączenie z API...")
    
    client = genai.Client(api_key=api_key)
    
    print("\n--- Wszystkie dostępne modele dla tego klucza ---")
    try:
        # Pobieramy i wyświetlamy wszystko jak leci
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
         print(f"Wystąpił błąd podczas pobierania modeli: {e}")