import streamlit as st
import requests
from PIL import Image

# ============================================================
# ONCOLENS AI — WEB APP
# ============================================================

st.set_page_config(
    page_title="OncoLens AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "https://billion-accepted-tongue-vol.trycloudflare.com/predict"

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main {background: #f7f9fc;}
    .block-container {padding-top: 2rem; max-width: 1250px;}
    .hero {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827, #312e81);
        color: white;
        margin-bottom: 22px;
    }
    .hero h1 {margin: 0 0 8px 0; font-size: 38px;}
    .hero p {margin: 0; opacity: .9; font-size: 17px;}
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 18px rgba(0,0,0,.04);
    }
    .small {color: #6b7280; font-size: 13px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Patient ID from URL if present
# -----------------------------
params = st.query_params
url_patient_id = params.get("patientId", "")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("# 🧬 OncoLens AI")
    st.caption("Breast Histopathology Analysis")
    st.divider()
    page = st.radio("Navigation", ["Analysis", "About"], index=0)
    st.divider()
    st.caption("Research / educational prototype")

# -----------------------------
# About page
# -----------------------------
if page == "About":
    st.title("About OncoLens AI")
    st.write(
        "OncoLens AI is an AI-assisted breast histopathology research prototype "
        "designed to classify uploaded histopathology images as benign or malignant."
    )
    st.info("Model pipeline: Phikon-v2 embeddings → Logistic Regression")
    st.markdown("### Current capabilities")
    st.markdown(
        "- Patient ID capture\n"
        "- Histopathology image upload and preview\n"
        "- AI-assisted benign/malignant prediction\n"
        "- Confidence and class probabilities\n"
        "- Technical API response for demonstration"
    )
    st.warning(
        "This is a research and educational demonstration. It is not a medical diagnosis "
        "and must not be used for clinical decision-making."
    )
    st.stop()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🔬 OncoLens AI</h1>
        <p>Intelligent Breast Histopathology Analysis Platform</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "Upload a breast histopathology image, enter a patient identifier, and run the "
    "AI-assisted classification pipeline."
)

# -----------------------------
# Patient + image
# -----------------------------
left, right = st.columns([1, 1.5], gap="large")

with left:
    st.markdown("### 👤 Patient Information")
    patient_id = st.text_input(
        "Patient ID",
        value=url_patient_id,
        placeholder="PT-7734",
    )
    if patient_id:
        st.caption(f"Current patient: {patient_id}")

    st.markdown("### 🧠 AI Pipeline")
    st.info("Phikon-v2 + Logistic Regression\n\nEmbedding: 1024 dimensions")

with right:
    st.markdown("### 🖼️ Histopathology Image")
    uploaded_file = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        try:
            preview = Image.open(uploaded_file)
            st.image(preview, caption="Uploaded histopathology image", width=650)
        except Exception:
            st.error("Unable to preview this image.")

st.divider()

# -----------------------------
# Analyze
# -----------------------------
if st.button("🔬 Analyze Image", type="primary", use_container_width=True):
    if not patient_id.strip():
        st.warning("Please enter a Patient ID.")
        st.stop()

    if uploaded_file is None:
        st.warning("Please upload a histopathology image.")
        st.stop()

    with st.spinner("Sending image to OncoLens AI... Please wait."):
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "image/png",
                )
            }
            response = requests.post(API_URL, files=files, timeout=300)

            if response.status_code != 200:
                st.error(f"AI server returned HTTP {response.status_code}.")
                st.code(response.text[:2000])
                st.stop()

            result = response.json()
            prediction = str(result.get("prediction", "unknown"))
            confidence = float(result.get("confidence", 0))
            probabilities = result.get("probabilities", {}) or {}
            benign = float(probabilities.get("benign", 0))
            malignant = float(probabilities.get("malignant", 0))

            st.session_state["last_result"] = {
                "patient_id": patient_id,
                "prediction": prediction,
                "confidence": confidence,
                "benign": benign,
                "malignant": malignant,
                "raw": result,
            }

        except requests.exceptions.Timeout:
            st.error("The AI server took too long to respond. Please try again.")
            st.stop()
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not connect to the AI server: {exc}")
            st.stop()
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

# -----------------------------
# Result dashboard
# -----------------------------
if "last_result" in st.session_state:
    r = st.session_state["last_result"]

    st.markdown("## 📋 Analysis Result")
    st.caption(f"Patient ID: **{r['patient_id']}**")

    if r["prediction"].lower() == "malignant":
        st.error(f"### Prediction: {r['prediction'].upper()}")
    else:
        st.success(f"### Prediction: {r['prediction'].upper()}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Confidence", f"{r['confidence'] * 100:.2f}%")
    c2.metric("Benign Probability", f"{r['benign'] * 100:.2f}%")
    c3.metric("Malignant Probability", f"{r['malignant'] * 100:.2f}%")

    st.progress(max(0.0, min(1.0, r["confidence"])))

    with st.expander("View technical AI response"):
        st.json(r["raw"])

    st.warning(
        "Research/Demo Use Only — this AI output is not a medical diagnosis. "
        "A qualified medical professional must review clinical findings."
    )
else:
    st.markdown("### 📊 Analysis Result")
    st.info("Upload an image and click **Analyze Image** to generate a result.")

st.divider()
st.caption("OncoLens AI • Breast Histopathology Analysis System • Research Prototype")
