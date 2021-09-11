class sessionData:
    def __init__(self, p_thread_name, p_thread_id, p_max_crawler_count, p_max_crawling_depth, p_thread_catagory, p_thread_repeatable, p_filter_catagory, p_filter_token_type, p_filter_token):
        self.m_thread_name = p_thread_name
        self.m_thread_id = p_thread_id
        self.m_thread_catagory = p_thread_catagory
        self.m_max_crawler_count = p_max_crawler_count
        self.m_max_crawling_depth = p_max_crawling_depth
        self.m_thread_repeatable = p_thread_repeatable
        self.m_filter_catagory = p_filter_catagory
        self.m_filter_token_type = p_filter_token_type
        self.m_filter_token = p_filter_token
