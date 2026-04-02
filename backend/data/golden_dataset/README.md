# Golden Dataset

Zdjęcia testowe i zweryfikowane ręcznie odpowiedzi ("ground truth") służące do ewaluacji modelu.

## Struktura

```
golden_dataset/
├── README.md              ← ten plik
├── ground_truth.json      ← ręcznie zweryfikowane dane (21 pozycji)
├── item_001.jpg           ← zdjęcia testowe (nie są wersjonowane w repo)
└── ...
```

## Format ground_truth.json

```json
[
  {
    "image_file": "item_001.jpg",
    "expected": {
      "title": "Samsung Galaxy S10 128GB Czarny",
      "description": "Opis ogłoszenia...",
      "category": "Electronics/Smartphones/Android",
      "estimated_price_pln": 450.0,
      "condition": "Dobry",
      "confidence": null
    }
  }
]
```

Pole `confidence` jest zawsze `null` w ground truth — model generuje je samodzielnie podczas ewaluacji.

## Jak uruchomić ewaluację

```bash
make test-evals
```

Testy sprawdzają: dokładność kategorii, odchylenie ceny (tolerancja 30%), pewność modelu (>0.5) i długość tytułu.