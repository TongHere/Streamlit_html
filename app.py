import os
import json
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re
import zipfile
import io
import time

load_dotenv()

def upload_and_process_keywords_file(uploaded_file):
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            keywords = [line.strip() for line in content.split('\n') if line.strip()]
            return keywords
        except Exception as e:
            st.error(f"Error processing the keywords file: {str(e)}")
            return None
    else:
        st.error("No keyword file was uploaded.")
        return None

def generate_article_content(keyword, content_length, language):
    try:
        # dummy text
        # simulating chatgpt's API response
        article_content = f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
        article_content += f'<h2>heading for keyword {keyword}</h2>'
        article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
        article_content += f'<h2>heading for keyword {keyword}</h2>'
        article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'

        return article_content
        # llm = ChatOpenAI(model='gpt-4', temperature=0.7)
        
        # prompt_template = """
        # Write a comprehensive article about the keyword "{keyword}". 
        # The article should cover the following aspects:

        # 1. Introduction to {keyword}
        # 2. Key points and best practices related to {keyword}
        # 3. Common challenges and how to overcome them in the context of {keyword}
        # 4. Future trends or predictions in the area of {keyword}
        # 5. Conclusion with actionable advice about {keyword}

        # Use a professional tone and structure the article with clear headings (h2) and subheadings (h3).
        # Wrap each paragraph in <p> tags.
        # Aim for an article length of about {content_length} words.
        # Write the article in {language}.
        # Use HTML tags for structure, but do not include any CSS or JavaScript.

        # Article Content:
        # """
        
        # prompt = PromptTemplate(
        #     input_variables=["keyword", "content_length", "language"],
        #     template=prompt_template
        # )
        
        # chain = LLMChain(llm=llm, prompt=prompt)
        
        # article_content = chain.run(keyword=keyword, content_length=content_length, language=language)
        # return article_content
    except Exception as e:
        st.error(f"Error generating article for keyword '{keyword}': {str(e)}")
        return None

def generate_json_metadata(keyword):
    return {
        "title": f"{keyword} - Video Chat Alternative - InstaCams",
        "description": f"With {keyword}, enjoy a cam-to-cam chat with strangers. Meet random people worldwide looking for an entertaining {keyword} alternative site.",
        "canonical": f"https://www.instacams.com/{keyword.lower().replace(' ', '-')}",
        "hreflang": [
            {
                "lang": "x-default",
                "href": f"https://www.instacams.com/{keyword.lower().replace(' ', '-')}"
            },
            {
                "lang": "de",
                "href": f"https://www.instacams.com/de/{keyword.lower().replace(' ', '-')}"
            },
            {
                "lang": "es",
                "href": f"https://www.instacams.com/es/{keyword.lower().replace(' ', '-')}"
            },
            {
                "lang": "fr",
                "href": f"https://www.instacams.com/fr/{keyword.lower().replace(' ', '-')}"
            }
        ]
    }

def main():
    load_dotenv()
    st.set_page_config(page_title="AI HTML5 and JSON Generator", page_icon="📄")

    st.header("AI HTML5 and JSON Generator")

    keyword_file = st.file_uploader("Upload your keywords file (txt)", type="txt")

    # load template
    templates_directory = Path().absolute() / "templates"
    jinja_env = Environment(
        loader=FileSystemLoader(templates_directory),
        autoescape=select_autoescape(),
        extensions=["jinja2_time.TimeExtension"],
    )
    template = jinja_env.get_template("instacams.html.jinja")

    languages = ["English", "Spanish", "French", "German", "Italian"]
    selected_language = st.selectbox("Select the language for the articles:", languages)

    content_length = st.number_input("Enter the desired word count for each article:", min_value=100, max_value=2000, value=800)

    if keyword_file:
        if st.button("Generate HTML5 and JSON Files"):
            keywords = upload_and_process_keywords_file(keyword_file)
            
            if keywords:
                st.write(f"Keywords found: {', '.join(keywords)}")
                progress_bar = st.progress(0)
                status_text = st.empty()

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for i, keyword in enumerate(keywords):
                        status_text.text(f"Generating content for: {keyword}")
                        article_content = generate_article_content(keyword, content_length, selected_language)
                        if article_content:
                            html5_page = template.render(article_content=article_content, keyword=keyword)

                            json_metadata = generate_json_metadata(keyword)
                            
                            if html5_page:
                                # Add HTML file to zip
                                html_filename = f"{keyword.replace(' ', '_')}.html"
                                zip_file.writestr(html_filename, html5_page)
                                
                                # Add JSON file to zip
                                json_filename = f"{keyword.replace(' ', '_')}.json"
                                zip_file.writestr(json_filename, json.dumps(json_metadata, indent=2))

                        progress_bar.progress((i + 1) / len(keywords))
                        time.sleep(0.1)  # To prevent potential rate limiting

                status_text.text("All files generated successfully!")
                
                # Offer the zip file for download
                zip_buffer.seek(0)
                st.download_button(
                    label="Download All Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="generated_files.zip",
                    mime="application/zip"
                )
            else:
                st.error("Failed to process input files. Please check your keyword file and HTML template and try again.")

if __name__ == '__main__':
    main()