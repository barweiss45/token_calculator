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
import tiktoken
import openai
from langchain.document_loaders import Docx2txtLoader, PyMuPDFLoader

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

if openai.api_key:
    print("API KEY LOADED")
else:
    st.error('No API Key found')

st.title('ChatGPT TokenCalculator')

def load():
    """_summary_

    Returns:
        _type_: _description_
    """    
    upload_file = st.file_uploader('Please upload a .txt, .docx, & .pdf File', ['.txt', '.pdf', '.docx'])
    return upload_file

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
    select_file = uploadcontainer.selectbox("Choose a File", options=os.listdir("./document_repo"), key="SelectFile")
    
    tab1, tab2, tab3  = st.tabs(["OpenAI Model and Encoding", "Number of Tokens", "Encodings"])
    with tab1:
        st.subheader("OpenAI Model and Encoding")
        model = st.selectbox('Choose OpenAI Model', options = list(get_models()))
        encoding = get_model_encoding(model)
        st.write(f"The {model} model uses {encoding.name} for encoding.")

    with tab2:
        st.header("Word Block")
        st.divider()
        if uploadcontainer.button("Calculate Tokens"):
            with st.spinner("Processing..."):
                if Path(fp).suffix == '.docx':
                    data = Docx2txtLoader(fp).load()
                    document = data[0].page_content
                if Path(fp).suffix == '.pdf':
                    data = PyMuPDFLoader(fp).load()
                    document = ",".join([doc.page_content for doc in data])
                word_block = list(document.split())
                st.write(f"Word count: {len(word_block)}")
                num_tokens_from_string = num_tokens_from_string(document, encoding.name)
                st.write(f"There are {num_tokens_from_string} token(s) in the file.")
                st.divider()
                with st.expander("View Uploaded Document"):
                    st.write(f"File Output:\n\n{document}")

    with tab3:
        if uploadcontainer.button("Calculate in Embeddings"):
            with st.spinner("Processing..."):
                encoded_list = encoding.encode(document)
                st.subheader(f"Text Turned into Encoded Tokens - {num_tokens_from_string} token(s)")
                st.table(encoded_list)
