/*Script Handler*/
class scriptHandler {

   constructor() {
   }

   /*Post Command Handler*/
   postCommand(command, post_data) {

        self.m_last_command = command;
        self.m_request_pending = true;
        const data = strings.command + command + "&" + strings.json_data + post_data;

        const request = new XMLHttpRequest();
        request.open(keys.post, strings.localhost_command_url, true);
        request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        onShowLoading()

        request.onreadystatechange = function() {
            if (this.readyState === 4) {
              if (this.status === 200) {
                  if(self.m_last_command === command){
                      updateResponseContainer(command, request.responseText)
                      self.m_request_pending = request;
                  }
                  onHideLoading()
              }
              else {
                  if(self.m_last_command === command){
                      updateResponseContainer(commands.server_error_command, strings.server_error + this.status)
                      self.m_request_pending = false;
                  }
                  onHideLoading()
              }
            }
        };
        request.onerror = function() {
          console.log(strings.post_error);
        };

        request.send(data);
   }
}

let m_script_handler = new scriptHandler();
let m_request_pending = false;
let m_last_command = "";
/*Event Handler*/
/*User Console Menu*/
function startCrawler() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.start_command, data);
    }
}
function pauseCrawler() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.pause_command, data);
    }
}
function stopCrawler() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.stop_command, data);
    }
}

function forcedStopCrawler() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        helperMethod.createAlert(keys.m_alert_header, keys.m_alert_message,strings.confirmation_header, strings.confirmation_message + "<hr><b>Command : </b><span style='color: red'><b> " + commands.force_stop_command + "<b></span>", keys.m_alert_confirm, true, keys.m_cancel_confirm, function fun() {
            data = JSON.stringify({m_thread_name : m_result[1]});
            m_script_handler.postCommand(commands.force_stop_command, data);
        })
    }
}

function saveCrawler() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.save_command, data);
        updateResponseContainer(commands.save_command, strings.saving_message + this.status)
    }
}

function restartTor() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.restart_tor_command, data);
    }
}

function clearCrawlerData() {
    helperMethod.createAlert(keys.m_alert_header, keys.m_alert_message,strings.confirmation_header, strings.confirmation_message + "<hr><b>Command : </b><span style='color: red'><b> " + commands.clear_data_command + "<b></span>", keys.m_alert_confirm, true, keys.m_cancel_confirm, function fun() {
        m_script_handler.postCommand(commands.clear_data_command, strings.empty_json);
    })
}

/*Data Fetching Handler*/

function fetchUniqueTitle() {
    m_script_handler.postCommand(commands.fetch_title_command, strings.empty_json);
}

function fetchCrawlerCatagories() {
    m_script_handler.postCommand(commands.fetch_thread_catagory_command, strings.empty_json);
}

function fetchSessionData() {
    m_script_handler.postCommand(commands.get_data, strings.empty_json);
}

function fetchThreadInfo() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.info_command, data);
    }
}

function fetchInfoLogs() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.fetch_info_logs_command, data);
    }
}

function fetchErrorLogs() {
    m_result = this.fetchSelectedThreadName()
    if(m_result[0]===true){
        data = JSON.stringify({m_thread_name : m_result[1]});
        m_script_handler.postCommand(commands.fetch_error_logs_command, data);
    }
}

function fetchThreadCreationForm() {
    m_script_handler.postCommand(commands.create_crawler_form_command, strings.empty_json);
}

function fetchSelectedThreadName() {
    m_thread_name = app_status.thread_name
    if(m_thread_name===strings.choose_thread){
        helperMethod.createAlert(keys.m_alert_header, keys.m_alert_message,strings.confirmation_header, strings.no_thread_choosen, keys.m_alert_confirm,false, keys.m_cancel_confirm , function fun() {
        })
        return [false, null]
    }else {
       return [true, m_thread_name]
    }
}

/*Local Update Handler*/
function autoLoader() {
        if(self.m_last_command === commands.fetch_title_command){
            m_script_handler.postCommand(commands.fetch_title_command, strings.empty_json);
        }
        else if(self.m_last_command === commands.fetch_info_logs_command){
            fetchInfoLogs()
        }
}

function updateCrawlerInfo(p_data) {
    data = JSON.parse(p_data); // this will convert your json string to a javascript object

    m_thread_list= document.getElementById(keys.thread_dropdown_container)
    m_keys = Object.keys(data)
    m_count = 0
    m_innerHTML = ""
    app_status.m_thread_catagories = []

    for (m_count; m_count < m_keys.length; m_count++) {
         m_innerHTML += "<li><a class=\"dropdown-item\" id=\"1\" href=\"#\" >" + m_keys[m_count] + "</a></li>"
         if(!app_status.m_thread_catagories.includes(data[m_keys[m_count]].m_thread_catagory)){
             app_status.m_thread_catagories.push(data[m_keys[m_count]].m_thread_catagory)
         }
    }

    if(m_count>0){
        m_thread_list.innerHTML = m_innerHTML
    }else {
        m_thread_list.innerHTML = "<li><a class=\"dropdown-item\" id=\"1\" href=\"#\" >" + strings.choose_thread + "</a></li>"
        $("#thread_dropdown").text(strings.choose_thread);
    }

    updateClickEvents()
}

