from typing import List, Set, Optional
from pydantic import BaseModel, Field
from crawler.crawler_instance.helper_services.web_request_handler import webRequestManager
from app.crawler.crawler_instance.local_shared_model.index_model import index_model
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model


class leak_data_model(BaseModel):
  cards_data: List[card_extraction_model] = Field(default_factory=list)
  contact_link: str
  base_url: str


class file_parse_manager:
  def __init__(self):
    self.processed_urls: Set[str] = set()
    self.web_request_manager = webRequestManager()

  def parse_generic_files(self, model: index_model) -> index_model:
    """
        Process the index_model by removing duplicates and validating URLs.
        Updates the model's m_document, m_video, and m_images fields with validated URLs.
        Only removes duplicate URLs in the current model context.
        """
    model.m_document = self.__remove_duplicate_urls(model.m_document)
    model.m_video = self.__remove_duplicate_urls(model.m_video)
    model.m_images = self.__remove_duplicate_urls(model.m_images)

    model.m_document = self.__validate_and_filter_urls(model.m_document)
    model.m_video = self.__validate_and_filter_urls(model.m_video)
    model.m_images = self.__validate_and_filter_urls(model.m_images)

    return model

  def parse_leak_files(self, model: leak_data_model) -> leak_data_model:
    """
        Process the leak_data_model by removing duplicates and validating URLs.
        Updates the model's card data fields with validated URLs.
        Only removes duplicate URLs in the current model context.
        """
    for card in model.cards_data:
      card.m_weblink = self.__remove_duplicate_urls(card.m_weblink)
      card.m_url = self.__remove_duplicate_urls(card.m_url)
      card.m_dumplink = self.__remove_duplicate_urls(card.m_dumplink)

      card.m_weblink = self.__validate_and_filter_urls(card.m_weblink)
      card.m_url = self.__validate_and_filter_urls(card.m_url)
      card.m_dumplink = self.__validate_and_filter_urls(card.m_dumplink)

    return model

  def __remove_duplicate_urls(self, urls: Optional[List[str]]) -> List[str]:
    """
        Remove duplicate URLs from a list in the context of a single request.
        """
    if urls is None:
      return []

    seen = set()
    unique_urls = []
    for url in urls:
      if url not in seen:
        seen.add(url)
        unique_urls.append(url)
    return unique_urls

  def __validate_and_filter_urls(self, urls: Optional[List[str]]) -> List[str]:
    """
        Validate URLs using HEAD requests to check if they are accessible.
        Returns a list of valid URLs only.
        """
    if urls is None:
      return []

    valid_urls = []

    for url in urls:
      url = helper_method.on_clean_url(url)
      if url in self.processed_urls:
        valid_urls.append(url)
        continue

      self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])
      is_valid, _ = self.web_request_manager.load_header(url, self.__m_proxy)

      if is_valid:
        valid_urls.append(url)
        self.processed_urls.add(url)

    return valid_urls
