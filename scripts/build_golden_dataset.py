"""
Skrypt do budowania golden dataset.

Użycie:
    python scripts/build_golden_dataset.py --images-dir path/do/zdjec

Można uruchamiać wielokrotnie — pomija już wypełnione wpisy.
"""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import httpx

GOLDEN_DIR = Path(__file__).parent.parent / "backend" / "data" / "golden_dataset"
GROUND_TRUTH_FILE = GOLDEN_DIR / "ground_truth.json"
API_URL = "http://localhost:8000/api/v1/extract-listing-info"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
RATE_LIMIT_DELAY = 15   # sekundy między requestami
RETRY_WAIT = 90         # sekundy czekania przy 429
MAX_RETRIES = 3


def copy_images(images_dir: Path) -> list[Path]:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for i, src in enumerate(sorted(images_dir.iterdir()), start=1):
        if src.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        dest_name = f"item_{i:03d}{src.suffix.lower()}"
        dest = GOLDEN_DIR / dest_name
        if not dest.exists():
            shutil.copy2(src, dest)
            print(f"  ✅ Skopiowano: {src.name} → {dest_name}")
        copied.append(dest)
    return copied


def load_existing() -> dict[str, dict]:
    """Wczytuje istniejący ground_truth.json i zwraca dict {image_file: entry}."""
    if not GROUND_TRUTH_FILE.exists():
        return {}
    with open(GROUND_TRUTH_FILE, encoding="utf-8") as f:
        entries = json.load(f)
    return {e["image_file"]: e for e in entries}


def is_todo(entry: dict) -> bool:
    return entry["expected"]["title"] == "TODO"


def call_api(image_path: Path) -> dict | None:
    suffix = image_path.suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")

    for attempt in range(MAX_RETRIES):
        try:
            with open(image_path, "rb") as f:
                response = httpx.post(
                    API_URL,
                    files={"image": (image_path.name, f, media_type)},
                    timeout=30,
                )
            if response.status_code in (429, 500):
                print(f"  ⏳ Rate limit, czekam {RETRY_WAIT}s (próba {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_WAIT)
                continue
            response.raise_for_status()
            return response.json()["data"]
        except httpx.ConnectError:
            print("❌ Nie można połączyć się z backendem. Uruchom: make run-backend")
            sys.exit(1)
        except Exception as e:
            print(f"  ⚠️  Błąd: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_WAIT)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", type=Path, required=True)
    args = parser.parse_args()

    if not args.images_dir.exists():
        print(f"❌ Folder nie istnieje: {args.images_dir}")
        sys.exit(1)

    print(f"\n📁 Kopiuję zdjęcia z: {args.images_dir}")
    images = copy_images(args.images_dir)

    if not images:
        print("❌ Brak obsługiwanych zdjęć.")
        sys.exit(1)

    existing = load_existing()
    todo_images = [img for img in images
                   if img.name not in existing or is_todo(existing[img.name])]

    skipped = len(images) - len(todo_images)
    print(f"\n📊 Łącznie: {len(images)} zdjęć | ✅ Już wypełnione: {skipped} | 🔍 Do analizy: {len(todo_images)}")

    if not todo_images:
        print("\n✅ Wszystkie wpisy są już wypełnione!")
        return

    estimated = len(todo_images) * RATE_LIMIT_DELAY // 60 + 1
    print(f"⏱  Szacowany czas: ~{estimated} min\n")

    for i, image_path in enumerate(todo_images):
        print(f"🔍 [{i+1}/{len(todo_images)}] Analizuję: {image_path.name}")
        data = call_api(image_path)

        if data is None:
            existing[image_path.name] = {
                "image_file": image_path.name,
                "expected": {
                    "title": "TODO", "description": "TODO", "category": "TODO",
                    "estimated_price_pln": 0.0, "condition": "TODO", "confidence": None,
                },
            }
            print(f"  ⚠️  Pominięto — uzupełnij ręcznie")
        else:
            data["confidence"] = None
            existing[image_path.name] = {"image_file": image_path.name, "expected": data}
            print(f"  📝 {data['title']} | {data['category']} | {data['estimated_price_pln']} PLN")

        # Zapisuj po każdym zdjęciu — żeby nie stracić danych przy przerwie
        ordered = [existing[img.name] for img in images if img.name in existing]
        with open(GROUND_TRUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(ordered, f, ensure_ascii=False, indent=2)

        if i < len(todo_images) - 1:
            print(f"  💤 Czekam {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)

    todo_count = sum(1 for e in existing.values() if is_todo(e))
    print(f"\n✅ Gotowe! Wypełnione: {len(existing) - todo_count}/{len(existing)}")
    if todo_count:
        print(f"⚠️  Pozostało {todo_count} wpisów TODO — uruchom skrypt ponownie lub uzupełnij ręcznie.")
    print("\n💡 Przejrzyj ground_truth.json i popraw błędne wartości (szczególnie ceny i stany).")


if __name__ == "__main__":
    main()