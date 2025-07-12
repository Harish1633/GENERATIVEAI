import os
import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI
from langchain.chains.llm_math.base import LLMMathChain
from langchain.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from fpdf import FPDF
import requests
import tempfile

# Streamlit Page Config
st.set_page_config(page_title="AI Travel Assistant", page_icon="🛩️")
st.title("🛩️ AI Travel Assistant Agent")

# API Key Inputs
api_key = st.text_input("Enter Your OpenAI API Key:", type="password")
weather_api_key = st.text_input("Enter Your OpenWeatherMap API Key (Optional):", type="password")

# Memory Initialization
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, max_token_limit=1000)

# Weather Info Tool
def get_weather(location):
    if not weather_api_key:
        return "Weather API key not provided."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            return f"The current weather in {location} is {temp}°C with {desc}."
        else:
            return "Couldn't fetch weather for the location provided."
    except Exception as e:
        return f"Error fetching weather: {e}"

# PDF Export Function
def export_to_pdf(question, answer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Travel Query:\n{question}\n\nAgent Response:\n{answer}")
    
    # Save to a temporary file for compatibility with Streamlit download
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Main Logic
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    query = st.text_input("Ask Your Travel Question:")

    if query:
        # LLM and Tools Initialization
        llm = OpenAI(temperature=0, max_tokens=256)
        wikipedia = WikipediaAPIWrapper()
        math_chain = LLMMathChain(llm=llm)

        tools = [
            Tool(name="Wikipedia Search", func=wikipedia.run, description="Useful for getting location or place details."),
            Tool(name="Calculator", func=math_chain.run, description="Useful for doing travel budget calculations."),
            Tool(name="Weather Info", func=get_weather, description="Get real-time weather information for a city.")
        ]

        # Agent Initialization
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )

        with st.spinner("Thinking ..."):
            try:
                result = agent_executor.run(query)
                st.success(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                result = None

        # PDF Export Button
        if result and st.button("Export this plan as PDF"):
            pdf_path = export_to_pdf(query, result)
            with open(pdf_path, "rb") as file:
                st.download_button("📄 Download PDF", file, file_name="travel_plan.pdf", mime="application/pdf")
else:
    st.info("Please enter your OpenAI API Key to start.")