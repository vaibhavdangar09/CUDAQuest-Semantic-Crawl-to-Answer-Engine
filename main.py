from crawler.web_crawler import WebCrawler
from data_processing.chunking import Chunker
from data_processing.embedding import Embedder
from vector_db.milvus_db import MilvusDB
from utils.logger import setup_logger
import logging

def main():
    setup_logger()
    
    # Web Crawling
    start_url = "https://docs.nvidia.com/cuda/"
    crawler = WebCrawler(start_url)
    crawler.crawl()
    
    all_text_file = "all_text_content.txt"
    crawler.save_all_text(all_text_file)
    
    # Data Chunking
    embedder = Embedder()
    chunker = Chunker(embedder.embeddings)
    chunks = chunker.chunk_text(crawler.all_text)
    
    # Embedding Creation
    embeddings = embedder.create_embeddings(chunks)
    
    # Vector Storage
    milvus_db = MilvusDB()
    collection = milvus_db.create_collection("cuda_docs", dim=384)  # Adjust dim based on your embedding model
    milvus_db.insert_data(collection, embeddings, chunks)
    
    logging.info(f"Number of pages crawled: {len(crawler.all_text)}")
    logging.info(f"Number of chunks created and stored: {len(chunks)}")
    logging.info(f"All text content has been saved to {all_text_file}")
    logging.info(f"Chunks have been saved to chunks_in_progress.txt")
    logging.info(f"Successfully processed URLs have been saved to {crawler.successful_urls_file}")
    logging.info(f"Crawled data has been saved to {crawler.crawled_data_file}")
    logging.info(f"Error log has been saved to {crawler.error_log_file}")

if __name__ == "__main__":
    main()