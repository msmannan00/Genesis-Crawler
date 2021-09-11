const application_status = {
    START: 0,
    PAUSE: 1,
    STOP: 2,
    SAVE: 3,
    CLEAR: 4,
    RUN: 5
}
const commands = {
    start_command : "genesis : start-application",
    pause_command : "genesis : pause-application",
    stop_command : "genesis : stop-application",
    save_command : "genesis : save-application",
    restart_tor_command : "genesis : restart_tor",
    info_command : "genesis : info-application",
    get_data : 'genesis : get_data',
    clear_command : "genesis : clear-application",
    run_command : "genesis : run-application",
    clear_data_command : 'genesis : clear-data',
    fetch_title_command : 'genesis : fetch-title',
    fetch_thread_catagory_command : 'genesis : fetch-thread-catagory-command',
    server_error_command : 'genesis : server-error',
    create_crawler_form_command : 'genesis : create-crawler-form',
    force_stop_command : 'genesis : force-stop',
    fetch_info_logs_command : "genesis : info-logs-application",
    fetch_error_logs_command : "genesis : error-logs-application",
    create_crawler_instance_command : 'genesis : create-crawler-instance'
}