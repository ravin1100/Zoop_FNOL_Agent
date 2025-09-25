from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# --- LLM setup ---
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
