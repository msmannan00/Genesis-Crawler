
class log:

    __instance = None

    # Initializations
    @staticmethod
    def g():
        if log.__instance is None:
            log()
        return log.__instance

    def __init__(self):
        log.__instance = self

    # Info Logs
    def i(self, p_log):
        print(p_log)

    # Error Logs
    def e(self, p_log):
        print(p_log)
