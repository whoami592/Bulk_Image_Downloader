import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import time

def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════╗
    ║         BULK IMAGE DOWNLOADER v1.0                 ║
    ║                                                    ║
    ║   Coded by Pakistani Ethical Hacker                ║
    ║         Mr. Sabaz Ali Khan                         ║
    ║                                                    ║
    ╚════════════════════════════════════════════════════╝
    """
    print(banner)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_image(img_url, folder, headers):
    try:
        # Parse the URL to get a valid filename
        parsed_url = urllib.parse.urlparse(img_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = img_url.split('/')[-1] or f"image_{int(time.time())}.jpg"
        
        # Ensure filename is valid
        filename = "".join(c for c in filename if c.isalnum() or c in ('.', '_', '-'))
        filepath = os.path.join(folder, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"Skipped: {filename} (already exists)")
            return
        
        # Download the image
        response = requests.get(img_url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed: {img_url} (Status: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {img_url}: {str(e)}")

def scrape_and_download(url, folder="downloaded_images", max_images=50):
    print_banner()
    
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Create directory for downloads
    create_directory(folder)
    
    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image tags
        img_tags = soup.find_all('img')
        image_urls = []
        
        # Extract image URLs
        for img in img_tags:
            src = img.get('src')
            if src:
                # Handle relative URLs
                if not src.startswith(('http://', 'https://')):
                    src = urllib.parse.urljoin(url, src)
                # Filter for common image extensions
                if src.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    image_urls.append(src)
        
        image_urls = list(dict.fromkeys(image_urls))[:max_images]  # Remove duplicates and limit
        if not image_urls:
            print("No images found on the webpage.")
            return
        
        print(f"Found {len(image_urls)} images. Starting download...")
        
        # Download images concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda img_url: download_image(img_url, folder, headers), image_urls)
        
        print(f"\nDownload complete! Images saved to '{folder}' directory.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    url = input("Enter the website URL to download images from: ")
    folder_name = input("Enter folder name to save images (default: downloaded_images): ") or "downloaded_images"
    max_images = int(input("Enter maximum number of images to download (default: 50): ") or 50)
    scrape_and_download(url, folder_name, max_images)