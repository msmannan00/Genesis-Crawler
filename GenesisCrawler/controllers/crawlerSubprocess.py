import os
import signal
import subprocess
import threading
import time

from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import ProcessStatus, ServerResponse


class crawlerSubprocess:

    # Initializations
    def __init__(self):
        self.process = None
        self.read_input = strings.empty
        self.process_status = ProcessStatus.sleep

    def onStart(self):
        m_crawl_thread = threading.Thread(target=self.run, args=[])
        m_crawl_thread.start()
        time.sleep(0.5)

    def run(self):
        self.process = subprocess.Popen(strings.python + strings.space + constants.m_application_controller_path, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.read()

    # Message Listener
    def read(self):
        self.process_status = ProcessStatus.running
        while True:
            nextline = self.process.stdout.readline().decode(strings.utf_8)
            m_fetch_line = str(nextline.replace(strings.linebreak, strings.empty))
            if self.process_status == ProcessStatus.terminate:
                break
            if nextline == strings.empty:
                self.process_status = ProcessStatus.stop
                break
            elif m_fetch_line[0] != '#':
                print(m_fetch_line)
                continue
            else:
                self.process_status = ProcessStatus.running
                self.read_input = m_fetch_line[2:-1]
                print(self.read_input)

        output, error = self.process.communicate()
        print(output, error)

    # Message Sender
    def write(self, m_request):
        if self.process_status == ProcessStatus.running:
            self.process_status = ProcessStatus.waiting
            self.read_input = strings.empty
            self.process.stdin.write(str.encode(m_request + strings.linebreak))
            self.process.stdin.flush()
            while self.process_status == ProcessStatus.waiting:
                continue

        if str(self.read_input) == str(ServerResponse.response002.value):
            self.process_status = ProcessStatus.stop
            return ProcessStatus.stop, ServerResponse.response002.value
        elif self.process_status == ProcessStatus.stop:
            return self.process_status, ServerResponse.response012.value
        elif self.process_status == ProcessStatus.waiting:
            return self.process_status, ServerResponse.response013.value
        else:
            return self.process_status, self.read_input

    # Helper Methods
    def forcedStop(self, m_request):
        self.process_status = ProcessStatus.terminate
        self.read_input = strings.empty
        self.process.stdin.write(str.encode(m_request + strings.linebreak))
        self.process.stdin.flush()

        os.system('taskkill /pid ' + str(self.process.pid) + ' /T /F')
        return ServerResponse.response002.value

    def getProcessStatus(self):
        return self.process_status

    def getLog(self):
        return self.read_input
