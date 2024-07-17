import concurrent.futures
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import logging
import json
import traceback

class WebCrawler:
    def __init__(self, start_url, max_depth=5, max_retries=3):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_retries = max_retries
        self.visited = set()
        self.all_text = []
        self.successful_urls_file = "successful_urls.txt"
        self.crawled_data_file = "crawled_data.json"
        self.error_log_file = "error_log.txt"

    def get_page_content(self, url):
        logging.info(f"Processing: {url}")
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()
                logging.info(f"Successfully processed: {url}")
                with open(self.successful_urls_file, 'a') as f:
                    f.write(f"{url}\n")
                
                with open(self.crawled_data_file, 'a') as f:
                    json.dump({"url": url, "text": text_content}, f)
                    f.write('\n')
                
                return str(soup), text_content
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logging.error(f"All attempts failed for {url}")
                    with open(self.error_log_file, 'a') as f:
                        f.write(f"Error processing {url}: {str(e)}\n")
                        f.write(traceback.format_exc())
                        f.write("\n" + "="*50 + "\n")
                    return None, None
        return None, None

    def parse_links(self, url, html_content):
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                if full_url.startswith(self.start_url):
                    links.append(full_url)
        except Exception as e:
            logging.error(f"Error parsing links from {url}: {str(e)}")
            with open(self.error_log_file, 'a') as f:
                f.write(f"Error parsing links from {url}: {str(e)}\n")
                f.write(traceback.format_exc())
                f.write("\n" + "="*50 + "\n")
        return links

    def crawl_recursive(self, url, depth=0):
        if depth > self.max_depth or url in self.visited:
            return
        
        self.visited.add(url)
        html_content, text_content = self.get_page_content(url)
        
        if html_content and text_content:
            self.all_text.append((text_content, url))
            links = self.parse_links(url, html_content)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.crawl_recursive, link, depth + 1) for link in links]
                concurrent.futures.wait(futures)

    def crawl(self):
        logging.info(f"Starting crawl from: {self.start_url}")
        self.crawl_recursive(self.start_url)
        logging.info("Crawling process completed.")

    def save_all_text(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for text, url in self.all_text:
                f.write(f"URL: {url}\n")
                f.write(f"{text}\n")
                f.write("\n" + "="*50 + "\n\n")
        logging.info(f"All text content has been saved to {filename}")