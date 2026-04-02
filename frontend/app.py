import httpx
import streamlit as st
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="quick-sell",
    page_icon="⚡",
    layout="centered",
)

tab_new, tab_listings = st.tabs(["Nowe ogłoszenie", "Opublikowane"])

# --- Zakładka: Nowe ogłoszenie ---
with tab_new:
    st.header("Nowe ogłoszenie")
    st.caption("Wgraj zdjęcie urządzenia — AI uzupełni ogłoszenie za Ciebie.")

    uploaded_file = st.file_uploader(
        "Wybierz zdjęcie (JPG, PNG, WEBP)",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_file:
        st.image(Image.open(uploaded_file), use_column_width=True)
        uploaded_file.seek(0)

        if st.button("Analizuj zdjęcie", type="primary"):
            with st.spinner("AI analizuje zdjęcie..."):
                try:
                    response = httpx.post(
                        f"{BASE_URL}/extract-listing-info",
                        files={"image": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                        timeout=30,
                    )
                    response.raise_for_status()
                    st.session_state["ai_data"] = response.json()["data"]
                except httpx.ConnectError:
                    st.error("Nie można połączyć się z backendem. Czy działa `make run-backend`?")
                    st.stop()
                except httpx.HTTPStatusError as e:
                    st.error(f"Błąd API ({e.response.status_code}): {e.response.text}")
                    st.stop()

    if "ai_data" in st.session_state:
        data = st.session_state["ai_data"]

        st.success("Gotowe. Sprawdź i edytuj dane przed publikacją.")
        st.divider()

        col1, col2 = st.columns([3, 1])
        with col1:
            title = st.text_input("Tytuł", value=data["title"])
        with col2:
            price = st.number_input(
                "Cena (PLN)",
                value=float(data["estimated_price_pln"]),
                step=50.0,
            )

        conditions = ["Nowy", "Bardzo dobry", "Dobry", "Akceptowalny", "Do naprawy"]
        condition = st.selectbox(
            "Stan",
            options=conditions,
            index=conditions.index(data["condition"]),
        )

        category = st.text_input("Kategoria", value=data["category"])
        description = st.text_area("Opis", value=data["description"], height=120)

        confidence = data["confidence"]
        st.caption(
            f"Pewność modelu: {confidence:.0%} — "
            + ("wysoka" if confidence >= 0.8 else "niska — sprawdź dane")
        )

        st.divider()
        if st.button("Opublikuj ogłoszenie", type="primary"):
            payload = {
                "title": title,
                "description": description,
                "category": category,
                "estimated_price_pln": price,
                "condition": condition,
                "confidence": confidence,
            }
            try:
                r = httpx.post(f"{BASE_URL}/listings", json=payload, timeout=10)
                r.raise_for_status()
                listing_id = r.json()["id"]
                st.success(f"Ogłoszenie opublikowane (ID: {listing_id}). Znajdziesz je w zakładce Opublikowane.")
                del st.session_state["ai_data"]
                st.balloons()
            except httpx.HTTPStatusError as e:
                st.error(f"Błąd zapisu ({e.response.status_code}): {e.response.text}")

# --- Zakładka: Opublikowane ogłoszenia ---
with tab_listings:
    st.header("Opublikowane ogłoszenia")

    try:
        response = httpx.get(f"{BASE_URL}/listings", timeout=10)
        response.raise_for_status()
        listings = response.json()["data"]
    except httpx.ConnectError:
        st.warning("Nie można połączyć się z backendem.")
        listings = []
    except httpx.HTTPStatusError:
        st.warning("Błąd pobierania ogłoszeń.")
        listings = []

    if not listings:
        st.info("Brak opublikowanych ogłoszeń.")
    else:
        for item in listings:
            with st.expander(f"{item['title']} — {item['price_pln']:.0f} PLN"):
                st.write(f"**Kategoria:** {item['category']}")
                st.write(f"**Stan:** {item['condition']}")
                st.write(f"**Opis:** {item['description']}")
                if item["confidence"]:
                    st.caption(f"Pewność modelu: {item['confidence']:.0%} | Dodano: {item['created_at']}")