from abc import abstractmethod


class requestHandler:

    @abstractmethod
    def invoke_trigger(self, p_command, p_data=None):
        pass
