from eventlet.hubs import threading
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
import csv
from bs4 import BeautifulSoup

class custom_filter_controller:
    __instance = None
    __S_CUSTOM_FILTER_HASH = set()
    lock = threading.Lock()

    # Load company data from CSV
    def load_company_data(self, csv_file):
        companies = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                companies.append(row)
        return companies

    # Initializations
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
        plain_text = soup.get_text(separator=' ')

        for company in self.companies:
            name_found = company['name'].lower() in plain_text.lower()
            domain_found = len(company['domain']) > 2 and company['domain'].lower() in plain_text.lower()
            linkedin_found = len(company['linkedin url']) > 2 and company['linkedin url'].lower() in plain_text.lower()

            if name_found or domain_found or linkedin_found:
                self.write_data(p_base_url, company)
                print("match is found")
                return m_validity_score

        return m_validity_score

    def write_data(self, p_url, company_info):
        if p_url not in self.__S_CUSTOM_FILTER_HASH:
            self.__S_CUSTOM_FILTER_HASH.add(p_url)
            file_path = './filtered_url.txt'
            with self.lock:
                with open(file_path, 'a') as file:
                    file.write(f"{p_url},{company_info['name']},{company_info['domain']},{company_info['year founded']},{company_info['industry']},{company_info['size range']},{company_info['locality']},{company_info['country']},{company_info['linkedin url']},{company_info['current employee estimate']},{company_info['total employee estimate']}\n")
