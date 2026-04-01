# Golden Dataset

Tutaj przechowujesz zdjęcia testowe i ich "ground truth" odpowiedzi.

## Struktura

```
golden_dataset/
├── README.md              ← ten plik
├── ground_truth.json      ← weryfikowane ręcznie odpowiedzi
├── item_001.jpg           ← zdjęcie testowe (NIE wrzucaj do repo - patrz .gitignore)
├── item_002.jpg
└── ...
```

## Format ground_truth.json

```json
[
  {
    "image_file": "item_001.jpg",
    "expected": {
      "title": "Samsung Galaxy S21 128GB Czarny",
      "description": "Smartfon w bardzo dobrym stanie. Brak rys na ekranie, lekkie ślady użytkowania z tyłu. Komplet z ładowarką i pudełkiem.",
      "category": "Electronics/Smartphones/Android",
      "estimated_price_pln": 900.0,
      "condition": "Bardzo dobry"
    }
  }
]
```

## Jak zbierać dane testowe

1. Zrób zdjęcia 20-30 urządzeń elektronicznych (lub pobierz z OLX/Allegro)
2. Ręcznie uzupełnij `expected` dla każdego zdjęcia
3. Uruchom `make test-evals` żeby zobaczyć jak model wypada vs ground truth
