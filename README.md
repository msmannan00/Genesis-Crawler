# Genesis Crawler

Genesis Crawler is a dark web-focused crawling tool built with Docker Compose. It consists of two main variants:  
1. **Generic Crawler**: Crawls and gathers data from generic websites.  
2. **Specific Crawler**: Loads custom parsers from a server to specifically crawl supported websites in a fine-tuned manner.

The project is designed for heavy-duty web scraping, equipped with tools to detect illegal material and categorize content. Built on top of multitor, it provides enhanced anonymity and protection while crawling the dark web.

## Features

- **Docker Compose Setup**: Easy to set up and deploy via Docker Compose.
- **Anonymity with multitor**: Ensures anonymity while crawling dark web content.
- **Customizable Crawling**: Custom parsers are used to specifically crawl certain websites, giving fine-grained control over the crawling process.
- **Illegal Content Detection**: Equipped with tools to detect and categorize illegal content.
- **Two Crawling Variants**:  
  - Generic crawler for general data collection.  
  - Specific crawler with custom parsers for in-depth site crawling.

## Technology Stack

The project leverages multiple programming languages, tools, and libraries to achieve its goals:

- **Languages**:  
  - Python: Used for the core logic, handling web requests, processing data, and managing workflows.
  
- **Libraries/Frameworks**:  
  - **Web Scraping & Parsing**:  
    - requests, beautifulsoup4, lxml, urllib3, and html-similarity are used for fetching and parsing HTML content from the web.  
  - **Data Processing**:  
    - pandas, numpy, scikit-learn, and gensim provide tools for data manipulation, machine learning, and natural language processing.  
  - **Natural Language Processing (NLP)**:  
    - spacy, nltk, and thefuzz enable advanced text analysis and similarity checking.  
  - **Machine Learning & AI**:  
    - transformers, torch, and onnxruntime support deep learning and model inference.  
  - **Database & Search**:  
    - elasticsearch, pymongo, and redis for efficient data storage and retrieval.  
  - **Task Management & Scheduling**:  
    - celery, schedule, and eventlet handle distributed tasks and job scheduling.  
  - **Security & Encryption**:  
    - fernet is used for data encryption.  
  - **Networking & Proxying**:  
    - socks, aiohttp_socks, and requests[socks] enable proxy-based web requests, especially useful for dark web crawling.  
  - **Error Logging**:  
    - logdna and raven help monitor and log errors during the crawling process.

## Setup and Installation

To get started with Genesis Crawler, follow these steps:

### 1. Clone the Repository

Clone the repository from GitHub and navigate to the project directory.

git clone https://github.com/msmannan00/Genesis-Crawler.git
cd genesis-crawler



### 2. Install Dependencies

Ensure you have Docker and Docker Compose installed on your machine. Once installed, the dependencies will be handled via Docker Compose.

### 3. Build and Start the Crawler

Use Docker Compose to build and run the crawler:

./run.sh build


to simply start the crawler run

./run.sh


to run and update unique urls while removing not only duplicate url but also removing url that are no longer active run

./run.sh invoke_unique_crawler



This will start the crawler, which can now begin collecting data.

### 4. Customizing Parsers (Optional for Specific Crawler)

For specific website crawling, you can provide your own parsers. Load them onto the server and configure the crawler to use these custom parsers for enhanced scraping capabilities.

## Usage

## Contribution

We welcome contributions to improve Genesis Crawler. If you'd like to contribute, please fork the repository and submit a pull request.

### Steps to Contribute

1. Fork the repository.  
2. Create a new feature branch (git checkout -b feature-branch).  
3. Commit your changes (git commit -m 'Add some feature').  
4. Push to the branch (git push origin feature-branch).  
5. Create a new Pull Request.

## License

Genesis Crawler is licensed under the [MIT License](LICENSE).

## Disclaimer

This project is intended for research purposes only. The authors of Genesis Crawler do not support or endorse illegal activities, and users of this project are responsible for ensuring their actions comply with the law.

## GitHub Repository

GitHub Repository URL: [https://github.com/msmannan00/Genesis-Crawler](https://github.com/msmannan00/Genesis-Crawler)
