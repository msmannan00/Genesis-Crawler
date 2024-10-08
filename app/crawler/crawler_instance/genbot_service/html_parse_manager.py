import pathlib
import re
import validators
import phonenumbers
import spacy
from urllib.parse import urljoin, urlparse
from abc import ABC
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from thefuzz import fuzz
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import STRINGS
from crawler.crawler_instance.genbot_service.genbot_enums import PARSE_TAGS
from crawler.crawler_instance.local_shared_model.index_model import index_model_init
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_services.helper_services.spell_check_handler import spell_checker_handler
nlp_core = spacy.load("en_core_web_sm")

class html_parse_manager(HTMLParser, ABC):

    def __init__(self, p_html, p_request_model):
        super().__init__()
        self.m_html = p_html
        self.request_model = p_request_model
        self.m_base_url = p_request_model.m_url
        self.m_soup = None

        self.m_title = STRINGS.S_EMPTY
        self.m_meta_description = STRINGS.S_EMPTY
        self.m_meta_content = STRINGS.S_EMPTY
        self.m_important_content = STRINGS.S_EMPTY
        self.m_content = STRINGS.S_EMPTY
        self.m_meta_keyword = STRINGS.S_EMPTY
        self.m_content_type = CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
        self.m_sub_url = []
        self.m_sub_url_hashed = []
        self.m_image_url = []
        self.m_doc_url = []
        self.m_video_url = []
        self.m_archive_url = []

        # New variables for extracted data
        self.m_clearnet_links = []

        self.m_paragraph_count = 0
        self.m_parsed_paragraph_count = 0
        self.m_query_url_count = 0
        self.m_non_important_text = STRINGS.S_EMPTY
        self.m_all_url_count = 0
        self.m_important_content_raw = []
        self.m_rec = PARSE_TAGS.S_NONE

        # New variable for managing sections
        self.m_sections = []
        self.m_current_section = ""  # This will accumulate consecutive paragraphs

    def __insert_external_url(self, p_url):
        self.m_all_url_count += 1

        # Extended list of archive extensions to check for compressed files (e.g., zip, tar, rar, etc.)
        archive_extensions = ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz', '.tgz', '.tbz2', '.tar.gz', '.tar.bz2']

        # File extension lists for images, videos, and documents
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff']
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
        document_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt']

        # Check if the URL is not None and does not end with "#"
        if p_url is not None and not str(p_url).endswith("#"):
            if 5 < len(p_url) <= CRAWL_SETTINGS_CONSTANTS.S_MAX_URL_SIZE:
                # Join relative URLs if they don't start with a valid scheme (http, https, ftp)
                if not p_url.startswith(("https://", "http://", "ftp://")):
                    m_temp_base_url = self.m_base_url
                    p_url = urljoin(m_temp_base_url, p_url)
                    p_url = p_url.replace(" ", "%20")
                    p_url = helper_method.on_clean_url(helper_method.normalize_slashes(p_url))

                # Validate if the URL is valid
                if validators.url(p_url):
                    suffix = ''.join(pathlib.Path(p_url).suffixes)
                    m_host_url = helper_method.get_host_url(p_url)
                    parent_domain = helper_method.on_clean_url(self.m_base_url).split(".")[0]
                    host_domain = helper_method.on_clean_url(p_url).split(".")[0]

                    # Parse the URL to get the path without query parameters or fragments
                    parsed_url = urlparse(p_url)
                    clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

                    # Check if the URL is an image, video, document, or archive based on suffix or MIME type
                    if any(ext in suffix.lower() for ext in image_extensions):
                        if len(self.m_image_url) < 10:
                            self.m_image_url.append(clean_url)
                    elif any(ext in suffix.lower() for ext in video_extensions):
                        if len(self.m_video_url) < 10:
                            self.m_video_url.append(clean_url)
                    elif any(ext in suffix.lower() for ext in document_extensions):
                        if len(self.m_doc_url) < 10:
                            self.m_doc_url.append(clean_url)
                    elif any(ext in suffix.lower() for ext in archive_extensions):
                        if len(self.m_archive_url) < 10:
                            self.m_archive_url.append(clean_url)

                    # Handle .onion links separately
                    elif parent_domain == host_domain and m_host_url.endswith(".onion"):
                        if "#" in p_url:
                            if p_url.count("/") > 2 and "?" in m_host_url and self.m_query_url_count < 5:
                                self.m_query_url_count += 1
                                clean_url = helper_method.normalize_slashes(clean_url)
                                if clean_url not in self.m_sub_url_hashed:
                                    self.m_sub_url_hashed.append(clean_url)
                        else:
                            self.m_query_url_count += 1
                            p_url = p_url.rstrip('/')
                            if p_url not in self.m_sub_url and p_url != self.m_base_url:
                                self.m_sub_url.append(p_url)

                    # Add to clearnet links if it's not an onion link
                    if ".onion" not in p_url:
                        self.m_clearnet_links.append(clean_url)

    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            for name, value in p_attrs:
                if name == "href":
                    self.__insert_external_url(value)

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not helper_method.is_url_base_64(value[1]) and len(self.m_image_url) < 35:
                    # Joining Relative URL
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.endswith("/"):
                        m_temp_base_url = m_temp_base_url + "/"
                    m_url = urljoin(m_temp_base_url, value[1])
                    m_url = helper_method.on_clean_url(helper_method.normalize_slashes(m_url))
                    if any(ext in m_url for ext in ['.jpg', '.jpeg', '.png']):
                        self.m_image_url.append(m_url)

        elif p_tag == 'title':
            self.m_rec = PARSE_TAGS.S_TITLE

        elif p_tag in ['h1', 'h2', 'h3', 'h4']:
            self.__save_section()  # Save accumulated section before starting a new one
            self.m_rec = PARSE_TAGS.S_HEADER

        elif p_tag == 'span' and self.m_paragraph_count == 0:
            self.__save_section()
            self.m_rec = PARSE_TAGS.S_SPAN

        elif p_tag == 'div':
            self.__save_section()  # Save accumulated section when a new div starts
            self.m_rec = PARSE_TAGS.S_DIV

        elif p_tag == 'li':
            self.__save_section()
            self.m_rec = PARSE_TAGS.S_PARAGRAPH

        elif p_tag == 'br':
            self.m_rec = PARSE_TAGS.S_BR

        elif p_tag == 'p':
            self.m_rec = PARSE_TAGS.S_PARAGRAPH
            self.m_paragraph_count += 1

        elif p_tag == 'meta':
            try:
                if p_attrs[0][0] == 'content':
                    if p_attrs[0][1] is not None and len(p_attrs[0][1]) > 50 and p_attrs[0][1].count(" ") > 4 and \
                            p_attrs[0][1] not in self.m_meta_content:
                        self.m_meta_content += p_attrs[0][1]
                if p_attrs[0][1] == 'description':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_meta_description += p_attrs[1][1]
                elif p_attrs[0][1] == 'keywords':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_meta_keyword = ' '.join(dict.fromkeys(p_attrs[1][1].replace(",", " ").split()))

            except Exception:
                pass
        else:
            self.m_rec = PARSE_TAGS.S_NONE

    def handle_endtag(self, p_tag):
        if p_tag == 'p':
            self.m_paragraph_count -= 1
        if self.m_rec != PARSE_TAGS.S_BR:
            self.m_rec = PARSE_TAGS.S_NONE

    def handle_data(self, p_data):
        if self.m_rec == PARSE_TAGS.S_HEADER:
            self.__add_important_description(p_data, False)
        if self.m_rec == PARSE_TAGS.S_TITLE and len(self.m_title) == 0:
            self.m_title = p_data
        elif self.m_rec == PARSE_TAGS.S_META and len(self.m_title) > 0:
            self.m_title = p_data
        elif self.m_rec == PARSE_TAGS.S_PARAGRAPH or self.m_rec == PARSE_TAGS.S_BR:
            self.m_current_section += " " + p_data.strip()
        elif self.m_rec == PARSE_TAGS.S_SPAN and p_data.count(' ') > 5:
            self.m_current_section += " " + p_data.strip()
        elif self.m_rec == PARSE_TAGS.S_DIV:
            if p_data.count(' ') > 5:
                self.m_current_section += " " + p_data.strip()

    # Function to save accumulated sections when a tag change happens
    def __save_section(self):
        section = self.m_current_section.strip()
        section = self.__clean_text(section)
        if section and section.count(" ")>20:
            # Save only non-empty sections
            self.m_sections.append(section)
            self.m_current_section = ""  # Reset the current section

    # Extract names, emails, and phone numbers from the text
    def __extract_names_places_phones_emails(self, text: str):
        text = text.lower()
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('\r', ' ')
        text = text.replace(' ', ' ')

        names = set()
        phone_numbers = set()
        emails = set()

        email_matches = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        emails.update(email_matches)

        doc = nlp_core(text)

        for ent in doc.ents:
            if ent.label_ in {'PERSON', 'GPE', 'ORG'}:
                entity_text = ent.text.strip()

                if entity_text.replace(" ", "").isalpha():
                    if len(entity_text.split()) > 3:
                        for token in ent:
                            if token.pos_ == 'PROPN' and not helper_method.is_stop_word(token):
                                names.add(token.text)
                    else:
                        if all(not helper_method.is_stop_word(token) for token in ent):
                            names.add(entity_text)

        phone_matches = re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)

        for phone in phone_matches:
            phone = re.sub(r'[^\d+]', '', phone)
            try:
                phone_obj = phonenumbers.parse(phone, None)
                if phonenumbers.is_valid_number(phone_obj):
                    phone_numbers.add(phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164))
            except phonenumbers.NumberParseException:
                continue

        return list(names), list(phone_numbers), list(emails)

    # Example function to retrieve sections (for further use)
    def __get_sections(self):
        return self.m_sections

    # Creating keyword request_manager1 for webpage representation
    def __add_important_description(self, p_data, extended_only):
        p_data = " ".join(p_data.split())
        if (p_data.__contains__("java") and p_data.__contains__("script")) or p_data.__contains__("cookies"):
            return

        if (p_data.count(' ') > 2 or (self.m_paragraph_count > 0 and len(p_data) > 0 and p_data != " ")) and p_data not in self.m_important_content:
            self.m_important_content_raw.append(p_data)
            self.m_parsed_paragraph_count += 1

            p_data = re.sub(r'[^A-Za-z0-9 ,;"\]\[/.+-;!\'@#$%^&*_+=]', '', p_data)
            p_data = re.sub(' +', ' ', p_data)
            p_data = re.sub(r'^\W*', '', p_data)

            if p_data.lower() in self.m_important_content.lower():
                return

            if not extended_only:
                try:
                    self.m_important_content = self.m_important_content + " " + spell_checker_handler.get_instance().clean_paragraph(p_data.lower())
                except Exception:
                    pass
                if len(self.m_important_content) > 250:
                    self.m_parsed_paragraph_count = 9

    def __clean_text(self, p_text):
        m_text = p_text.lower()

        for m_important_content_item in self.m_important_content_raw:
            m_text = m_text.replace(m_important_content_item, ' ')

        m_text = m_text.replace('\n', ' ')
        m_text = m_text.replace('\t', ' ')
        m_text = m_text.replace('\r', ' ')
        m_text = m_text.replace(' ', ' ')

        m_text = re.sub(' +', ' ', m_text)
        p_text = m_text.lower()
        m_word_tokenized = p_text.split()
        m_content = []
        word_count = len(m_word_tokenized)

        i = 0
        while i < word_count:
            current_word = m_word_tokenized[i]
            left_context = m_content[-5:]
            right_context = m_word_tokenized[i+1:i+6]
            current_pattern = " ".join(m_word_tokenized[i:i+5])

            if current_word not in left_context and current_word not in right_context:
                if current_pattern not in " ".join(m_content):
                    m_content.append(current_word)

            i += 1

        final_content = ' '.join(m_content)
        return final_content

    def __generate_html(self):
        try:
            # Start the HTML parsing by feeding the HTML content
            self.feed(self.m_html)

            # After feeding the HTML to HTMLParser, use BeautifulSoup for additional text processing
            self.m_soup = BeautifulSoup(self.m_html, "html.parser")
            self.m_content = self.m_soup.get_text()
            self.m_content = self.__clean_text(self.m_content)

        except Exception as ex:
            print(f"Error during HTML parsing: {ex}")

    # ----------------- Data Receivers -----------------

    def __get_title(self):
        return self.__clean_text(helper_method.strip_special_character(self.m_title).strip())

    def __get_meta_description(self):
        meta_tag = self.m_soup.find("meta", {"name": "description"})
        if meta_tag and meta_tag.get("content"):
            return self.__clean_text(meta_tag.get("content"))
        return ""

    def __get_important_content(self):
        m_content = self.m_important_content
        if len(m_content) < 150 and fuzz.ratio(m_content, self.m_meta_description) < 85 and len(
                self.m_meta_description) > 10:
            m_content += self.m_meta_description
        if len(m_content) < 150 and fuzz.ratio(m_content, self.m_non_important_text) < 85 and len(
                self.m_non_important_text) > 10:
            self.__add_important_description(self.m_non_important_text, False)
            m_content += self.m_important_content
        if len(m_content) < 50 and len(self.m_sub_url) >= 3:
            m_content = "- No description found but contains some urls. This website is most probably a search engine or only contain references of other websites - " + self.m_title.lower()

        return helper_method.strip_special_character(m_content)

    def __get_validity_score(self, p_important_content):
        m_rank = (((len(p_important_content) + len(self.m_title)) > 150) or len(self.m_sub_url) >= 3) * 10 + (
                len(self.m_sub_url) > 0 or self.m_all_url_count > 5) * 5

        return m_rank

    def __get_content_type(self):
        try:
            if len(self.m_content) > 0:
                self.m_content_type = topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER, [self.m_title, self.m_important_content, self.m_content])
                if self.m_content_type is None:
                    return CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL

                return self.m_content_type
            return CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
        except Exception as ex:
            return CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL

    def __get_static_file(self):
        return self.m_sub_url[0:10], self.m_image_url, self.m_doc_url, self.m_video_url, self.m_archive_url

    def __get_content(self):
        return self.m_content

    def __get_meta_keywords(self):
        return self.__clean_text(self.m_meta_keyword)

    def parse_html_files(self):
        self.__generate_html()

        m_sub_url, m_images, m_document, m_video, m_archive_url = self.__get_static_file()
        m_title = self.__get_title()
        m_meta_description = self.__get_meta_description()
        m_important_content = self.__clean_text(self.__get_important_content() + " " + m_meta_description)
        m_meta_keywords = self.__get_meta_keywords()
        m_content_type = self.__get_content_type()
        m_content = self.__clean_text(self.__get_content() + " " + m_title + " " + m_meta_description)
        m_validity_score = self.__get_validity_score(m_important_content)
        m_section = self.__get_sections()
        m_names, m_phone_numbers, m_emails = self.__extract_names_places_phones_emails(self.m_soup.get_text(separator=' '))
        m_clearnet_links = self.m_clearnet_links

        return index_model_init(
            m_base_url=self.m_base_url,
            m_url=self.request_model.m_url,
            m_title=m_title,
            m_meta_description=m_meta_description,
            m_content=m_content,
            m_important_content=m_important_content,
            m_images=m_images,
            m_document=m_document,
            m_video=m_video,
            m_sub_url = m_sub_url,
            m_validity_score=m_validity_score,
            m_meta_keywords=m_meta_keywords,
            m_content_type=m_content_type,
            m_section=m_section,
            m_names=m_names,
            m_emails=m_emails,
            m_archive_url=m_archive_url,
            m_phone_numbers=m_phone_numbers,
            m_clearnet_links=m_clearnet_links,
        )
