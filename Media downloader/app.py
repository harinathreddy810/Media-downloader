import os
import instaloader
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from yt_dlp import YoutubeDL
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Path to ChromeDriver
CHROME_DRIVER_PATH = r"C:\Path\To\ChromeDriver\chromedriver.exe"  # Update with your actual ChromeDriver path

# Directory to save downloads
DOWNLOAD_PATH = r"C:\Users\harinathreddy\Downloads\media"

# Ensure download directory exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Unified download function
def download_media(url, platform):
    print(f"Attempting to download from URL: {url}, Platform: {platform}")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'nocheckcertificate': True,
        'cookies': r'C:\Path\To\cookies.txt',  # Update with your cookies file path
        'verbose': True,  # Enable verbose logging
    }
    
    try:
        if platform in ['youtube', 'facebook']:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        elif platform == 'instagram':
            # Use yt-dlp for downloading Instagram videos
            download_instagram_video(url)
            return True
        else:
            raise ValueError("Unsupported platform.")
    except Exception as e:
        print(f"Failed to download media: {e}")
        return False

def download_instagram_video(instagram_url):
    ydl_opts = {
        'format': 'bestvideo',
        'outtmpl': os.path.join(DOWNLOAD_PATH, 'instagram_video.%(ext)s'),
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([instagram_url])
        print("Instagram video downloaded successfully.")
    except Exception as e:
        print(f"An error occurred while downloading Instagram video: {e}")

# Function to capture WhatsApp status
def download_whatsapp_status():
    options = Options()
    options.add_argument("user-data-dir=./chrome_profile")
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.get("https://web.whatsapp.com")
    time.sleep(15)  # Wait for the user to scan QR code

    try:
        driver.find_element(By.XPATH, "//span[@data-icon='status']").click()
        time.sleep(5)  # Wait for statuses to load
        status_elements = driver.find_elements(By.CLASS_NAME, "_2v3VV")
        
        for index, status in enumerate(status_elements):
            status.screenshot(os.path.join(DOWNLOAD_PATH, f"whatsapp_status_{index}.png"))
        return True
    except Exception as e:
        print(f"Failed to download WhatsApp status: {e}")
        return False
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        platform = request.form.get('platform')

        if url and platform:
            if download_media(url, platform):
                flash(f'Downloaded {platform.capitalize()} media successfully!', 'success')
            else:
                flash(f'Failed to download {platform} media.', 'danger')
        else:
            flash('Please provide a URL and select a platform.', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
