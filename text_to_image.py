import streamlit as st
import openai
import requests
from PIL import Image
import io
import os
from datetime import datetime
from dotenv import load_dotenv

#Load Environemtn Variable
load_dotenv()

#Configure page
st.set_page_config(page_title="AI IMAGE GENERATION HUB", page_icon="🖼️", layout="wide")

#title and Discription
st.title("🖼️ Image Generative AI 🤖")
st.markdown("Generating Stunnig Images From Text Description Using OpenAI's DALL-E 🤖Model")


#Side bar for settings
st.sidebar.header("Settings⚙️")

#API key Input

default_api_key = os.getenv("OPENAI_API_KEY","")
if default_api_key:
    st.sidebar.success("API Key is Loaded From the Environment")
    api_key = default_api_key
else:
    api_key = st.sidebar.text_input("OPENAI_API_KEY",type="password",placeholder="Enter Serial Key",help="Enter your Open AI Key")

if api_key:
    openai.api_key = api_key
    
    #Image generator parameter
    st.sidebar.subheader("Generate Parameter")
    #model Selection
    model= st.sidebar.selectbox("Model🌀",["dall-e-3","dall-e-2"],help="Choose the DAll-E Model Version")
    #Image Quality
    if model == "dall-e-3":
        size_option = ["1024x1024","1024x1792","1792x1024"]
    else:
        size_option = ["256x256","512x512","1024x1024"]
    
    size = st.sidebar.selectbox("Image Size📏", size_option)
    
    #Quality ( only for Dall-E 3)
    if model == "dall-e-3":
        quality = st.sidebar.selectbox("Quality📚",["Standard","HD"])
    else:
        quality = "Standard"
    
    #style (Only for Dall-e-3)
    if model == "dall-e-3":
        style = st.sidebar.selectbox("Style",["vivid","Natural"])
    else:
        style = "Natural"
    
    if model == "dall-e-2":
        n_images = st.sidebar.slider("Number of Images",1,5,1)
    else:
        n_images = 1
        
    #main content area
    col1,col2 = st.columns([1,1])
    
    with col1:
        st.subheader("Text Prompt")