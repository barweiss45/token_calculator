#! /usr/bin/env Python3

"""
Tolken Calculation for OpenAI Models

Based on notes found in:
https://github.com/openai/openai-cookbook/blob/297c53430cad2d05ba763ab9dca64309cb5091e9/examples/How_to_count_tokens_with_tiktoken.ipynb

"""

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from streamlit.logger import get_logger
import tiktoken
import openai
from langchain.document_loaders import (
    Docx2txtLoader, 
    PyMuPDFLoader, 
    TextLoader
    )

load_dotenv()

# Set Logging
logger = get_logger(__name__)

openai.api_key = os.environ['OPENAI_API_KEY']

if openai.api_key:
    print("API KEY LOADED")
else:
    st.error('No API Key found')

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_models():
    """_summary_

    Yields:
        _type_: _description_
    """
    models = openai.Engine.list()['data']
    for model in models:
        if model.id in tiktoken.model.MODEL_TO_ENCODING:
            yield model.id

def get_model_encoding(model: str) -> tiktoken.Encoding|Exception:
    """
    get_model_encoding get correct encoding for the selected model.

    Args:
        model (str): the model retrieved from model in st.selectbox
                     widget.
    Returns:
        tiktoken.Encoding|Exception: Encoding string | KeyError exception
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return encoding
    except KeyError as e:
        st.exception(e)

def session_state(key,value):
    if key not in st.session_state:
        st.session_state[key] = value
        logger.info(f"Session State: {key} added.")
    elif key in st.session_state:
        st.session_state[key] = value
        logger.info(f"Session State: {key} updated")

st.title('ChatGPT TokenCalculator')
st.title("Tiktoken - OpenAI Token Calculator")

upload_file = st.file_uploader('Please upload a .txt, .docx, & .pdf File', ['.txt', '.pdf', '.docx'])

uploadcontainer = st.container()
if upload_file is not None:
    uploadcontainer.write("File Loaded")
    working_dir = Path.cwd()
    fp= str(working_dir.joinpath(f"document_repo",f"{upload_file.name}"))
    with open(fp,"wb") as f:
        f.write(upload_file.getbuffer())
        uploadcontainer.success(f"Saved File {upload_file.name} to the Application Repository (./document_repo)")
    uploadcontainer.write("Choose the file the file that you would like to determine the number of tokens for.")
    select_file = uploadcontainer.selectbox("Choose a File", options=os.listdir("./document_repo"), index=0, key="SelectFile")

    tab1, tab2, tab3  = st.tabs(["OpenAI Model and Encoding", "Number of Tokens", "Encodings"])
    with tab1:
        st.subheader("OpenAI Model and Encoding")
        model = st.selectbox('Choose OpenAI Model', options = list(get_models()))
        encoding = get_model_encoding(model)
        st.write(f"The {model} model uses {encoding.name} for encoding.")

    with tab2:
        st.header("Word Block")
        st.divider()
        file = str(working_dir.joinpath(f"document_repo",f"{st.session_state.SelectFile}"))
        if st.button("Calculate Tokens"):
            with st.spinner("Processing..."):
                if Path(file).suffix == '.docx':
                    data = Docx2txtLoader(file).load()
                    document = data[0].page_content
                elif Path(file).suffix == '.pdf':
                    data = PyMuPDFLoader(file).load()
                    document = ",".join([doc.page_content for doc in data])
                elif Path(file).suffix == '.txt':
                    data = TextLoader(file).load()
                    document = ",".join([doc.page_content for doc in data])
                else:
                    st.error("There was an issue with processing the file")
                word_block = list(document.split())
                st.write(f"Word count: {len(word_block)}")
                num_tokens_from_string = num_tokens_from_string(document, encoding.name)
                st.write(f"There are {num_tokens_from_string} token(s) in the file.")
                st.divider()
                session_state("document",document)
                session_state("num_of_tokens", num_tokens_from_string)
                with st.expander("View Uploaded Document"):
                    st.write(f"File Output, truncated to the first 5000 Characters:\n\n{document[:5000]}")
        if uploadcontainer.button("Reset All Values"):
            session_state("document", "")
            session_state("num_of_tokens", "")
            document = ""
            num_of_tokens = ""
            select_file = None
            st.experimental_rerun()

    with tab3:
        if st.button("Calculate in Embeddings"):
            with st.spinner("Processing..."):
                try:
                    document = st.session_state['document']
                    num_tokens_from_string = st.session_state['num_of_tokens']
                except Exception as e:
                    st.exception(e)
                encoded_list = encoding.encode(document)
                st.subheader(f"Text Turned into Encoded Tokens - {num_tokens_from_string} token(s). Only the first 50 will be shown.")
                st.table(encoded_list[:50])
