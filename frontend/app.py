import httpx
import streamlit as st
from PIL import Image

API_URL = "http://localhost:8000/api/v1/extract-listing-info"

st.set_page_config(
    page_title="quick-sell",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ quick-sell")
st.caption("Wgraj zdjęcie urządzenia — AI uzupełni ogłoszenie za Ciebie.")

uploaded_file = st.file_uploader(
    "Wybierz zdjęcie (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file:
    st.image(Image.open(uploaded_file), use_column_width=True)
    uploaded_file.seek(0)

    if st.button("✨ Analizuj zdjęcie", type="primary"):
        with st.spinner("AI analizuje zdjęcie..."):
            try:
                response = httpx.post(
                    API_URL,
                    files={"image": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()["data"]

            except httpx.ConnectError:
                st.error("Nie można połączyć się z backendem. Czy działa `make run-backend`?")
                st.stop()
            except httpx.HTTPStatusError as e:
                st.error(f"Błąd API ({e.response.status_code}): {e.response.text}")
                st.stop()

        st.success("Gotowe! Sprawdź i edytuj dane przed publikacją.")
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

        condition = st.selectbox(
            "Stan",
            options=["Nowy", "Bardzo dobry", "Dobry", "Akceptowalny", "Do naprawy"],
            index=["Nowy", "Bardzo dobry", "Dobry", "Akceptowalny", "Do naprawy"].index(
                data["condition"]
            ),
        )

        category = st.text_input("Kategoria", value=data["category"])
        description = st.text_area("Opis", value=data["description"], height=120)

        confidence = data["confidence"]
        st.caption(
            f"Pewność modelu: {confidence:.0%} — "
            + ("✅ wysoka" if confidence >= 0.8 else "⚠️ sprawdź dane")
        )

        st.divider()
        if st.button("📤 Opublikuj ogłoszenie", type="primary"):
            st.balloons()
            st.success("Ogłoszenie opublikowane! (demo — brak zapisu do bazy)")