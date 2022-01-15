# Local Imports
from crawler.crawler_instance.constants.strings import STRINGS
from crawler.crawler_services.crawler_services.content_duplication_manager.content_duplication_enums import CONTENT_DUPLICATION_MANAGER
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class content_duplication_controller_local(request_handler):

    __m_duplication_content_handler = None

    # Initializations

    def __init__(self):
        self.__m_duplication_content_handler = duplication_handler()

    def __verify_content_duplication(self, p_title, p_description, p_content_type):
        if p_title is None:
            p_title = STRINGS.S_EMPTY
        if p_description is None:
            p_description = STRINGS.S_EMPTY
        if p_content_type is None:
            p_content_type = STRINGS.S_EMPTY

        m_duplicate_content_string = p_title + "-" + p_description + "-" + p_content_type
        if self.__m_duplication_content_handler.validate_duplicate(m_duplicate_content_string) is False:
            return False
        else:
            return True

    def __on_insert_content(self, p_title, p_description, p_content_type):
        if p_title is None:
            p_title = STRINGS.S_EMPTY
        if p_description is None:
            p_description = STRINGS.S_EMPTY
        if p_content_type is None:
            p_content_type = STRINGS.S_EMPTY

        m_duplicate_content_string = p_title + "-" + p_description + "-" + p_content_type
        self.__m_duplication_content_handler.insert(m_duplicate_content_string)

    def __on_reset(self):
        self.__m_duplication_content_handler.clear_filter()

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CONTENT_DUPLICATION_MANAGER.S_VALIDATE:
            return self.__verify_content_duplication(p_data[0], p_data[1], p_data[2])
        if p_command == CONTENT_DUPLICATION_MANAGER.S_INSERT:
            return self.__on_insert_content(p_data[0], p_data[1], p_data[2])
        if p_command == CONTENT_DUPLICATION_MANAGER.S_RESET:
            return self.__on_reset()
