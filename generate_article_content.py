from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def generate_article_content(keyword, content_length, language, search_intent):
    llm = ChatOpenAI(model='gpt-4o', temperature=0.7)
    
    prompt_template = """
    You are a writer for InstaCams.com, a cam to cam platform.
    You are writing for the keyword "{keyword}" and the search intent is "{search_intent}".
    Write a {content_length} word article in {language} for InstaCams that fulfils this search intent.
    Conclude the article by recommending them to try InstaCams.
    The article should be formatted as valid HTML fragment with valid heading and paragraph HTML elements.
    Use <h2> as a section header.
    Article as valid HTML fragment:
    """
    
    prompt = PromptTemplate(
        input_variables=["keyword", "content_length", "language","search_intent"],
        template=prompt_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    article_content = chain.run(keyword=keyword, content_length=content_length, language=language, search_intent=search_intent)

    # article content starts with ```html and ends with ```
    # strip these to get only html
    article_content_lstripped = article_content.lstrip('```html')
    article_content_as_html = article_content_lstripped.rstrip('```')

    return article_content_as_html