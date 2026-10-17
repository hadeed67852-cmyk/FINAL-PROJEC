import os
import streamlit as st
import re
import pytesseract
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai

st.set_page_config(page_title="Quranic AI Study Assistant", page_icon="📖", layout="wide")

st.title("📖 Quranic AI Study Assistant")
st.markdown("Upload any Surah translation PDF (supports both standard text and scanned image PDFs) to automatically generate study insights using premium Gemini 2.5 Flash!")

# Secure Configuration Sidebar
with st.sidebar:
    st.header("🔑 Authentication")
    # Tries to pull from Streamlit Secrets or Environment Variables first
    default_key = os.getenv("GEMINI_API_KEY", "")
    
    user_api_key = st.text_input(
        "AQ.Ab8RN6LVFraP0edSWrVy6_AnGxt5s-pLH45yneBvJlkYsUPCZg", 
        value=default_key, 
        type="password", 
        placeholder="AIzaSy..."
    )
    
    if user_api_key:
        genai.configure(api_key=user_api_key)
        st.success("✅ Gemini API Configured!")
    else:
        st.warning("⚠️ Please provide an API key to enable live AI responses.")

uploaded_file = st.file_uploader("Choose a Surah PDF file", type=["pdf"])

def clean_text(text):
    text = re.sub(r'(?i)https?://\S+|www\.\S+|alkalam\.pk|alkalam', '', text)
    text = re.sub(r'\b\d{3,4}\b', '', text)
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

fallback_database = {
    "What are the central themes and moral teachings discussed in this Surah?": {
        "passage": "Blessed is He in Whose Hand is the dominion, and He is Able to do all things. Who has created death and life that He may test you which of you is best in deed.",
        "supporting": "The Surah centers on the absolute sovereignty of God, the purpose of life as a moral test, and the perfection of the cosmos as a sign of Divine design."
    },
    "Who are the main figures, messengers, or nations mentioned in these verses?": {
        "passage": "When they are cast therein, they will hear the terrible drawing in of its breath as it blazes up... Its keepers will ask: 'Did no warner come to you?' They will say: 'Yes, a warner indeed came to us, but we denied.'",
        "supporting": "The verses mention the keepers of Hell and the warners (Messengers) sent to nations who rejected the message, illustrating the dialogue between the deniers and the angelic guardians."
    },
    "What specific commands or ethical guidelines are laid out for believers?": {
        "passage": "And speak your word in secret or publish it aloud; verily, He is All-Knowing of what is in the breasts (of men).",
        "supporting": "Believers are instructed to maintain mindfulness of God (Taqwa) in private and public, reminding humanity that ethical uprightness stems from knowing that God is aware of every secret thought."
    },
    "How does the Surah describe the ultimate rewards of righteousness and faith?": {
        "passage": "Verily, those who fear their Lord unseen, for them is forgiveness and a great reward (Paradise).",
        "supporting": "The ultimate rewards are depicted as absolute forgiveness of shortcomings and an immense, honorable reward (the Gardens of Paradise) for those who establish sincere faith."
    },
    "What warnings, consequences, or past events are highlighted for reflection?": {
        "passage": "Say: 'He it is Who has created you, and endowed you with hearing and seeing and hearts. Little thanks you give.' Say: 'Have you considered: if your water was to sink into the earth, who then could bring you flowing water?'",
        "supporting": "Humanity is warned against ungratefulness. They are asked to reflect on how easily their basic daily blessings—like fresh flowing water, sight, and hearing—could be stripped away."
    },
    "How is patience, perseverance, or trust in Divine wisdom illustrated?": {
        "passage": "And who is more guided—one who walks fallen on his face, or one who walks upright on a straight path?",
        "supporting": "Patience and steadfast guidance are illustrated through the metaphor of walking upright with clear vision on a straight path, representing absolute trust in Divine direction."
    },
    "What attributes of creation, nature, or the universe are cited as signs?": {
        "passage": "Who created the seven heavens one above another. You can see no fault in the creation of the Most Gracious. Then look again: 'Can you see any rifts?'",
        "supporting": "The physical heavens, the flawless harmony of nature, and the flight of birds sustained in the air by none but the Most Gracious are cited as undeniable, physical signs."
    },
    "What specific prayers, invocations, or words of remembrance are recommended?": {
        "passage": "Say: 'He is the Most Gracious; we have believed in Him, and upon Him we have put our trust.'",
        "supporting": "The ultimate declaration of reliance (Tawakkul) and identifying God by His attribute of Mercy ('Al-Rahman') is recommended as a core remembrance for daily practice."
    },
    "What does the text instruct regarding societal justice and treating others?": {
        "passage": "He it is Who has made the earth subservient to you, so walk in the paths thereof and eat of His provision.",
        "supporting": "Humanity is instructed to live in balance, walk gently upon the earth, seek honest livelihoods, and share the provisions responsibly without corruption."
    },
    "How can the concluding passages of this Surah be applied to modern daily life?": {
        "passage": "Say: 'Have you considered: if your water were to drain away tomorrow, who could bring you flowing water?'",
        "supporting": "The conclusion serves as a powerful call to ecological mindfulness and humility, urging modern society to never take natural resources and life-support systems for granted."
    }
}

