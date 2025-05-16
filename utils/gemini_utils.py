import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar el modelo Gemini con LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

# Función principal para obtener respuesta de Gemini usando LangChain
def obtener_respuesta(prompt):
    try:
        prompt_template = ChatPromptTemplate.from_template("{mensaje}")
        cadena = prompt_template | llm
        response = cadena.invoke({"mensaje": prompt})

        # Si el contenido es tipo dict con partes estructuradas, tomamos 'text'
        if hasattr(response, "content"):
            contenido = response.content
        elif isinstance(response, dict) and "text" in response:
            contenido = response["text"]
        else:
            raise ValueError("La respuesta de Gemini está vacía o no estructurada correctamente.")

        return contenido.strip()

    except Exception as e:
        print(f"❌ Error al obtener respuesta de Gemini (LangChain): {e}")
        return ""

