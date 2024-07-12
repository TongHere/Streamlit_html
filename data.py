from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_html(url):
    """
    Sends a GET request to the specified URL and returns the HTML content of the page.
    Parameters:
    - url (str): The URL of the webpage to retrieve.
    Returns:
    - str: The HTML content of the webpage as text.
    """
    response = requests.get(url)
    return response.text

def extract_links(base_url, html):
    """
    Parses the given HTML content to extract all links with a specific class attribute and constructs absolute URLs.
    Parameters:
    - base_url (str): The base URL used to resolve relative links.
    - html (str): The HTML content from which links are to be extracted.
    Returns:
    - list of tuples: A list of tuples where each tuple contains the text and the absolute URL of a link.
    Raises:
    - Exception: If the HTML content could not be parsed.
    """
    if not html:
        print("Invalid HTML content provided for parsing.")
        return []
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []
    links = soup.find_all('a', class_='article-list__item')
    return [(link.text.strip(), urljoin(base_url, link['href'])) for link in links if link.text and link.has_attr('href')]

def extract_content(html):
    """
    Extracts and returns the main content from a given HTML string, targeting a specific div class.
    Parameters:
    - html (str): HTML content from which to extract the main content.
    Returns:
    - str: The extracted content text, stripped of leading and trailing spaces.
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='article-blog__content').text
    return content.strip() 

def create_pdf(title_content_pairs):
    """
    Creates a PDF document with the provided title and content pairs.
    Parameters:
    - title_content_pairs (list of tuples): A list where each tuple contains a title and its corresponding content.
    Side effects:
    - Writes a PDF file named 'blog_content.pdf' to the current working directory.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    counter = 1 

    for title, content in title_content_pairs:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12) 
        cell_width = 190
        title_with_number = f"{counter}. Title: {title}"
        pdf.multi_cell(cell_width, 10, title_with_number.encode('latin-1', 'replace').decode('latin-1'))
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(cell_width, 10, "Content: " + content.encode('latin-1', 'replace').decode('latin-1'))
        counter += 1

    pdf.output("blog_content.pdf")

def main():
    """
    Main function to orchestrate the scraping, processing, and PDF creation tasks.
    Starts by fetching the HTML from a given starting URL, extracts links, fetches content for each link,
    and then generates a PDF containing the content of each link.
    """
    start_url = 'N/A'
    main_page_html = get_html(start_url)
    blog_links = extract_links(start_url, main_page_html)
    title_content_pairs = []

    for title, url in blog_links:
        print(f"Fetching content for: {title}")
        blog_html = get_html(url)
        content = extract_content(blog_html)
        title_content_pairs.append((title, content))
    
    create_pdf(title_content_pairs)

if __name__ == '__main__':
    main()
