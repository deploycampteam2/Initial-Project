#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper untuk mengunduh gambar tempat wisata Indonesia
Menggunakan Bing Image Search untuk mendapatkan 5 gambar per lokasi
"""

import requests
import pandas as pd
import time
from PIL import Image
import io
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TourismImageScraper:
    def __init__(self, images_per_place=5, delay_between_requests=1.0):
        """
        Initialize scraper untuk gambar tempat wisata
        
        Args:
            images_per_place (int): Jumlah gambar per tempat wisata (default: 5)
            delay_between_requests (float): Delay antara request dalam detik (default: 1.0)
        """
        self.images_per_place = images_per_place
        self.delay = delay_between_requests
        
        # Headers untuk request yang lebih natural
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Create image directory
        self.image_dir = Path("image")
        self.image_dir.mkdir(exist_ok=True)
        
        # Track progress
        self.stats = {
            'total_places': 0,
            'processed_places': 0,
            'total_downloaded': 0,
            'failed_downloads': 0,
            'skipped_places': 0
        }

    def sanitize_filename(self, text):
        """
        Bersihkan nama file dari karakter yang tidak valid
        
        Args:
            text (str): Text yang akan dibersihkan
            
        Returns:
            str: Text yang sudah dibersihkan
        """
        import re
        # Remove special characters and replace with underscore
        clean_text = re.sub(r'[^\w\s-]', '', text)
        clean_text = re.sub(r'[-\s]+', '_', clean_text)
        return clean_text[:50]  # Limit length

    def search_bing_images(self, query, num_images=5):
        """
        Search gambar menggunakan Bing Image Search
        
        Args:
            query (str): Query pencarian
            num_images (int): Jumlah gambar yang diinginkan
            
        Returns:
            list: List URL gambar
        """
        try:
            # URL Bing Image Search with different parameters
            search_url = "https://www.bing.com/images/search"
            params = {
                'q': query,
                'form': 'HDRSC3',
                'first': 1,
                'count': num_images * 2,
                'qft': '+filterui:aspect-wide+filterui:imagesize-large'  # Large wide images
            }
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Extract image URLs from response
            image_urls = []
            html_content = response.text
            
            # Debug: Print a small part of HTML to understand structure
            logger.debug(f"HTML snippet: {html_content[:500]}")
            
            # Simple regex untuk extract image URLs dari Bing
            import re
            
            # Try direct image URLs first (most reliable)
            direct_patterns = [
                r'https://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s"\'<>]*)?',
                r'http://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s"\'<>]*)?'
            ]
            
            all_urls = set()  # Use set to avoid duplicates
            
            for pattern in direct_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    # Clean up URL more thoroughly
                    clean_url = match.split('"')[0].split("'")[0].split('<')[0].split('>')[0]
                    clean_url = clean_url.split('&quot;')[0].split('\\')[0]
                    
                    # Must be valid URL and image
                    if clean_url.startswith(('http://', 'https://')) and any(ext in clean_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        # Skip common non-image URLs and domains
                        skip_domains = ['bing.com', 'microsoft.com', 'msn.com', 'live.com', 'googleapis.com']
                        skip_patterns = ['logo', 'icon', 'avatar', 'thumb', 'placeholder']
                        
                        if not any(domain in clean_url for domain in skip_domains):
                            if not any(pattern in clean_url.lower() for pattern in skip_patterns):
                                all_urls.add(clean_url)
            
            # Convert to list and take the first num_images
            image_urls = list(all_urls)[:num_images]
            
            # If we still don't have enough, try fallback to Google Images
            if len(image_urls) < num_images // 2:
                google_urls = self.search_google_images(query, num_images - len(image_urls))
                image_urls.extend(google_urls)
            
            logger.info(f"Found {len(image_urls)} image URLs for query: {query}")
            return image_urls[:num_images]
            
        except Exception as e:
            logger.error(f"Error searching Bing images for '{query}': {str(e)}")
            return []
    
    def search_google_images(self, query, num_images=5):
        """
        Fallback: Search gambar menggunakan Google Images
        
        Args:
            query (str): Query pencarian
            num_images (int): Jumlah gambar yang diinginkan
            
        Returns:
            list: List URL gambar
        """
        try:
            search_url = "https://www.google.com/search"
            params = {
                'q': query,
                'tbm': 'isch',  # Image search
                'num': num_images * 2,
                'safe': 'active'
            }
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            import re
            
            # Extract image URLs from Google Images
            image_urls = []
            
            # Google Images patterns
            patterns = [
                r'https://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s"\'<>]*)?',
                r'http://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s"\'<>]*)?'
            ]
            
            all_urls = set()
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    clean_url = match.split('"')[0].split("'")[0].split('<')[0].split('>')[0]
                    
                    # Skip Google's own URLs and common non-content URLs
                    skip_domains = ['google.com', 'googleusercontent.com', 'gstatic.com']
                    if not any(domain in clean_url for domain in skip_domains):
                        all_urls.add(clean_url)
            
            image_urls = list(all_urls)[:num_images]
            logger.info(f"Google fallback found {len(image_urls)} URLs for: {query}")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error searching Google images for '{query}': {str(e)}")
            return []

    def download_image(self, url, save_path):
        """
        Download gambar dari URL
        
        Args:
            url (str): URL gambar
            save_path (Path): Path untuk menyimpan gambar
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Request dengan timeout
            response = requests.get(url, headers=self.headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                logger.warning(f"URL tidak mengandung gambar: {url}")
                return False
            
            # Read image data
            image_data = response.content
            
            # Validate image dengan PIL
            try:
                img = Image.open(io.BytesIO(image_data))
                
                # Check image size (minimal 100x100 pixels)
                if img.width < 100 or img.height < 100:
                    logger.warning(f"Gambar terlalu kecil ({img.width}x{img.height}): {url}")
                    return False
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save dengan kualitas yang baik
                img.save(save_path, 'JPEG', quality=85, optimize=True)
                
                logger.info(f"✅ Downloaded: {save_path.name} ({img.width}x{img.height})")
                return True
                
            except Exception as e:
                logger.error(f"Error validating image from {url}: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return False

    def scrape_place_images(self, place_row):
        """
        Scrape gambar untuk satu tempat wisata
        
        Args:
            place_row: Row data tempat wisata dari pandas DataFrame
            
        Returns:
            int: Jumlah gambar yang berhasil didownload
        """
        place_id = place_row['Place_Id']
        place_name = place_row['Place_Name']
        city = place_row['City']
        category = place_row['Category']
        
        logger.info(f"\n🔍 Processing: {place_name} ({city})")
        
        # Create folder untuk tempat ini
        folder_name = f"{place_id:03d}_{self.sanitize_filename(place_name)}"
        place_folder = self.image_dir / folder_name
        place_folder.mkdir(exist_ok=True)
        
        # Check jika sudah ada cukup gambar
        existing_images = list(place_folder.glob("*.jpg"))
        if len(existing_images) >= self.images_per_place:
            logger.info(f"✅ Folder {folder_name} already has {len(existing_images)} images, skipping...")
            self.stats['skipped_places'] += 1
            return len(existing_images)
        
        # Buat query pencarian yang lebih spesifik
        search_queries = [
            f"{place_name} {city} indonesia wisata",
            f"{place_name} {city} tourism",
            f"{place_name} {city} tempat wisata",
            f"wisata {place_name} {city}",
            f"{place_name} indonesia destination"
        ]
        
        downloaded_count = len(existing_images)
        
        # Try each search query until we get enough images
        for query_idx, query in enumerate(search_queries):
            if downloaded_count >= self.images_per_place:
                break
                
            logger.info(f"🔎 Searching with query {query_idx + 1}: {query}")
            
            # Search untuk gambar
            image_urls = self.search_bing_images(query, self.images_per_place - downloaded_count + 2)
            
            if not image_urls:
                logger.warning(f"No images found for query: {query}")
                continue
            
            # Download gambar
            for img_idx, url in enumerate(image_urls):
                if downloaded_count >= self.images_per_place:
                    break
                
                # Generate filename
                file_extension = 'jpg'
                filename = f"{place_id:03d}_{downloaded_count + 1:02d}.{file_extension}"
                save_path = place_folder / filename
                
                # Skip jika file sudah ada
                if save_path.exists():
                    continue
                
                logger.info(f"📥 Downloading image {downloaded_count + 1}/{self.images_per_place}...")
                
                # Download
                if self.download_image(url, save_path):
                    downloaded_count += 1
                    self.stats['total_downloaded'] += 1
                else:
                    self.stats['failed_downloads'] += 1
                
                # Delay between downloads
                time.sleep(self.delay)
            
            # Delay between queries
            if query_idx < len(search_queries) - 1:
                time.sleep(self.delay * 2)
        
        self.stats['processed_places'] += 1
        logger.info(f"📊 Downloaded {downloaded_count} images for {place_name}")
        
        return downloaded_count

    def scrape_all_places(self, csv_file="archive/tourism_with_id.csv", start_from=0, max_places=None):
        """
        Scrape gambar untuk semua tempat wisata dari CSV file
        
        Args:
            csv_file (str): Path ke file CSV
            start_from (int): Index tempat untuk mulai (untuk resume)
            max_places (int): Maksimal tempat yang diproses (None untuk semua)
        """
        try:
            # Load data
            logger.info(f"📖 Loading tourism data from {csv_file}...")
            df = pd.read_csv(csv_file)
            
            if start_from > 0:
                df = df.iloc[start_from:]
                logger.info(f"🔄 Resuming from index {start_from}")
            
            if max_places:
                df = df.head(max_places)
                logger.info(f"📊 Processing maximum {max_places} places")
            
            self.stats['total_places'] = len(df)
            logger.info(f"📊 Total places to process: {len(df)}")
            
            # Process each place
            for idx, (_, row) in enumerate(df.iterrows()):
                try:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"🏛️  Place {idx + 1}/{len(df)}: {row['Place_Name']}")
                    logger.info(f"{'='*60}")
                    
                    downloaded = self.scrape_place_images(row)
                    
                    # Print progress every 10 places
                    if (idx + 1) % 10 == 0:
                        self.print_stats()
                    
                    # Longer delay between places
                    time.sleep(self.delay * 3)
                    
                except KeyboardInterrupt:
                    logger.info("\n⏸️  Scraping interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"❌ Error processing {row['Place_Name']}: {str(e)}")
                    continue
            
            # Final stats
            logger.info(f"\n{'='*60}")
            logger.info("🎉 SCRAPING COMPLETED!")
            self.print_stats()
            logger.info(f"{'='*60}")
            
        except FileNotFoundError:
            logger.error(f"❌ File {csv_file} tidak ditemukan!")
        except Exception as e:
            logger.error(f"❌ Error in scrape_all_places: {str(e)}")

    def print_stats(self):
        """Print statistik scraping"""
        logger.info(f"""
📊 SCRAPING STATISTICS:
   • Total places: {self.stats['total_places']}
   • Processed places: {self.stats['processed_places']}
   • Skipped places: {self.stats['skipped_places']}
   • Total images downloaded: {self.stats['total_downloaded']}
   • Failed downloads: {self.stats['failed_downloads']}
   • Success rate: {(self.stats['total_downloaded']/(self.stats['total_downloaded']+self.stats['failed_downloads'])*100) if (self.stats['total_downloaded']+self.stats['failed_downloads']) > 0 else 0:.1f}%
        """)

def main():
    """Main function"""
    logger.info("🎯 Starting Tourism Image Scraper")
    logger.info("Using Bing Image Search to download 5 images per tourist location")
    
    # Initialize scraper
    scraper = TourismImageScraper(
        images_per_place=5,
        delay_between_requests=1.5  # Respectful delay
    )
    
    # Start scraping
    try:
        scraper.scrape_all_places(
            csv_file="archive/tourism_with_id.csv",
            start_from=0,  # Change this to resume from specific index
            max_places=None  # Set number to limit processing for testing
        )
    except KeyboardInterrupt:
        logger.info("👋 Scraping stopped by user")
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}")

if __name__ == "__main__":
    main()