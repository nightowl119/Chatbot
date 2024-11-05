import requests
from bs4 import BeautifulSoup
import os

# Specify the folder path where you want to save the file
folder_path = 'D:/Smac-x/backend'  # Change this to your desired path

# Create the folder if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

# List of URLs to scrape
urls = [
    'https://en.wikipedia.org/wiki/World_War_II'
]

# Open a file to save the scraped data in the specified folder
file_path = os.path.join(folder_path, "para.txt")
with open(file_path, "w", encoding="utf-8") as file:
    for url in urls:
        # Send request to the URL
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            file.write(f"Data from {url}:\n")
            file.write("="*50 + "\n")
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all paragraphs (or other elements)
            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                file.write(paragraph.get_text() + "\n")
            file.write("\n" + "="*50 + "\n\n")
        else:
            file.write(f"Failed to retrieve {url}\n")
            file.write("="*50 + "\n\n")

print("Data has been successfully saved to 'para.txt'")
