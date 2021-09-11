from GenesisCrawlerServices.constants.enums import CrawlerStatus, TorStatus

# Application Runtime Status
crawler_status = CrawlerStatus.closed
crawler_name = "c_default"

# External DB Queue Exists And Not Empty
backup_queue_status = True

# Tor Status
tor_status = TorStatus.ready
tor_connection_port = 9052
tor_control_port = 9053
