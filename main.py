import pdfplumber
import streamlit as st
import pandas as pd
import os
import io
import tempfile
import time


def _tmp_pdf(bytes):
    tmp = tempfile.NamedTemporaryFile(delete=False)

    # Open the file for writing.
    with open(tmp.name, 'wb') as f:
        f.write(bytes)

    return tmp.name


def plumb(file):
    print(str(file))
    time.sleep(5)
    if not os.path.exists(file):
        file = _tmp_pdf(file)

    print(file)

    return pdfplumber.open(file)


def metadata(pdf):
    if type(pdf) != pdfplumber.pdf.PDF:
        pdf = plumb(pdf)

    mine = {"Pages": len(pdf.pages), "Images": len(pdf.images)}

    return {**mine, **pdf.metadata}


def text(pdf, page=1):
    if type(pdf) != pdfplumber.pdf.PDF:
        pdf = plumb(pdf)

    return pdf.pages[page].extract_text()


def tables(pdf, page=1):
    if type(pdf) != pdfplumber.pdf.PDF:
        pdf = plumb(pdf)

    return pdf.pages[page].extract_tables()


def render(pdf, page=1):
    if type(pdf) != pdfplumber.pdf.PDF:
        pdf = plumb(pdf)

    return pdf.pages[page].to_image()


def st_ui():
    st.set_page_config(layout = "wide")
    st.title("Plumb a PDF!")

    st.write("This Daisi can help you extract images, tables, text, and metadata from arbitrary PDF files.")
    with st.sidebar:
        uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        pdf = plumb(bytes_data)
    else:
        st.text("Using example.pdf for illustration")
        pdf = plumb("example.pdf")

    text_tab, table_tab, image_tab = st.tabs(["Text", "Tables", "Images"])

    with text_tab:
        st.markdown("## Metadata")
        st.json(metadata(pdf))

        st.markdown("## Text")
        st.text(text(pdf))

    with table_tab:
        page = st.selectbox("Page to Plumb", options=list(range(len(pdf.pages))))
        my_tables = tables(pdf, page=page)

        for table in my_tables:
            st.dataframe(pd.DataFrame(table))

    with image_tab:
        page2 = st.selectbox("Page to Render", options=list(range(len(pdf.pages))))
        image = render(pdf, page=page2)

        with io.BytesIO() as output:
            image.save(output, format="PNG")
            contents = output.getvalue()

            st.image(contents)

if __name__ == "__main__":
    st_ui()