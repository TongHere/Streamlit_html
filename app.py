import os
import json
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

def generate_article_content(keyword, vectorstore, content_length, language, template_json):
    llm = ChatOpenAI(model='gpt-4')
    
    prompt_template = template_json['prompt_template']
    
    prompt = PromptTemplate(
        input_variables=["keyword", "content_length", "language"],
        template=prompt_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    article_content = chain.run(keyword=keyword, content_length=content_length, language=language)
    return article_content

def generate_html5_page(keyword, article_content, language, template_html):
    return template_html.format(
        language=language.lower()[:2],
        keyword=keyword,
        article_content=article_content
    )

def main():
    load_dotenv()
    st.set_page_config(page_title="AI HTML5 Article Generator", page_icon="@")

    st.header("AI HTML5 Article Generator")

    # File uploader for multiple PDFs
    uploaded_files = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)

    # File uploader for keywords
    keywords_file = st.file_uploader("Upload a file with keywords (one per line)", type="txt")

    # HTML template uploader
    html_template_file = st.file_uploader("Upload HTML template", type="html")

    # JSON template uploader
    json_template_file = st.file_uploader("Upload JSON template", type="json")

    # Content length (fixed to 800)
    content_length = 800

    # Language selection (excluding English)
    languages = ["Spanish", "French", "German", "Italian"]
    selected_language = st.selectbox("Select the language for the article:", languages)

    # Process PDFs and generate HTML5 article
    if uploaded_files and keywords_file and html_template_file and json_template_file:
        if st.button("Generate HTML5 Articles"):
            with st.spinner("Processing PDFs and generating HTML5 articles..."):
                # Read keywords
                keywords = keywords_file.getvalue().decode().splitlines()

                # Read templates
                html_template = html_template_file.getvalue().decode()
                json_template = json.load(json_template_file)

                # Process PDFs
                raw_text = fetch_pdf_content(uploaded_files)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)

                # Generate articles for each keyword
                for keyword in keywords:
                    article_content = generate_article_content(keyword, vectorstore, content_length, selected_language, json_template)
                    html5_page = generate_html5_page(keyword, article_content, selected_language, html_template)
                    
                    st.subheader(f"Generated HTML5 Article: {keyword}")
                    st.code(html5_page, language='html')
                    
                    # Option to download the HTML5 file
                    st.download_button(
                        label=f"Download HTML5 Article for '{keyword}'",
                        data=html5_page,
                        file_name=f"{keyword.replace(' ', '_')}_article.html",
                        mime="text/html"
                    )

if __name__ == '__main__':
    main()