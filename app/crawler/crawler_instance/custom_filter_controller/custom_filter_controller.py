import os
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

    # Load company data from CSV and create hash dictionary
    def load_company_data(self, csv_file):
        companies = []
        company_hashes = {}
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                companies.append(row)
                domain = row['domain'].lower()
                linkedin_url = row['linkedin url'].lower()
                company_hashes[domain] = row
                if len(linkedin_url) > 2:
                    company_hashes[linkedin_url] = row
        return companies, company_hashes

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
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(script_dir, 'custom_client_dataset.csv')
            self.companies, self.company_hashes = self.load_company_data(csv_path)

    def init_filter(self):
        if not os.path.exists("filtered_url.txt"):
            open("filtered_url.txt", 'a').close()
        with open("filtered_url.txt", 'r') as file:
            for line in file:
                self.__S_CUSTOM_FILTER_HASH.add(line.strip())

    def validate_custom_html_filter(self, p_base_url, p_html, m_validity_score):
        p_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Company List</title>
        </head>
        <body>
            <h1>Company List</h1>
            <ul>
                <li>
                    <a href="http://dxc.technology">DXC Technology</a> - <a href="http://linkedin.com/company/dxctechnology">LinkedIn</a>
                </li>
                <li>
                    <a href="http://miami.edu">University of Miami</a> - <a href="http://linkedin.com/company/university-of-miami">LinkedIn</a>
                </li>
            </ul>
            <p>Text mentioning broward.edu and linkedin.com/company/broward-college.</p>
            <p>Text mentioning foxnews.com and linkedin.com/company/fox-news-channel.</p>
        </body>
        </html>
        """

        # Now, this HTML can be passed to the validate_custom_html_filter method

        soup = BeautifulSoup(p_html, 'html.parser')
        plain_text = soup.get_text(separator=' ').lower()
        urls = [a['href'].lower() for a in soup.find_all('a', href=True)]
        plain_text += ' ' + ' '.join(urls)
        found_domains = set()

        for key in self.company_hashes:
            if key in plain_text:
                found_domains.add(self.company_hashes[key]['domain'])
                print("Match found for", self.company_hashes[key]['name'])
                log.g().s("CUSTOM FILTER : " + "Match Found : " + p_base_url)

        if found_domains:
            self.write_data(p_base_url, found_domains)
            return m_validity_score

        return m_validity_score

    def write_data(self, p_url, domains):
        domain_list = ','.join(domains)
        if p_url not in self.__S_CUSTOM_FILTER_HASH:
            self.__S_CUSTOM_FILTER_HASH.add(p_url)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(script_dir, 'filtered_url.txt')
            file_path = data_path
            with self.lock:
                with open(file_path, 'a') as file:  # 'a' mode will create the file if it doesn't exist
                    file.write(f"{p_url},{domain_list}\n")
