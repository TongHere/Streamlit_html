# AI HTML5 and JSON Generator

## Toggle article generation fake mode

In order to use fake data when developping, set `USE_FAKE_ARTICLE_CONTENT` to `True` in `.env`

```
USE_FAKE_ARTICLE_CONTENT="True"
```

This uses `generate_article_content_fake.py`

Any other value (including not setting the variable, or setting it to `USE_FAKE_ARTICLE_CONTENT=...`) sets the env value to false, using OpenAI data (and credits), using `generate_article_content.py`

# RAG AI Chatbot

The AI Chatbot is an advanced conversational agent specifically designed to assist users by extracting and utilizing information from PDF documents. By employing cutting-edge Natural Language Processing (NLP) technologies, this chatbot is capable of processing text from PDFs, generating embeddings for efficient retrieval, and engaging in meaningful dialogue based on the extracted content.

## Features

- PDF Text Extraction: Extract text from one or multiple PDF files.

- Text Chunking: Break down large text data into manageable chunks.

- Embedding Generation: Convert text chunks into embeddings using OpenAI's models.

- Vector Storage: Store and manage embeddings with FAISS for efficient retrieval.

- Conversational AI: Utilize a conversational retrieval chain powered by GPT-4 for dynamic and contextual chat interactions.

## Installation

```bash
python -m venv venv
source venv/bin/activate
```

Install the required Python packages.

```bash
pip install -r requirements.txt
```

Environment Variables

```bash
OPENAI_API_KEY= ...
HUGGINGFACEHUB_API_TOKEN= ...
LANGCHAIN_TRACING_V2= ...
LANGCHAIN_ENDPOINT= ...
LANGCHAIN_API_KEY= ...
LANGCHAIN_PROJECT= ...
```

Running the Application

```bash
python3 main.py
```

## Usage

After launching the application, the web interface provided by Streamlit will guide you through the process:

- Web Scrapping : Extract data from the web and store it in PDF files for the chatbot to process.
- Enter Queries: Once the PDFs are processed, enter your questions in the text input box to engage with the chatbot.
- Review Responses: The chatbot utilizes the processed PDF content to provide answers and engage in a meaningful conversation about the document contents.
