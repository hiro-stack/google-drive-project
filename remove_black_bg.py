from PIL import Image

def make_transparent(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # item is (R, G, B, A)
            # Check if likely black (allow some noise: R,G,B < 50)
            if item[0] < 50 and item[1] < 50 and item[2] < 50:
                # Make transparent (keep R,G,B but set Alpha to 0)
                # Or set to white/transparent
                newData.append((0, 0, 0, 0)) # Fully transparent black
            else:
                # Keep original color
                # Optional: Ensure it's fully opaque if it's white
                newData.append(item)

        img.putdata(newData)
        img.save(image_path, "PNG")
        print(f"Successfully processed {image_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

# Target file
target = "c:/Users/zhang/python/ai_project_2/frontend/public/mic-icon.png"
make_transparent(target)
