import speech_recognition as sr
import sounddevice as sd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

samplerate = 16000 
def recognize_command():
    recognizer = sr.Recognizer()
    print("please speak a command...")
    duration =  5
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    audio = sr.AudioData(audio_data.tobytes(), samplerate, 2)
    try:
        command = recognizer.recognize_google(audio)
        print("you said", command)
        return command.lower()
    except sr.UnknownValueError:
        print("can't understand")
    except sr.RequestError as e:
        print("could not request results", e)
    return None

def handle_command(command):
    if "scroll down" in command:
        print("scrolling down...")
        driver.execute_script("window.scrollBy({ top: window.innerHeight, behavior: 'smooth' });")
        time.sleep(1)
    elif "scroll up" in command:
        print("scrolling up...")
        driver.execute_script("window.scrollBy({ top: -window.innerHeight, behavior: 'smooth' });")
        time.sleep(1)
    elif "search bar" in command or "go to search" in command:
        print("focusing on search bar...")
        try:
            search_bar = driver.find_element(By.ID, "searchInput")
            driver.execute_script("arguments[0].focus();", search_bar)
        except:
            print("can not find search bar")
    elif "first heading" in command:
        print("going to the first heading...")
        driver.execute_script("""
            headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
            if (headings.length > 0) {
                headings.sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top)
                headings[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        """)
    else:
        print("sorry, I don't recognize that command yet.")

if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.wikipedia.org") 
    time.sleep(2)
    command = recognize_command()
    if command:
        handle_command(command)
    input("Press Enter to exit...")
