from icrawler.builtin import GoogleImageCrawler
import os
import time
import random

# Set the directory for storing unknown images
unknown_dir = r"C:\Users\USER\Documents\GitHub\malaria-expert-system\backend\dataset\malaria\train\NonBloodSmear\Unknown"

# Ensure the directory exists
os.makedirs(unknown_dir, exist_ok=True)

# Set up Google Image Crawler with optimized settings
google_crawler = GoogleImageCrawler(
    feeder_threads=1,  # Further reduce to 1 to minimize risk of IP bans
    parser_threads=1,  
    downloader_threads=1,  
    storage={"root_dir": unknown_dir}
)

# Search queries for downloading diverse images
search_queries = [
    "random objects", "landscapes", "abstract art", "cars", "animals",
    "furniture", "food", "cityscapes", "paintings", "electronics",
    "flowers", "buildings", "sports", "gadgets", "textures",
    "papers with ink", "handwritten notes", "printed documents", "notebooks with writing",
    "healthy blood smear microscope",
    "white blood cells microscope",
    "sickle cell blood smear",
    "leukemia blood smear",
    "bacteria under microscope",
    "stained tissue microscope"
]

# Shuffle the search queries to avoid patterns
random.shuffle(search_queries)

# Download images for each query
for query in search_queries:
    try:
        print(f"🔍 Downloading images for: {query}...")
        
        google_crawler.crawl(
            keyword=query,
            max_num=500,  # Increased to gather more images
            min_size=(128, 128),
            max_size=None
        )
        
        print(f"✅ Completed: {query}")
        
        # Pause to prevent Google from blocking the requests
        sleep_time = random.uniform(10, 30)  # Increased wait time (10-30 sec)
        print(f"⏳ Waiting {sleep_time:.2f} seconds before next query...")
        time.sleep(sleep_time)

    except Exception as e:
        print(f"❌ Error downloading images for '{query}': {e}")

print("🎉 Download complete! Images saved in 'Unknown' folder.")