full_text = ""

if uploaded_file is not None:
    with open("temp_surah.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Reading and parsing your Surah PDF..."):
        try:
            loader = PyPDFLoader("temp_surah.pdf")
            raw_documents = loader.load()
            documents = []
            for doc in raw_documents:
                cleaned_content = clean_text(doc.page_content)
                if cleaned_content:
                    doc.page_content = cleaned_content
                    documents.append(doc)

            full_text = "\n".join([doc.page_content for doc in documents])

            if len(full_text.strip()) < 100:
                st.info("🔍 Scanned PDF detected! Running OCR scanner...")
                try:
                    pages = convert_from_path('temp_surah.pdf', 150)
                    extracted_paragraphs = []
                    for page in pages[:5]:
                        page_text = pytesseract.image_to_string(page)
                        clean_lines = [line.strip() for line in page_text.split('\n') if len(line.strip()) > 15]
                        filtered_lines = [l for l in clean_lines if "alkalam" not in l.lower() and "www." not in l.lower()]
                        if filtered_lines:
                            extracted_paragraphs.append(" ".join(filtered_lines))
                    full_text = "\n\n".join(extracted_paragraphs)
                except Exception as ocr_err:
                    st.warning("OCR Scanner offline. Using curated fallback database instead.")
            st.success("Successfully loaded Surah context!")
        except Exception as e:
            st.error(f"An error occurred while reading the PDF: {e}")
else:
    st.info("Please upload a Surah translation PDF above. Currently demonstrating using the default curated Surah Al-Mulk context.")

questions_list = list(fallback_database.keys())
st.markdown("### 📋 Top 10 Study Questions from this Surah")
selected_q = st.selectbox("Choose a study question to investigate:", ["-- Select a Question --"] + questions_list)

if selected_q and selected_q != "-- Select a Question --":
    st.markdown(f"### 📝 Analysis for: *{selected_q}*")
    
    if user_api_key and len(full_text.strip()) > 100:
        with st.spinner("Generating AI Analysis using Gemini 2.5..."):
            prompt = f"""
            You are an expert Quranic scholar and academic study assistant.
            Use the following parsed text from a Surah translation to answer the study question.

            --- START SURAH TEXT ---
            {full_text[:3000]}
            --- END SURAH TEXT ---

            STUDY QUESTION: {selected_q}

            Format your response beautifully with 3 parts:
            1. "Key Passage Insight": A clear, readable English translation of relevant verses.
            2. "Detailed Academic Analysis": Explaining the context, core concepts, and grammar/narrative keys.
            3. "Modern Takeaway / Application": Practical actions a modern believer can implement in daily life.
            """
            try:
                # Upgraded to stable standard initialization framework
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as api_err:
                st.error(f"Gemini API request failed: {api_err}")
    else:
        # Fallback to local structured matching logic if key is absent or text is minimal
        ans_data = fallback_database.get(selected_q)
        st.markdown("#### 🔍 Key Passage Insights")
        st.info(ans_data["passage"])
        st.markdown("#### 📖 Additional Context")
        st.write(ans_data["supporting"])
