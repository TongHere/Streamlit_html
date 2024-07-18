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
import tempfile
import re

load_dotenv()

def upload_and_process_keywords_file(uploaded_file):
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        keywords = [line.strip() for line in content.split('\n') if line.strip()]
        return keywords, None
    except Exception as e:
        return None, f"Error processing the keywords file: {str(e)}"

def fetch_pdf_content(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(pdf.read())
                temp_file_path = temp_file.name

            pdf_reader = PdfReader(temp_file_path)
            for page in pdf_reader.pages:
                text += page.extract_text()

            os.unlink(temp_file_path)
        except Exception as e:
            st.error(f"Error processing PDF: {pdf.name}. Error: {str(e)}")
    return text

def clean_text(text):
    # Remove any non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove 'dataLayer' references
    text = re.sub(r'\bdataLayer\b', '', text)
    return text.strip()

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
    Based on the information from the uploaded documents and focusing on the keyword "{keyword}",
    write a comprehensive article that covers the following aspects:

    1. Introduction to {keyword}
    2. Key points and best practices related to {keyword}
    3. Common challenges and how to overcome them in the context of {keyword}
    4. Future trends or predictions in the area of {keyword}
    5. Conclusion with actionable advice about {keyword}

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
    
    try:
        article_content = chain.run(keyword=keyword, content_length=content_length, language=language)
        return article_content
    except Exception as e:
        st.error(f"Error generating article for keyword '{keyword}': {str(e)}")
        return None

def generate_html5_page(keyword, article_content, language, html_template):
    return html_template.format(
        language=language.lower()[:2],
        keyword=keyword,
        article_content=article_content
    )

def main():
    load_dotenv()
    st.set_page_config(page_title="AI HTML5 Article Generator", page_icon="📄")

    st.header("AI HTML5 Article Generator")

    uploaded_files = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)
    keyword_file = st.file_uploader("Upload your keywords file (txt)", type="txt")
    html_template_file = st.file_uploader("Upload HTML template", type="html")

    languages = ["English", "Spanish", "French", "German", "Italian"]
    selected_language = st.selectbox("Select the language for the articles:", languages)

    content_length = 800

    if uploaded_files and keyword_file and html_template_file:
        if st.button("Generate HTML5 Articles"):
            with st.spinner("Processing PDFs and generating HTML5 articles..."):
                try:
                    keywords, error_message = upload_and_process_keywords_file(keyword_file)
                    if error_message:
                        st.error(error_message)
                        return

                    html_template = html_template_file.getvalue().decode()

                    raw_text = fetch_pdf_content(uploaded_files)
                    if not raw_text:
                        st.error("No text could be extracted from the uploaded PDFs. Please check the files and try again.")
                        return

                    cleaned_text = clean_text(raw_text)
                    st.text("Sample of cleaned text:")
                    st.code(cleaned_text[:500])  # Display first 500 characters of cleaned text

                    text_chunks = get_text_chunks(cleaned_text)
                    vectorstore = get_vectorstore(text_chunks)

                    st.write(f"Generating articles for keywords: {', '.join(keywords)}")

                    for keyword in keywords:
                        article_content = generate_article_content(keyword, vectorstore, content_length, selected_language)
                        if article_content:
                            html5_page = generate_html5_page(keyword, article_content, selected_language, html_template)
                            
                            st.subheader(f"Generated HTML5 Article: {keyword}")
                            st.code(html5_page, language='html')
                            
                            st.download_button(
                                label=f"Download HTML5 Article for '{keyword}'",
                                data=html5_page,
                                file_name=f"{keyword.replace(' ', '_')}_article.html",
                                mime="text/html"
                            )
                    
                    st.success("All articles have been generated successfully!")
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
                    st.error("Please check your input files and try again.")

if __name__ == '__main__':
    main()