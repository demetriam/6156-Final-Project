import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def describe_image(image_url):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image for someone who is visually impaired."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=100
    )
    return response.choices[0].message.content

def process_webpage(url):
    print(f"Loading page: {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    images = soup.find_all('img')
    print(f"Found {len(images)} images")

    for img in images:
        if not img.get('alt'):
            src = img.get('src')
            if not src.startswith('http'):
                src = requests.compat.urljoin(url, src)
            print(f"\nImage URL: {src}")
            try:
                description = describe_image(src)
                print(f"Generated Alt Text: {description}")
            except Exception as e:
                print(f"Failed to describe image: {e}")


process_webpage("https://www.mta.info")