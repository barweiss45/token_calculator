#! /usr/bin/env Python3
"""
Tolken Calculation for OpenAI Models

Based on notes found in:
https://github.com/openai/openai-cookbook/blob/297c53430cad2d05ba763ab9dca64309cb5091e9/examples/How_to_count_tokens_with_tiktoken.ipynb

"""

from os import getenv
from dotenv import load_dotenv
import streamlit as st
import tiktoken
import openai

load_dotenv('./.env')

openai.api_key = getenv('API_KEY_OPENAI')

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
    upload_file = st.file_uploader('Please upload a .txt or .pdf File', ['.txt', '.pdf'])
    return upload_file

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_model_encoding(model):
    """_summary_

    Args:
        model (_type_): _description_

    Returns:
        _type_: _description_
    """
    encoding = tiktoken.encoding_for_model(model)
    return encoding 

def get_models():
    """_summary_

    Yields:
        _type_: _description_
    """
    models = openai.Engine.list()
    for model in models['data']:
        yield model['id']

file = load()
if file is not None:
    st.write("File Loaded")
    file_output = file.read().decode()

    tab1, tab2, tab3  = st.tabs(["OpenAI Model and Encoding", "Number of Tokens", "Encodings"])

    with tab1:
        st.subheader("OpenAI Model and Encoding")
        model = st.selectbox('Choose OpenAI Model', list(get_models()))
        encoding = get_model_encoding(model)
        st.write(f"The {model} model uses {encoding.name} for encoding.")

    with tab2:
        st.subheader("Word Block")
        word_block = list(file_output.split())
        st.write(f"Word count: {len(word_block)}")
        num_tokens_from_string = num_tokens_from_string(file_output, encoding.name)
        st.write(f"There are {num_tokens_from_string} token(s) in the file.")
        st.write(f"File Output:\n\n{file_output}")

    with tab3:
        encoded_list = encoding.encode(file_output)
        st.subheader(f"Text Turned into Encoded Tokens - {num_tokens_from_string} token(s)")
        st.table(encoded_list)
