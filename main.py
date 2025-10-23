import requests
import time
import os

def upload_image_to_veed(api_key, image_path):
    """Upload a local image to VEED and get the URL"""
    
    print(f" Uploading image: {image_path}")
    
    url = "https://api.veed.io/v1/uploads"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            
            data = response.json()
            image_url = data.get('url')
            print(f" Image uploaded: {image_url}")
            return image_url
            
    except FileNotFoundError:
        print(f" Image file not found: {image_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f" Upload error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def create_video_from_image(api_key, image_url, text, output_filename="output.mp4"):
    """Create a video from an image with text overlay"""
    
    print(f" Creating video with text: '{text}'")
    
    url = "https://api.veed.io/v1/videos"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create a 5-second video with image and text
    payload = {
        "title": "Generated Video",
        "width": 1920,
        "height": 1080,
        "duration": 5,
        "elements": [
            {
                "type": "image",
                "source": image_url,
                "position": {"x": 0, "y": 0},
                "size": {"width": 1920, "height": 1080},
                "startTime": 0,
                "duration": 5
            },
            {
                "type": "text",
                "content": text,
                "position": {"x": 960, "y": 100},
                "style": {
                    "fontSize": 60,
                    "color": "#FFFFFF",
                    "backgroundColor": "rgba(0, 0, 0, 0.8)",
                    "fontFamily": "Arial",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "padding": 20
                },
                "startTime": 0,
                "duration": 5
            }
        ]
    }
    
    try:
        print(" Creating video project...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        video_id = result.get("id")
        
        print(f" Video project created! ID: {video_id}")
        
        # Request video render
        video_url = render_video(api_key, video_id)
        
        if video_url:
            download_video(video_url, output_filename)
            return True
        else:
            print(" Failed to render video")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f" Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def render_video(api_key, video_id):
    """Request video rendering"""
    
    url = f"https://api.veed.io/v1/videos/{video_id}/render"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {"quality": "1080p"}
    
    try:
        print(" Requesting render...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        render_id = result.get("id")
        
        print(f" Render started! ID: {render_id}")
        
        # Wait for render to complete
        return wait_for_render(api_key, render_id)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Render error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def wait_for_render(api_key, render_id, max_wait=120):
    """Wait for the render to complete"""
    
    url = f"https://api.veed.io/v1/renders/{render_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(" Waiting for video to render (this may take a minute)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            status = data.get("status")
            
            if status == "completed":
                print(" Render completed!")
                return data.get("url")
            elif status == "failed":
                print(" Render failed")
                return None
            else:
                print(f" Status: {status}...")
                time.sleep(5)
                
        except requests.exceptions.RequestException as e:
            print(f" Error checking status: {e}")
            time.sleep(5)
    
    print(" Timeout")
    return None

def download_video(video_url, filename):
    """Download the generated video"""
    
    print(f" Downloading video to {filename}...")
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"📥 Progress: {percent:.1f}%", end='\r')
        
        print(f"\n Video saved as {filename}")
        return True
    except Exception as e:
        print(f" Download error: {e}")
        return False

# ===== MAIN SCRIPT =====
if __name__ == "__main__":
    print("=" * 60)
    print(" VEED Video Generator - Image to Video with Text")
    print("=" * 60)
    print()
    
    # Configuration
    API_KEY = "AIzaSyCF66bGmj1mr_5gAPwKIv0Psaydiz10fuQ"  # Replace with your API key
    IMAGE_FILE = "test.png"              # Your local image file
    TEXT = "make her dance"              # Text to overlay
    OUTPUT_FILE = "output_video.mp4"     # Output filename
    
    # Check if image exists
    if not os.path.exists(IMAGE_FILE):
        print(f" Error: Image file '{IMAGE_FILE}' not found!")
        print(f" Please make sure {IMAGE_FILE} is in the current directory.")
        print()
        print("Current directory:", os.getcwd())
        print()
        exit(1)
    
    # Check if API key is set
    if API_KEY == "your_veed_api_key_here":
        print("  WARNING: API key not set!")
        print()
        print(" To use this script:")
        print("1. Get your API key from https://www.veed.io/api")
        print("2. Open main.py and replace 'your_veed_api_key_here' with your key")
        print("3. Run: python main.py")
        print()
        exit(1)
    
    print(f" Image: {IMAGE_FILE}")
    print(f" Text: '{TEXT}'")
    print(f" Output: {OUTPUT_FILE}")
    print("=" * 60)
    print()
    
    # Step 1: Upload image
    image_url = upload_image_to_veed(API_KEY, IMAGE_FILE)
    
    if not image_url:
        print("\n Failed to upload image")
        exit(1)
    
    print()
    
    # Step 2: Create video
    success = create_video_from_image(API_KEY, image_url, TEXT, OUTPUT_FILE)
    
    print()
    print("=" * 60)
    if success:
        print(" SUCCESS! Video created successfully!")
        print(f"Check {OUTPUT_FILE} in your current directory")
    else:
        print(" FAILED - Check errors above")
    print("=" * 60)
