from eventlet.hubs import threading
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
import csv
import re
from bs4 import BeautifulSoup
from crawler.crawler_shared_directory.log_manager.log_controller import log

class custom_filter_controller:
    __instance = None
    __S_CUSTOM_FILTER_HASH = set()
    lock = threading.Lock()

    # Keywords indicating possible data leaks
    leak_keywords = ["leak", "breach", "confidential", "exposed", "unauthorized access", "data spill", "hack"]

    # Load company data from CSV
    def load_company_data(self, csv_file):
        companies = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                companies.append(row)
        return companies

    # Singleton pattern implementation
    @staticmethod
    def get_instance():
        if custom_filter_controller.__instance is None:
            custom_filter_controller()
        return custom_filter_controller.__instance

    def __init__(self):
        if custom_filter_controller.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            custom_filter_controller.__instance = self
            self.companies = self.load_company_data('custom_client_dataset.csv')

    def init_filter(self):
        with open("filtered_url.txt", 'r') as file:
            for line in file:
                self.__S_CUSTOM_FILTER_HASH.add(line.strip())

    def validate_custom_html_filter(self, p_base_url, p_html, m_validity_score):
        soup = BeautifulSoup(p_html, 'html.parser')
        plain_text = soup.get_text(separator=' ').lower()
        found_domains = set()
        # Check if any leak-related keywords are present
        leak_indicator_found = any(keyword in plain_text for keyword in self.leak_keywords)

        #if not leak_indicator_found:
        #    return m_validity_score  # Early return if no leak indicators are found

        for company in self.companies:
            domain_regex = rf"\b{re.escape(company['domain'].lower())}\b"
            patterns = []
            if len(company['name'].split()) >= 3:
                patterns.append(re.escape(company['name'].lower()))
            if re.search(domain_regex, plain_text):
                patterns.append(domain_regex)
            if len(company['linkedin url']) > 2:
                patterns.append(re.escape(company['linkedin url'].lower()))

            for pattern in patterns:
                if pattern and re.search(pattern, plain_text) and len(company['domain'])>5:
                    found_domains.add(company['domain'])
                    print("Match found for", company['name'])
                    log.g().s("CUSTOM FILTER : " + "Match Found : " + p_base_url)
                    break

        if found_domains:
            self.write_data(p_base_url, found_domains)
            return m_validity_score

        return m_validity_score

    def write_data(self, p_url, domains):
        domain_list = ','.join(domains)
        if p_url not in self.__S_CUSTOM_FILTER_HASH:
            self.__S_CUSTOM_FILTER_HASH.add(p_url)
            file_path = 'filtered_url.txt'
            with self.lock:
                with open(file_path, 'a') as file:  # 'a' mode will create the file if it doesn't exist
                    file.write(f"{p_url},{domain_list}\n")


