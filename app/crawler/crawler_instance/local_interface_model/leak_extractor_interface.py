from abc import abstractmethod, ABC
from typing import Tuple, List, Set
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model

class leak_extractor_interface(ABC):
    @abstractmethod
    def parse_leak_data(self, html_content: str, p_data_url:str) -> Tuple[leak_data_model, Set[str]]:
        """Parse leak data from HTML content and return a tuple of leak_data_model and a set of sub-links."""
        pass

    @abstractmethod
    def extract_cards(self, url:str) -> List[card_extraction_model]:
        """Extract card data from the HTML content and return a list of card_extraction_model objects."""
        pass

    @abstractmethod
    def extract_sub_links(self) -> Set[str]:
        """Extract sub-links from the HTML content and return a set of strings."""
        pass

    @abstractmethod
    def contact_page(self) -> str:
        """Return the contact page URL as a string."""
        pass
