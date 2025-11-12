"""
Test image upload to ImgBB
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_course_thumbnail(title, color, size=(400, 300)):
    """Create a simple course thumbnail"""
    # Create image
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add text
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), title, fill='white', font=font)
    
    return img

def upload_to_imgbb(image, filename, api_key):
    """Upload image to ImgBB"""
    # Convert PIL image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Convert to base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    # Upload to ImgBB
    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'image': img_base64,
        'name': filename
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['data']['url']
    
    return None

def main():
    api_key = "3b05045025d5ef1fd1ad13a864909d2c"
    
    # Course thumbnails to create
    courses = [
        ("Python Programming", "#3B82F6"),
        ("React Development", "#06B6D4"), 
        ("Data Science", "#8B5CF6"),
        ("Machine Learning", "#10B981"),
        ("Web Bootcamp", "#F59E0B"),
        ("JavaScript", "#EF4444")
    ]
    
    print("🎨 Creating and uploading course thumbnails...")
    
    uploaded_urls = {}
    
    for course_name, color in courses:
        try:
            # Create thumbnail
            img = create_course_thumbnail(course_name, color)
            
            # Upload to ImgBB
            filename = f"{course_name.lower().replace(' ', '_')}_thumbnail"
            url = upload_to_imgbb(img, filename, api_key)
            
            if url:
                uploaded_urls[course_name] = url
                print(f"✅ {course_name}: {url}")
            else:
                print(f"❌ {course_name}: Upload failed")
                
        except Exception as e:
            print(f"❌ {course_name}: Error - {e}")
    
    print(f"\n📊 Successfully uploaded {len(uploaded_urls)}/6 images")
    
    # Update courses in database
    if uploaded_urls:
        print("\n🔄 Updating courses with new thumbnails...")
        
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from src.database.models import get_db
            
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Map course names to database titles
            course_mapping = {
                "Python Programming": "Python Programming for Beginners",
                "React Development": "Web Development with React",
                "Data Science": "Data Science Fundamentals", 
                "Machine Learning": "Machine Learning Fundamentals",
                "Web Bootcamp": "Complete Web Development Bootcamp",
                "JavaScript": "JavaScript Fundamentals"
            }
            
            for short_name, url in uploaded_urls.items():
                full_name = course_mapping.get(short_name)
                if full_name:
                    cursor.execute("""
                        UPDATE courses SET thumbnail_url = ? WHERE title = ?
                    """, (url, full_name))
                    print(f"✅ Updated {full_name}")
            
            conn.commit()
            print(f"\n🎉 Successfully updated {len(uploaded_urls)} courses with thumbnails!")
            
        except Exception as e:
            print(f"❌ Database update failed: {e}")

if __name__ == "__main__":
    main()
