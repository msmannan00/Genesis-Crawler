# Local Imports
import os

# ------- Allowed Files --------- #

doc_types = [".pdf", ".msword", ".document", ".docx", "doc"]

# ------- Local Paths --------- #

# OS Directory
m_project_path = "C:\\Workspace\\Genesis-Crawler-Python"

m_cigwin_path = "\\cygwin64\\bin\\bash.exe --login"
m_tor_path = m_project_path + "\\GenesisOnionProxy"

# Local Directory
m_shell_config_path = m_project_path+"\\GenesisCrawlerServices\\raw\\config_script.sh"
m_raw_path = m_project_path+"\\"
m_queue_state_path = m_project_path+"\\CrawlerInstance\\stateManager\\queues_state"
m_duplication_filter_backup_path_1 = m_project_path + "\\CrawlerInstance\\stateManager\\duplication_fiilter_backup_1"
m_duplication_filter_backup_path_2 = m_project_path + "\\CrawlerInstance\\stateManager\\duplication_fiilter_backup_2"
m_prefs_state_path = m_project_path+"\\CrawlerInstance\\stateManager\\prefs_state"
m_dict_path = m_project_path+"\\GenesisCrawlerServices\\raw\\dictionary"
m_dict_small_path = m_project_path+"\\GenesisCrawlerServices\\raw\\dictionary_small"
m_application_controller_path = m_project_path + "\\CrawlerInstance\\applicationController\\applicationController.py"

# Local URL
m_start_url = "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=onion+links"
m_ip_ping_url = r'http://jsonip.com'

# ------- Crawler Settings --------- #

# Total Thread Instances Allowed
m_max_crawler_count = 3

# Time Delay to Invoke New Url Requests
m_icrawler_invoke_delay = 5
m_crawler_invoke_delay = 5

# URL Intensity
m_crawling_url_intensity = 3

# Max Allowed Depth
m_max_crawling_depth = 3

# Max URL Timeout
m_url_timeout = 10
m_header_timeout = 30

# Max Host Queue Size
m_max_host_queue_size = 50

# Max Thread Life
m_max_thread_life = 3600

# Max Allowed Failed URL
m_max_failed_url_allowed = 100

# Max URL Size
m_max_url_size = 480

# Backup Time
m_backup_time_delay = 86400
m_mongoDB_backup_url_fetch_limit = 50
m_mongoDB_index_url_fetch_limit = 1000
restart_crawler_delay = 300

# MongoDB Database
m_mongoDB_database = 'genesis'
m_mongoDB_port = 27017
m_mongoDB_ip = 'localhost'

# New Circuit Time Delay
m_new_circuit_delay = 600

# Min Image Content Size
m_min_content_length = 10000

# Logs
m_max_log_queue_size = 500

# User Agent
m_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'

# Crawl Catagory
m_thread_catagory = "general"

# Repetition Mode
m_thread_repeatable = False

# Filter Mode
m_filter_token = ""
m_filter_type = "soft"
m_filter_catagory = "General"
