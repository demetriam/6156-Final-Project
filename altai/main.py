import os
import requests
import base64
import json
from bs4 import BeautifulSoup
from io import BytesIO
import csv
from openai import OpenAI
from dotenv import load_dotenv
from google.generativeai import configure, GenerativeModel

PROMPT1 = "Describe the image with a red border to someone who is blind. The description will be read aloud by a screen reader, so keep the description to 1-2 sentences and follow best practices for alt text. Convey the most important visual details that are relevant in the context of the webpage this image is a part of, but don’t overwhelm the user with unnecessary information. Consider why this image is included instead of describing every little detail. No need to say 'image of' or 'picture of', but do say if it's a logo, illustration, or diagram."
PROMPT2 = "Describe the image with a red border to someone who is blind. This screenshot includes a visual element (ex: product banner, photo, text etc.) generate appropriate alt text for that visual element only ignoring the surrounding webpage layout or article structure. Keep the description concise and relevant to the image content and purpose."

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
configure(api_key=os.getenv("GEMINI_API_KEY"))

def describe_image_gpt4(image_url):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image for someone who is visually impaired"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=100
    )
    return response.choices[0].message.content

def describe_image_gemini(image_url):
    model = GenerativeModel("gemini-pro-vision")
    response = model.generate_content([
        "Describe this image for someone who is visually impaired.",
        {
            "image_url": image_url
        }
    ])
    return response.text
  

def process_screenshot(image_path, model="openai"):
    try:
        if model == "openai":
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image to someone who is blind. The description will be read aloud by a screen reader, so keep the description to 1-2 sentences and follow best practices for alt text. Convey the most important visual details that are relevant in the context of the webpage this image is a part of (<URL>), but don’t overwhelm the user with unnecessary information. Consider why this image is included instead of describing every little detail. The HTML metadata description of the webpage is <DESCRIPTION>."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=500
            )
            print("\nGenerated Alt Text (GPT-4o):")
            print(response.choices[0].message.content)
        elif model == "gemini":
            model = GenerativeModel("gemini-1.5-flash")
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            response = model.generate_content([
                "Describe this image to someone who is blind. The description will be read aloud by a screen reader, so keep the description to 1-2 sentences and follow best practices for alt text. Convey the most important visual details that are relevant in the context of the webpage this image is a part of (<URL>), but don’t overwhelm the user with unnecessary information. Consider why this image is included instead of describing every little detail. The HTML metadata description of the webpage is <DESCRIPTION>",
                {
                    "mime_type": "image/png",
                    "data": image_data
                }
            ])
            print("\nGenerated Alt Text (Gemini):")
            print(response.text)
        else:
            raise ValueError("Unknown model specified.")
    except Exception as e:
        print(f"Failed to process screenshot: {e}")

def batch_process_screenshots(folder_path, output_file="alttext_results.csv"):
    with open(output_file, mode="w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Image", "Model", "Generated Alt Text"]) 
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")) and "highlight" in filename:
                image_path = os.path.join(folder_path, filename)
                print(f"processing: {filename}")
                for model in ["openai", "gemini", "llama"]:
                    for PROMPT in [PROMPT1, PROMPT2]:   
                        print(f"model: {model.capitalize()}")
                        try:
                            if model == "openai":
                                with open(image_path, "rb") as image_file:
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                                response = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": [
                                                {"type": "text", "text": PROMPT},
                                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                                            ]
                                        }
                                    ],
                                    max_tokens=500
                                )
                                alt_text = response.choices[0].message.content
                                print("\ngenerated Alt Text (GPT-4o):")
                                print(alt_text)
                            elif model == "gemini":
                                model_instance = GenerativeModel("gemini-1.5-flash")
                                with open(image_path, "rb") as f:
                                    image_data = base64.b64encode(f.read()).decode("utf-8")
                                response = model_instance.generate_content([
                                    PROMPT,
                                    {
                                        "mime_type": "image/png",
                                        "data": image_data
                                    }
                                ])
                                alt_text = response.text
                                print("\ngenerated Alt Text (Gemini):")
                                print(alt_text)
                            elif model == "llama":
                                client = OpenAI(
                                    base_url="https://openrouter.ai/api/v1",
                                    api_key=os.getenv("OPENAI_API_KEY")
                                )
                                with open(image_path, "rb") as image_file:
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')

                                completion = client.chat.completions.create(
                                    model="meta-llama/llama-3.2-11b-vision-instruct:free",
                                    messages=[
                                        {
                                        "role": "user",
                                        "content": [
                                            {
                                            "type": "text",
                                            "text": PROMPT
                                            },
                                            {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{image_data}"
                                            }
                                            }
                                        ]
                                        }
                                    ]
                                )
                                alt_text = completion.choices[0].message.content
                                print("\ngenerated Alt Text (Llama 3.2 11B Vision Instruct):")
                                print(alt_text)
                            writer.writerow([filename, model, alt_text])
                        except Exception as e:
                            print(f"failed to process {filename} with {model}: {e}")
                            writer.writerow([filename, model, f"Error: {e}"])


batch_process_screenshots("screenshots", "alttext_results.csv")

# process_screenshot("screenshots/amazon.png", model="openai")

# process_screenshot("screenshots/amazon.png", model="gemini")