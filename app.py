import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter 
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

def fetch_pdf_content(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def generate_article_content(keyword, vectorstore, content_length, language):
    llm = ChatOpenAI(model='gpt-4')
    
    prompt_template = """
    Based on the information from the uploaded documents and your knowledge about {keyword},
    write a comprehensive article that covers the following aspects:

    1. Introduction to {keyword}
    2. Key points and best practices related to {keyword}
    3. Common challenges and how to overcome them
    4. Future trends or predictions in this area
    5. Conclusion with actionable advice

    Use a professional tone and structure the article with clear headings (h2) and subheadings (h3).
    Wrap each paragraph in <p> tags.
    Aim for an article length of about {content_length} words.
    Write the article in {language}.
    Use HTML tags for structure, but do not include any CSS or JavaScript.

    Article Content:
    """
    
    prompt = PromptTemplate(
        input_variables=["keyword", "content_length", "language"],
        template=prompt_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    article_content = chain.run(keyword=keyword, content_length=content_length, language=language)
    return article_content

def generate_html5_page(keyword, article_content, language):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="{language.lower()[:2]}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{keyword} - AI Article</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                margin-top: 30px;
            }}
            h3 {{
                color: #27ae60;
            }}
            p {{
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <h1>{keyword}</h1>
        {article_content}
    </body>
    </html>
    """
    return html_template

def main():
    load_dotenv()
    st.set_page_config(page_title="AI HTML5 Article Generator", page_icon="@")

    st.header("AI HTML5 Article Generator")

    # File uploader for multiple PDFs
    uploaded_files = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)

    # User input for keyword
    user_keyword = st.text_input("Enter a keyword for the article:")

    # Content length selection
    content_length = st.selectbox("Select content length:", [800])

    # Language selection
    languages = ["English"]
    selected_language = st.selectbox("Select the language for the article:", languages)

    # Process PDFs and generate HTML5 article
    if uploaded_files and user_keyword:
        if st.button("Generate HTML5 Article"):
            with st.spinner("Processing PDFs and generating HTML5 article..."):
                raw_text = fetch_pdf_content(uploaded_files)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                
                article_content = generate_article_content(user_keyword, vectorstore, content_length, selected_language)
                html5_page = generate_html5_page(user_keyword, article_content, selected_language)
                
                st.subheader(f"Generated HTML5 Article: {user_keyword}")
                st.code(html5_page, language='html')
                
                # Option to download the HTML5 file
                st.download_button(
                    label="Download HTML5 Article",
                    data=html5_page,
                    file_name=f"{user_keyword.replace(' ', '_')}_article.html",
                    mime="text/html"
                )

if __name__ == '__main__':
    main()