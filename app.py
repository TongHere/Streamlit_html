from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import zipfile
import io
import re
import time

load_dotenv()

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
                    print(f"Read: Keyword='{keyword}', search_intent='{search_intent}'")
                    if keyword and search_intent:  # Ensure neither is empty
                        keywords_and_values.append((keyword, search_intent))
                        print(f"Added: ({keyword}, {search_intent})")
                    else:
                        print("Skipped: Empty keyword or search_intent")
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

def generate_article_content(keyword, content_length, language):
    # raise Exception('Upps, article content failed to be generated in generate_article_content')
    # dummy text
    # simulating chatgpt's API response
    article_content = f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
    article_content += f'<h2>heading for keyword {keyword}</h2>'
    article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
    article_content += f'<h2>heading for keyword {keyword}</h2>'
    article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'

    return article_content
    # llm = ChatOpenAI(model='gpt-4o', temperature=0.7)
    
    # prompt_template = """
    # You are a writer for InstaCams.com, a cam to cam platform.
    # You are writing for the keyword "{keyword}" and the search intent is "User is looking for alternatives to {keyword}".
    # Write a {content_length} word article in {language} for InstaCams that fulfils this search intent.
    # Conclude the article by recommending them to try InstaCams.
    # The article should be formatted as valid HTML fragment with valid heading and paragraph HTML elements.
    # Use <h2> as a section header.
    # Article as valid HTML fragment:
    # """
    
    # prompt = PromptTemplate(
    #     input_variables=["keyword", "content_length", "language"],
    #     template=prompt_template
    # )
    
    # chain = LLMChain(llm=llm, prompt=prompt)
    
    # article_content = chain.run(keyword=keyword, content_length=content_length, language=language)

    # article content starts with ```html and ends with ```
    # strip these to get only html
    # article_content_lstripped = article_content.lstrip('```html')
    # article_content_as_html = article_content_lstripped.rstrip('```')

    # return article_content_as_html

def get_relative_path(keyword):
    keyword_lower_case = keyword.lower()
    keyword_with_hyphens_only = re.sub('[^0-9a-z]+', '-', keyword_lower_case)
    keyword_with_single_hyphens = re.sub('-+', '-', keyword_with_hyphens_only)
    keyword_without_trailing_leading_hyphens = keyword_with_single_hyphens.strip('-')

    return keyword_without_trailing_leading_hyphens

def main():
    load_dotenv()
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

    languages = ["English", "Spanish", "French", "German", "Italian"]
    selected_language = st.selectbox("Select the language for the articles:", languages)
    content_length = st.number_input("Enter the desired word count for each article:", min_value=100, max_value=2000, value=800)

    if keyword_file:
        if st.button("Generate HTML5 and JSON Files"):
            keywords_and_values = upload_and_process_keywords_file(keyword_file)

            if keywords_and_values:
                st.write(f"Keywords and search intent found:")
                for keyword, search_intent in keywords_and_values:
                    st.write(f"- Keyword: '{keyword}', search_intent: '{search_intent}'")
                
                progress_bar = st.progress(0)
                status_text = st.empty()

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for i, (keyword, search_intent) in enumerate(keywords_and_values):
                        status_text.text(f"Generating content for: {keyword}")

                        keyword_capitalized = keyword.title()
                        relative_path = get_relative_path(keyword)

                        try:
                            article_content = generate_article_content(keyword, content_length, selected_language)

                            html_contents = html_template.render(
                                article_content=article_content,
                                keyword_capitalized=keyword_capitalized,
                                search_intent=search_intent  # You can use this search_intent in your template if needed
                            )

                            html_filename = f"{relative_path}.html"
                            zip_file.writestr(html_filename, html_contents)
                            status_text.text(f"{html_filename} created, added to zip")

                            json_contents = json_template.render(
                                keyword_capitalized=keyword_capitalized,
                                relative_path=relative_path,
                                search_intent=search_intent  # You can use this search_intent in your JSON template if needed
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