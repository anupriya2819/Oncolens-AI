import streamlit as st
import requests

# ============================================================
# ONCOLENS AI
# ============================================================

st.set_page_config(
    page_title="OncoLens AI",
    page_icon="🔬",
    layout="wide"
)

# Temporary backend for TESTING ONLY
API_URL = "https://billion-accepted-tongue-vol.trycloudflare.com/predict"


# ============================================================
# HEADER
# ============================================================

st.title("🧬 OncoLens AI")
st.subheader("Breast Histopathology Analysis System")

st.write(
    "Upload a breast histopathology image for "
    "AI-assisted benign/malignant classification."
)

st.info(
    "Model: Phikon-v2 + Logistic Regression | "
    "Embedding dimension: 1024"
)

st.divider()


# ============================================================
# PATIENT ID
# ============================================================

patient_id = st.text_input(
    "🆔 Patient ID",
    placeholder="Example: PT-7734"
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "🔬 Upload Histopathology Image",
    type=["png", "jpg", "jpeg"]
)


# ============================================================
# IMAGE PREVIEW
# ============================================================

if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded Histopathology Image",
        width=500
    )


# ============================================================
# ANALYZE
# ============================================================

if st.button(
    "🔬 Analyze Image",
    type="primary",
    use_container_width=True
):

    if not patient_id:

        st.warning("Please enter a Patient ID.")

    elif uploaded_file is None:

        st.warning("Please upload a histopathology image.")

    else:

        with st.spinner(
            "Analyzing image with OncoLens AI..."
        ):

            try:

                # Send image to Python backend
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=300
                )

                if response.status_code != 200:

                    st.error(
                        f"API Error: {response.status_code}"
                    )

                else:

                    result = response.json()

                    prediction = result.get(
                        "prediction",
                        "unknown"
                    )

                    confidence = result.get(
                        "confidence",
                        0
                    )

                    probabilities = result.get(
                        "probabilities",
                        {}
                    )

                    benign = probabilities.get(
                        "benign",
                        0
                    )

                    malignant = probabilities.get(
                        "malignant",
                        0
                    )

                    # ------------------------------------------------
                    # RESULT
                    # ------------------------------------------------

                    st.divider()

                    st.header(
                        "🔬 OncoLens AI Result"
                    )

                    st.write(
                        f"**Patient ID:** {patient_id}"
                    )

                    if prediction.lower() == "malignant":

                        st.error(
                            f"Prediction: {prediction.upper()}"
                        )

                    else:

                        st.success(
                            f"Prediction: {prediction.upper()}"
                        )

                    # ------------------------------------------------
                    # METRICS
                    # ------------------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Confidence",
                            f"{confidence * 100:.2f}%"
                        )

                    with col2:

                        st.metric(
                            "Benign",
                            f"{benign * 100:.2f}%"
                        )

                    with col3:

                        st.metric(
                            "Malignant",
                            f"{malignant * 100:.2f}%"
                        )

                    # ------------------------------------------------
                    # API RESPONSE
                    # ------------------------------------------------

                    with st.expander(
                        "View technical result"
                    ):

                        st.json(result)

            except Exception as e:

                st.error(
                    f"Connection error: {e}"
                )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    "⚠️ Research and educational use only. "
    "This AI output is not a medical diagnosis."
)
