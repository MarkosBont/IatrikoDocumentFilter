import streamlit as st
import re
import zipfile
from io import BytesIO
from PyPDF2 import PdfReader

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        pass
    return text

def matches_criteria(text):
    psad_matches = re.findall(r'PSA-D\s+([0-9]*\.?[0-9]+)', text)
    psad_valid = any(float(match) < 0.15 for match in psad_matches)
    pirad_match = re.search(r'PI-RADS\s+[45]\b', text)
    return psad_valid and pirad_match

def create_zip_of_filtered_files(filtered_files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in filtered_files:
            file.seek(0)  # rewind the file before reading
            zip_file.writestr(file.name, file.read())
    zip_buffer.seek(0)
    return zip_buffer

# --- Streamlit UI ---
st.title("PDF Filter App")
st.markdown("""
Upload PDF files to filter by:
- **PSD** followed by a number **less than 0.15**
- **RSID** followed by **4** or **5**
""")

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    matching_files = []
    st.subheader("Processing files...")

    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)
        if matches_criteria(text):
            matching_files.append(uploaded_file)

    if matching_files:
        st.success(f"{len(matching_files)} matching file(s) found:")
        for file in matching_files:
            st.markdown(f"- {file.name}")

        # Create ZIP and add download button
        zip_buffer = create_zip_of_filtered_files(matching_files)
        st.download_button(
            label="📁 Download Filtered PDFs as ZIP",
            data=zip_buffer,
            file_name="filtered_pdfs.zip",
            mime="application/zip"
        )
    else:
        st.warning("No matching files found.")