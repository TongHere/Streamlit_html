import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re

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
        llm = ChatOpenAI(model='gpt-4')
        
        prompt_template = """
        Write a comprehensive article about the keyword "{keyword}". 
        The article should cover the following aspects:

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
        
        article_content = chain.run(keyword=keyword, content_length=content_length, language=language)
        return article_content
    except Exception as e:
        st.error(f"Error generating article for keyword '{keyword}': {str(e)}")
        return None

def generate_html5_page(keyword, article_content, html_template):
    try:
        # Update meta title
        title_pattern = r'<title>.*?</title>'
        new_title = f'<title>{keyword}</title>'
        if re.search(title_pattern, html_template):
            html_template = re.sub(title_pattern, new_title, html_template)
        else:
            head_end = html_template.find('</head>')
            if head_end != -1:
                html_template = html_template[:head_end] + new_title + html_template[head_end:]
            else:
                st.warning("Could not find </head> tag. Title may not be updated.")

        # Insert article content
        content_section_start = html_template.find('<section class="content-section">')
        content_section_end = html_template.find('</section>', content_section_start)
        
        if content_section_start != -1 and content_section_end != -1:
            before_content = html_template[:content_section_start + len('<section class="content-section">')]
            after_content = html_template[content_section_end:]
            
            new_content = f"""
            <h1>{keyword}</h1>
            {article_content}
            """
            
            return before_content + new_content + after_content
        else:
            st.error("Could not find the content section in the HTML template.")
            return None
    except Exception as e:
        st.error(f"Error generating HTML page: {str(e)}")
        return None

def main():
    load_dotenv()
    st.set_page_config(page_title="AI HTML5 Article Generator", page_icon="📄")

    st.header("AI HTML5 Article Generator")

    keyword_file = st.file_uploader("Upload your keywords file (txt)", type="txt")
    html_template_file = st.file_uploader("Upload your HTML template file", type="html")

    languages = ["English", "Spanish", "French", "German", "Italian"]
    selected_language = st.selectbox("Select the language for the articles:", languages)

    content_length = st.number_input("Enter the desired word count for each article:", min_value=100, max_value=2000, value=800)

    if keyword_file and html_template_file:
        if st.button("Generate HTML5 Articles"):
            keywords = upload_and_process_keywords_file(keyword_file)
            html_template = html_template_file.getvalue().decode('utf-8')
            
            if keywords and html_template:
                st.write(f"Keywords found: {', '.join(keywords)}")
                with st.spinner("Generating HTML5 articles..."):
                    for keyword in keywords:
                        st.write(f"Generating article for: {keyword}")
                        article_content = generate_article_content(keyword, content_length, selected_language)
                        if article_content:
                            html5_page = generate_html5_page(keyword, article_content, html_template)
                            
                            if html5_page:
                                st.subheader(f"Generated HTML5 Article: {keyword}")
                                st.code(html5_page, language='html')
                                
                                st.download_button(
                                    label=f"Download HTML5 Article for '{keyword}'",
                                    data=html5_page,
                                    file_name=f"{keyword.replace(' ', '_')}_article.html",
                                    mime="text/html"
                                )
                    
                    st.success("All articles have been generated successfully!")
            else:
                st.error("Failed to process input files. Please check your keyword file and HTML template and try again.")

if __name__ == '__main__':
    main()