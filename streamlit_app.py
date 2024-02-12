import streamlit as st
import instructor
from openai import OpenAI
from pydantic import BaseModel
import datetime
import PyPDF2

"""
# Extract data from a PDF invoice using ChatGPT
"""

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"

client = instructor.patch(
    OpenAI(
        api_key=openai_api_key,
    ),
)

invoice_file = st.file_uploader("Upload a PDF invoice", type=["pdf"])

class Invoice(BaseModel) :
    date: datetime.date = datetime.datetime.now()
    reference: str = ""
    supplier: str = ""
    currency: str = ""
    total_amount: float = 0.0
    total_tax_amount: float = 0.0
    description: str = ""

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

invoice = Invoice()
if invoice_file:
    pdf_text = extract_text_from_pdf(invoice_file)
    invoice = client.chat.completions.create(
        temperature=0,
        response_model=Invoice,
        messages=[
            {
                "role": "user",
                "content": f"""
                    Extract, 
                    while making sure currency is in ISO 4217 format,
                    infer the reference from the invoice number,
                    and the date in ISO 8601 format:
                    
                    {pdf_text}
                """,
            }
        ],
        model="gpt-3.5-turbo",
    )

st.header("Extracted JSON data:")
st.json(invoice.model_dump_json(), expanded=True)



