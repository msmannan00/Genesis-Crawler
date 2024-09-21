import pandas as pd
from transformers import pipeline
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_MODEL, TOPIC_CLASSFIER_MESSAGES
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class topic_classifier_model(request_handler):

    def __init__(self):
        self.classifier = pipeline("text-classification", model="unitary/toxic-bert")

    def __predict_classifier(self, p_title, p_description, p_keyword):
        input_text = p_title + p_description + p_keyword

        if not input_text.strip():
            return CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL

        prediction = self.classifier(input_text)

        predicted_label = prediction[0]['label']

        if prediction[0]['score'] > 0.45:
            return predicted_label
        else:
            return CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_MODEL.S_PREDICT_CLASSIFIER:
            return self.__predict_classifier(p_data[0], p_data[1], p_data[2])