/*Update Post Response*/
function updateResponseContainer(m_response_command, m_updateResponseContainer) {
    if(m_response_command === commands.create_crawler_form_command){
        m_response_data = m_updateResponseContainer;
        updateClickEvents()
    }
    else {
        m_response_data = strings.empty_str
        m_json = JSON.parse(m_updateResponseContainer);
        m_session_info = m_json.m_session_info;
        m_result = m_json.m_result;
        updateCrawlerInfo(m_session_info)

        if(m_response_command === commands.get_data){
            return false
        }
        else if(m_response_command === commands.fetch_error_logs_command || m_response_command === commands.fetch_info_logs_command){
            m_response_data = m_result;
            if(m_response_data.length <=0){
               m_response_data = "<div class=\"p-3 mb-2 bg-secondary text-white\">" + "List Empty" + "</div>";
            }
            else {
               m_response_html = "<table class=\"table table-striped\" > <thead class=\"table table-striped\"> <tr> <th scope=\"col\">ID</th> <th scope=\"col\">Logs</th></tr></thead> <tbody>";
               m_counter=1
               for (let item of m_response_data) {
                   m_response_html += " <tr> <th scope=\"row\">" + m_counter++ +"</th> <td><span style='color: darkblue;font-weight: bold'>"+item+"</span></td></tr>";
               }
               m_response_html += "</tbody></table>";
               m_response_data = m_response_html;
            }
        }else if(m_response_command === commands.fetch_title_command || m_response_command === commands.fetch_thread_catagory_command){
            m_response_data = m_result;
            if(m_response_data.length <=0){
               m_response_data = "<div class=\"p-3 mb-2 bg-secondary text-white\">" + "List Empty" + "</div>";
            }
            else {
               m_response_html = "<table class=\"table table-striped\" > <thead class=\"table table-striped\"> <tr> <th scope=\"col\">ID</th> <th scope=\"col\">Host</th></tr></thead> <tbody>";
               m_counter=1
               for (let item of m_response_data) {
                   m_response_html += " <tr> <th scope=\"row\">" + m_counter++ +"</th> <td><a href=\""+item+"\">"+item+"</a></td></tr>";
               }
               m_response_html += "</tbody></table>";
               m_response_data = m_response_html;
            }
        }else {
            m_response_data = "<div class=\"p-3 mb-2 bg-secondary text-white\">" + m_result + "</div>";
        }
    }
    const response_container = document.getElementById(keys.response_container_key);
    response_container.innerHTML = m_response_data

    // Post Form Creation Commands

    if(m_response_command === commands.create_crawler_form_command){
        loadCreationForm();
    }

}

function onShowLoading(){
    $("#m_loading").fadeIn(250);
}

function onHideLoading(){
    if(self.m_last_command !== commands.fetch_title_command && self.m_last_command !== commands.fetch_info_logs_command){
        $("#m_loading").fadeOut(250);
    }
}

/*Helper Method*/

function updateTokenType(p_type){
    m_filter_token_type = document.getElementById(keys.m_filter_token_type)
    m_filter_token_type.innerText = p_type
}

function updateFilterType(p_type){
    m_filter_catagory = document.getElementById(keys.m_filter_catagory)
    m_filter_catagory.innerText = p_type
}

function loadCreationForm(){
    m_thread_catagories_defined = document.getElementById(keys.catagories_defined)
    m_thread_catagories_defined.innerHTML = ""
    for (let item of app_status.m_thread_catagories) {
        m_thread_catagories_defined.innerHTML += '<a class="dropdown-item" href="#" onClick="onSelectThreadCustomCatagory(\'' + item + '\')"> ' + item + ' </a>'
    }
}

function onSelectThreadCustomCatagory(p_catagory){
    m_thread_catagories = document.getElementById(keys.m_thread_catagory_id)
    m_thread_catagories.value = p_catagory
}

function validateThreadCreateForm(m_form) {
    m_error_label = document.getElementById(keys.m_error_label)
    m_error_container = document.getElementById(keys.m_error_container)
    if(m_form.m_max_crawling_depth.value === strings.empty_str || m_form.m_max_crawler_count.value === strings.empty_str || m_form.m_thread_name.value === strings.empty_str || m_form.m_start_url.value === strings.empty_str || m_form.m_thread_catagory.value === strings.empty_str){
        m_error_label.innerHTML = strings.form_empty
        m_error_container.style.opacity = "1";
    }else {
        helperMethod.createAlert(keys.m_alert_header, keys.m_alert_message,strings.confirmation_header, strings.confirmation_message + "<hr><b>Command : </b><span style='color: red'><b> " + commands.create_crawler_instance_command + "<b></span>", keys.m_alert_confirm, true, keys.m_cancel_confirm ,function fun() {
            data = JSON.stringify({m_max_crawling_depth : m_form.m_max_crawling_depth.value, m_max_crawler_count: m_form.m_max_crawler_count.value,m_thread_repeatable: (m_form.m_thread_repeatable.checked ? 1 : 0) ,m_thread_catagory: m_form.m_thread_catagory.value,m_thread_name: m_form.m_thread_name.value, m_start_url: encodeURIComponent(m_form.m_start_url.value), m_filter_token: m_form.m_filter_token.value, m_filter_catagory: m_form.m_filter_catagory.value, m_filter_type: m_form.m_filter_token_type.value});
            m_script_handler.postCommand(commands.create_crawler_instance_command, data);
        })
    }
    return false
}

function onLoad(){
    fetchSessionData();
    onHideLoading()
    setInterval(autoLoader, 3000);
}

/*JQuery Static Commands*/

function updateClickEvents(){
    $(".dropdown-menu li a").click(function(){
        app_status.thread_name = $(this).text()
        $("#thread_dropdown").text($(this).text());
    });
}

$(document).ready(function(){
    updateClickEvents()
});
