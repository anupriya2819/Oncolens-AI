import streamlit as st
import requests

# ============================================================
# ONCOLENS AI - BREAST HISTOPATHOLOGY ANALYSIS
# ============================================================

st.set_page_config(
    page_title="OncoLens AI",
    page_icon="🔬",
    layout="wide"
)

# Your current Colab API
API_URL = "https://billion-accepted-tongue-vol.trycloudflare.com/predict"

# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #0b1220;
}

.title {
    font-size: 42px;
    font-weight: 700;
    color: #ffffff;
}

.subtitle {
    font-size: 20px;
    color: #cbd5e1;
}

.result-box {
    padding: 25px;
    border-radius: 15px;
    background-color: #172033;
    margin-top: 20px;
}

.prediction {
    font-size: 32px;
    font-weight: 700;
}

.metric {
    font-size: 20px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    '<div class="title">🧬 OncoLens AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Breast Histopathology Analysis System</div>',
    unsafe_allow_html=True
)

st.write(
    "Upload a breast histopathology image and let the "
    "OncoLens AI model analyze it."
)

st.write("**AI Model:** Phikon-v2 + Logistic Regression")
st.write("**Classes:** Benign / Malignant")

st.divider()


# ------------------------------------------------------------
# Patient ID
# ------------------------------------------------------------

patient_id = st.text_input(
    "🆔 Patient ID",
    value="PT-100"
)


# ------------------------------------------------------------
# Image Upload
# ------------------------------------------------------------

uploaded_file = st.file_uploader(
    "🔬 Upload Histopathology Image",
    type=["png", "jpg", "jpeg"]
)


# ------------------------------------------------------------
# Image Preview
# ------------------------------------------------------------

if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Uploaded Histopathology Image",
        width=500
    )


# ------------------------------------------------------------
# Analyze Button
# ------------------------------------------------------------

if st.button(
    "🔬 Analyze Image",
    type="primary",
    use_container_width=True
):

    if uploaded_file is None:

        st.warning(
            "Please upload a histopathology image first."
        )

    else:

        with st.spinner(
            "Sending image to OncoLens AI..."
        ):

            try:

                # Prepare file for API
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                # Send image to your AI API
                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=300
                )

                # Check API response
                if response.status_code != 200:

                    st.error(
                        f"API Error: {response.status_code}"
                    )

                else:

                    result = response.json()

                    # ------------------------------------------------
                    # Extract result
                    # ------------------------------------------------

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

                    benign_probability = probabilities.get(
                        "benign",
                        0
                    )

                    malignant_probability = probabilities.get(
                        "malignant",
                        0
                    )

                    # ------------------------------------------------
                    # Display result
                    # ------------------------------------------------

                    st.divider()

                    st.subheader(
                        "🔬 OncoLens AI Result"
                    )

                    st.write(
                        f"**Patient ID:** {patient_id}"
                    )

                    st.markdown(
                        f"""
                        <div class="result-box">

                        <div class="prediction">
                        Prediction: {prediction.upper()}
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # ------------------------------------------------
                    # Metrics
                    # ------------------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Confidence",
                            f"{confidence * 100:.2f}%"
                        )

                    with col2:

                        st.metric(
                            "Benign Probability",
                            f"{benign_probability * 100:.2f}%"
                        )

                    with col3:

                        st.metric(
                            "Malignant Probability",
                            f"{malignant_probability * 100:.2f}%"
                        )

                    # ------------------------------------------------
                    # Status
                    # ------------------------------------------------

                    st.success(
                        "✅ Prediction completed successfully."
                    )

                    # ------------------------------------------------
                    # Raw API result
                    # ------------------------------------------------

                    with st.expander(
                        "View AI API Response"
                    ):

                        st.json(result)

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ The AI server took too long to respond."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to the OncoLens AI server."
                )

            except Exception as e:

                st.error(
                    f"❌ Prediction failed: {str(e)}"
                )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.caption(
    "OncoLens AI — Breast Histopathology Analysis System"
)
