import enum

# HTML Parsing Manager
from CrawlerInstance.constants import constants

class ApplicationResponse(enum.Enum):
    response001 = "Stopping Crawler Instance"
    response002 = "Saving Successfull"
    response003 = "Forced Stopped Crawler Instance"


class ServerResponse(enum.Enum):
    response001 = "Successfully Started Crawler"
    response002 = "Successfully Stopped Crawler"
    response003 = "Successfully Paused Crawler"
    response004 = "Successfully Cleared Data"
    response005 = "Successfully Saved Crawler"
    response006 = "Successfully Resume Crawler"
    response007 = "Crawler Already Running"
    response008 = "Successfully Restarted Tor"
    response009 = "Creating Backup Please Wait"
    response010 = "Sending Thread Data"
    response011 = "Crawler Created Successfully"
    response012 = "Crawler has Stopped Working | Might Be Cause Of Error"
    response013 = "Crawler is Busy Handling Previous Request"

class ErrorMessages(enum.Enum):
    singleton_exception = "This class is a singleton"
    critical_exception_crawl = "Critical Error : Crawl"
    critical_exception_icrawl = "Critical Error ICrawl: "
    database_error_fetch = "Database Load Error : Fetch Failed"


class InfoMessages(enum.Enum):
    loaded_backup_URL = "Loaded Backup URL"
    backup_queue_empty = "Backup Queue Empty"
    generating_new_circuit = "Generating new circuit"
    your_ip = "Your IP is"


class ParserTags(enum.Enum):
    title = 1
    meta = 2
    keyword = 3
    header = 4
    paragraph = 5
    none = -1


# Crawler URL Rule - Extract Url From HTML Text
class CrawlURLIntensity(enum.Enum):
    low = 1
    medium = 2
    high = 3


# Database Interaction stats
class DatabaseCommand(enum.IntEnum):
    url_queue = 1
    url_parse = 2
    url_get_backup = 3


# External Stats - Post Commands
class CrawlerInterfaceCommands(enum.Enum):
    info_command = "genesis : info-application"
    start_command = "genesis : start-application"
    pause_command = "genesis : pause-application"
    stop_command = "genesis : stop-application"
    save_command = "genesis : save-application"
    create_command = "genesis : create-application"
    clear_command = "genesis : clear-application"
    run_command = "genesis : run-application"
    clear_data_command = 'genesis : clear-data'
    get_data = 'genesis : get_data'
    fetch_title_command = 'genesis : fetch-title'
    fetch_thread_catagory_command = 'genesis : fetch-thread-catagory-command'
    force_stop_command = 'genesis : force-stop'
    restart_tor_command = 'genesis : restart_tor'
    create_crawler_form_command = 'genesis : create-crawler-form'
    create_crawler_instance_command = 'genesis : create-crawler-instance'
    stop_content_classifier_generation = 'genesis : stop-content-classifier-generation'
    train_content_classifier = 'genesis : train-content-classifier'
    train_content_classifier_description = 'genesis : train-content-classifier-description'
    fetch_info_logs_command = "genesis : info-logs-application"
    fetch_error_logs_command = "genesis : error-logs-application"


# External Stats - Process Status
class ProcessStatus(enum.Enum):
    sleep = 0
    running = 1
    pause = 2
    stop = 3
    waiting = 4
    backing = 5
    terminate = 6


# External Stats - Crawler Status
class CrawlerStatus(enum.Enum):
    closed = 0
    running = 1
    pause = 2
    stop = 3
    backing = 4


# Keyword Score
class KeywordScore(enum.IntEnum):
    keyword = 3,
    title = 3,
    description = 1,
    none = 0


# External Stats - Tor Commands
class TorCommands(enum.Enum):
    start_command = 1
    pause_command = 2
    stop_command = 3
    restart_command = 3
    generate_circuit_command = 4


# External Stats - Tor Commands
class TorCommandsCMD(enum.Enum):
    start_command = constants.m_cigwin_path + " " + constants.m_shell_config_path + " " + constants.m_tor_path + " " + "build-start-tor"


# External Stats - Tor Status
class TorStatus(enum.Enum):
    running = 1
    pause = 2
    stop = 3
    ready = 4
    starting = 5
    closed = 6


# External Stats - Mongodb Commands
class MongoDBCommands(enum.Enum):
    mongoDB_clear_data = '-1'
    mongoDB_clear_data_invoke = '0'
    mongoDB_save_backup_url = '1'
    mongoDB_save_parse_url = '2'
    mongoDB_get_backup_url = '3'
    mongoDB_get_unique_title = '4'
    mongoDB_save_raw_url = '5'
    mongoDB_get_unique_category = '6'
    mongoDB_get_parsed_url = '7'
