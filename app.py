import json
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
import zipfile
import io
import re
import time
import os

load_dotenv()

if (os.getenv('USE_FAKE_ARTICLE_CONTENT', 'False').lower() == 'True'):
    print("\nUsing fake article content generation (NOT OpenAI)\n")
    from generate_article_content_fake import generate_article_content 
else:
    print("\nUsing real article content generation: OpenAI\n")
    from generate_article_content import generate_article_content 

import csv
import io

def upload_and_process_keywords_file(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read the content of the uploaded file
            content = uploaded_file.getvalue().decode('utf-8')
            
            print("File content:")
            print(content)
            print("\nProcessing CSV rows:")
            
            # Create a CSV reader object
            csv_reader = csv.reader(io.StringIO(content))
            
            # Initialize a list to store the keywords and values
            keywords_and_values = []
            
            # Read the first and second columns
            for row in csv_reader:
                if len(row) >= 2:
                    keyword = row[0].strip()
                    search_intent = row[1].strip()
                    footer_title = row[2].strip()
                    print(f"Read: Keyword='{keyword}', search_intent='{search_intent}', footer_title='{footer_title}'")
                    if keyword and search_intent and footer_title:  # Ensure neither is empty
                        keywords_and_values.append((keyword, search_intent, footer_title))
                        print(f"Added: ({keyword}, {search_intent}, {footer_title})")
                    else:
                        print("Skipped: Empty keyword or search_intent or footer title")
                else:
                    print(f"Skipped: Insufficient columns in row {row}")
            
            print("\nFinal processed list:")
            for item in keywords_and_values:
                print(item)
            
            return keywords_and_values
        except Exception as e:
            print(f"Error processing the CSV file: {str(e)}")
            return None
    else:
        print("No CSV file was uploaded.")
        return None

def get_relative_path(keyword):
    keyword_lower_case = keyword.lower()
    keyword_with_hyphens_only = re.sub('[^0-9a-z]+', '-', keyword_lower_case)
    keyword_with_single_hyphens = re.sub('-+', '-', keyword_with_hyphens_only)
    keyword_without_trailing_leading_hyphens = keyword_with_single_hyphens.strip('-')

    return keyword_without_trailing_leading_hyphens

def get_footer_title_for_json_template(footer_title):
    footer_title_stripped = footer_title.strip()
    footer_title_escaped = json.dumps(footer_title_stripped).strip('"')

    return footer_title_escaped

def main():
    st.set_page_config(page_title="AI HTML5 and JSON Generator", page_icon="📄")
    st.header("AI HTML5 and JSON Generator")
    
    keyword_file = st.file_uploader("Upload your keywords file (CSV)", type="csv")
    
    # Load templates
    templates_directory = Path().absolute() / "templates"
    jinja_env = Environment(
        loader=FileSystemLoader(templates_directory),
        autoescape=select_autoescape(),
        extensions=["jinja2_time.TimeExtension"],
    )
    html_template = jinja_env.get_template("instacams-seo-subpage.html")
    json_template = jinja_env.get_template("instacams-seo-subpage.html.json")

    languages = {
        "English": {
            "lang": "x-default",
            "href_country_path": ""
            }, 
        "Spanish": {
            "lang": "es",
            "href_country_path": "es/"
            }, 
        "French": {
            "lang": "fr",
            "href_country_path": "fr/"
            }, 
        "German": {
            "lang": "de",
            "href_country_path": "de/"
            }, 
        "Italian": {
            "lang": "it",
            "href_country_path": "it/"
            }, 
        "Suomi": {
            "lang": "fi",
            "href_country_path": "fi/"
            }, 
        "Japanese": {
            "lang": "ja",
            "href_country_path": "ja/"
            }, 
        "Korean": {
            "lang": "ko",
            "href_country_path": "ko/"
            }, 
        "Dutch": {
            "lang": "nl",
            "href_country_path": "nl/"
            }, 
        "Norsk": {
            "lang": "no",
            "href_country_path": "no/"
            }, 
        "Portuguese": {
            "lang": "pt",
            "href_country_path": "pt/"
            }, 
        "Romanian": {
            "lang": "ro",
            "href_country_path": "ro/"
            }, 
        "Russian": {
            "lang": "ru",
            "href_country_path": "ru/"
            }, 
        "Swedish": {
            "lang": "sv",
            "href_country_path": "sv/"
            }, 
        }
    selected_language = st.selectbox("Select the language for the articles:", languages)
    hreflang_language_config = languages.get(selected_language, languages["English"])

    content_length = st.number_input("Enter the desired word count for each article:", min_value=100, max_value=2000, value=800)

    if keyword_file:
        if st.button("Generate HTML5 and JSON Files"):
            keywords_and_values = upload_and_process_keywords_file(keyword_file)

            if keywords_and_values:
                st.write(f"Keywords and search intent found:")
                for keyword, search_intent, footer_title in keywords_and_values:
                    st.write(f"- Keyword: '{keyword}', search_intent: '{search_intent}', footer_title: '{footer_title}'")
                
                progress_bar = st.progress(0)
                status_text = st.empty()

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for i, (keyword, search_intent, footer_title) in enumerate(keywords_and_values):
                        status_text.text(f"Generating content for: {keyword}")

                        keyword_capitalized = keyword.title()
                        relative_path = get_relative_path(keyword)

                        try:
                            article_content = generate_article_content(keyword, content_length, selected_language, search_intent)

                            html_contents = html_template.render(
                                article_content=article_content,
                                keyword_capitalized=keyword_capitalized,
                                search_intent=search_intent
                            )

                            html_filename = f"{relative_path}.html"
                            zip_file.writestr(html_filename, html_contents)
                            status_text.text(f"{html_filename} created, added to zip")

                            footer_title_for_template = get_footer_title_for_json_template(footer_title)

                            json_contents = json_template.render(
                                keyword_capitalized=keyword_capitalized,
                                relative_path=relative_path,
                                search_intent=search_intent,
                                footer_title=footer_title_for_template,
                                lang=hreflang_language_config["lang"],
                                href_country_path=hreflang_language_config["href_country_path"],
                            )

                            json_filename = f"{relative_path}.html.json"
                            zip_file.writestr(json_filename, json_contents)
                            status_text.text(f"{json_filename} created, added to zip")

                        except Exception as exception:
                            st.error(f"Error generating content for keyword '{keyword}': {str(exception)}")

                        progress_bar.progress((i + 1) / len(keywords_and_values))
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
                st.error("Failed to process input files. Please check your CSV file and try again.")

if __name__ == '__main__':
    main()
