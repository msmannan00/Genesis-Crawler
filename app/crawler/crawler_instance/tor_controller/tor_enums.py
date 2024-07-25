from crawler.constants.constant import RAW_PATH_CONSTANTS, TOR_CONSTANTS


class TOR_COMMANDS:
    S_START = 1
    S_RESTART = 2
    S_GENERATED_CIRCUIT = 3
    S_RELEASE_SESSION = 4
    S_CREATE_SESSION = 5
    S_PROXY = 6


class TOR_CMD_COMMANDS:
    S_START_DIRECT = RAW_PATH_CONSTANTS.S_SIGWIN_PATH + " " + TOR_CONSTANTS.S_SHELL_CONFIG_PATH + " " + TOR_CONSTANTS.S_TOR_PATH + " " + "build-start-tor"
    S_START_DOCKERISED = "." + TOR_CONSTANTS.S_SHELL_CONFIG_PATH + " " + TOR_CONSTANTS.S_TOR_PATH + " " + "build-start-tor"


class TOR_STATUS:
    S_RUNNING = 1
    S_PAUSE = 2
    S_STOP = 3
    S_READY = 4
    S_START = 5
    S_CLOSE = 6


def generate_proxies(start_ip, start_port, count, port_step=2, control_port_offset=1):
    base_ip = [int(x) for x in start_ip.split('.')]
    proxies = []
    control_proxies = []

    for i in range(count):
        ip = f"172.0.0.{base_ip[3] + i}"
        http_port = start_port + (i * port_step)
        https_port = http_port  # Assuming HTTP and HTTPS ports are the same
        control_port = http_port + control_port_offset

        proxies.append({
            "http": f"socks5h://{ip}:{http_port}",
            "https": f"socks5h://{ip}:{https_port}"
        })

        control_proxies.append({
            "proxy": ip,
            "port": control_port
        })

    return proxies, control_proxies
