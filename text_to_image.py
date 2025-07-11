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
        quality = st.sidebar.selectbox("Quality📚",["standard","hd"])
    else:
        quality = "standard"
    
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
        
        #Sample prompts
        st.markdown("** Quick Start - Sample Prompts:**")
        sample_prompts = {
            "CT SCANNING":[
                    "A high-resolution 3D rendering of a human chest CT scan showing lungs and heart in vivid detail",
                    "Radiology technician operating a modern CT scanner in a bright hospital room.",
                    "Annotated CT scan image showing fractured bones in the forearm"],
            "MRI SCAN":[
                    "A detailed 3D MRI brain scan showing the cerebral cortex and ventricles in vivid colors",
                    "Cross-sectional MRI of the lumbar spine highlighting a herniated disc with high contrast",
                    "Patient lying inside a modern MRI machine, with technicians monitoring the scan",
                    "MRI image showing inflammation in knee joint tissues, with annotated markers"],
            "X-Ray":[
                "A high-resolution X-ray image of a human chest showing ribs, lungs, and heart with clear bone structure",
                "Digital X-ray of a fractured forearm, with clean white bones on a black background.",
                "X-ray scan of a patient’s spine showing scoliosis curvature in a medical report format"
            ]
        }
        
        selected_category = st.selectbox("Category",list(sample_prompts.keys()))
        selected_prompts = st.selectbox("Sample Prompt",sample_prompts[selected_category])
                                        
        if st.button("Use This prompt"):
            st.session_state.prompt_text = selected_prompts
            
        # Text Input
        prompt = st.text_area(
            "Custom Prompt:",
            value=st.session_state.get('prompt_text',' '),
            placeholder=" A scene landscape with mountain",
            height=150
        )
        
        #Generate Button
        if st.button("Generate Image",type="primary",disabled=not (api_key and prompt)):

            if not api_key:
                st.error("Please Enter Your OpenAI key In the sidebar ")
            elif not prompt:
                st.error("Please Provide Text Prompt")
            else:
                try:
                    with st.spinner("Generating Image... This May Take a Few Seconds"):
                        if model == "dall-e-3":
                            response = openai.images.generate(
                                prompt=prompt,
                                model=model,
                                n=n_images,
                                size=size,
                                quality=quality,
                                style=style
                            )
                        else:
                            response = openai.images.generate(
                                prompt=prompt,
                                model=model,
                                n=n_images,
                                size=size
                            )
                        # Print the first image URL
                        image_url = response.data[0].url
                        print(image_url)
                        #Store Generated Images in session State
                        st.session_state.generated_images = response.data
                        st.session_state.current_prompt = prompt
                        st.success("Image Generated Successfully")
                except Exception as e:
                    st.error(f"❌Error Generating Image:{str(e)}")
                    
with col2:
    st.subheader("Generated Images")
    
    #Display Generated Images
    if hasattr(st.session_state,'generated_images') and st.session_state.generated_images:
        for i,image_data in enumerate(st.session_state.generated_images):
            try:
                #download and display image
                image_response = requests.get(image_data.url)
                image = Image.open(io.BytesIO(image_response.content))
                
                st.image(image, caption=f"Generated Image{i+1}", use_container_width=True)
                
                #download Image
                img_buffer = io.BytesIO()
                image.save(img_buffer,format='PNG')
                img_buffer.seek(0)

                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}_{i+1}.png"
                
                st.download_button(
                    label=f"Download Image",
                    data=img_buffer.getvalue(),
                    file_name=filename,
                    mime="image/png"
                )
                
                #show Prompt used
                if hasattr(st.session_state,'current_prompt'):
                    st.caption(f"Prompt:{st.session_state.current_prompt}")
            except Exception as e:
                st.error(f"Error Display Image {i+1}:{str(e)}")
    else:
        st.info("Generated Images will Appear Hear")
