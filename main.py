import subprocess

def run_scripts():
    # Run the web scraping script to generate the PDF
    print("Running data.py to scrape data and generate PDF...")
    subprocess.run(['python', 'data.py'], check=True)

    # Run the Streamlit app which processes and interacts with the PDF
    print("Running app.py to start the Streamlit application...")
    subprocess.run(['streamlit', 'run', 'app.py'], check=True)

if __name__ == "__main__":
    run_scripts()
