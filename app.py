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
        
        prompt_template = """
        Give a friendly intro to {keyword}. What's it all about? Why should we care?
        Structure the article like this:

        1. Introduction to {keyword}
        2. Break down the important stuff about {keyword}. What should people know?
        3. Share some awesome tips and tricks for mastering {keyword}.</p>
        4. Future trends or predictions in the area of {keyword}
        5. Sum it all up and give some easy-to-follow advice on{keyword}
        
        Keep it fun, friendly, and easy to read. Aim for about {content_length} words.
        Write in {language}, and remember - we're chatting with friends here, not giving a lecture!
        Stick to the HTML structure above.

        Article Content:
        """
        main
        
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

def get_relative_path(keyword):
    return keyword.lower().replace(' ', '-')

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
    html_template = jinja_env.get_template("instacams-seo-subpage.html")
    json_template = jinja_env.get_template("instacams-seo-subpage.html.json")

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
                            html_contents = html_template.render(article_content=article_content, keyword=keyword)

                            relative_path = get_relative_path(keyword)
                            json_contents = json_template.render(keyword=keyword, relative_path=relative_path)

                            if html_contents:
                                # Add HTML file to zip
                                html_filename = f"{keyword.replace(' ', '_')}.html"
                                zip_file.writestr(html_filename, html_contents)
                                
                                # Add JSON file to zip
                                json_filename = f"{keyword.replace(' ', '_')}.json"
                                zip_file.writestr(json_filename, json.dumps(json_contents, indent=2))

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