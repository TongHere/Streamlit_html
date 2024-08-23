def generate_article_content(keyword, content_length, language, search_intent):
    # raise Exception('Upps, article content failed to be generated in generate_article_content')

    # dummy text
    # simulating chatgpt's API response
    article_content = f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor read {search_intent} sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
    article_content += f'<h2>heading for keyword {keyword}</h2>'
    article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor read {search_intent} sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'
    article_content += f'<h2>heading for keyword {keyword}</h2>'
    article_content += f'<p>dummy text for keyword {keyword} in language {language} text in bLorem ipsum dolor read {search_intent} sit amet consectetur adipisicing elit. Accusantium, libero omnis perspiciatis animi at similique tempora mollitia in rem soluta.</p>'

    return article_content