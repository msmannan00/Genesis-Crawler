import os
import pickle

import pandas as pd

from GenesisCrawlerServices.constants import constants
from GenesisCrawlerServices.constants.enums import TOPIC_CLASSFIER_MODEL
from GenesisCrawlerServices.sharedModel.requestHandler import RequestHandler


class TopicClassifierModel(RequestHandler):

    def __init__(self):
        self.__m_vectorizer = None
        self.__m_feature_selector = None
        self.__m_classifier = None
        self.__m_classifier_trained = False

    def __classifier_exists(self):
        if self.__m_classifier_trained is not True:
            if os.path.exists(constants.S_PROJECT_PATH + constants.S_VECTORIZER_PATH) is True and \
               os.path.exists(constants.S_PROJECT_PATH + constants.S_SELECTKBEST_PATH) is True and \
               os.path.exists(constants.S_PROJECT_PATH + constants.S_TRAINING_DATA_PATH) is True:
                self.__m_classifier_trained = True
                self.__load_classifier()
                return True
            else:
                return False
        else:
            return True

    def __load_classifier(self):
        self.__m_vectorizer = pickle.load(open(constants.S_PROJECT_PATH + constants.S_VECTORIZER_PATH, 'rb'))
        self.__m_feature_selector = pickle.load(open(constants.S_PROJECT_PATH + constants.S_SELECTKBEST_PATH, 'rb'))
        self.__m_classifier = pickle.load(open(constants.S_PROJECT_PATH + constants.S_CLASSIFIER_PICKLE_PATH, 'rb'))

    def __predict_classifier(self, p_title,p_description, p_keyword):
        m_status = self.__classifier_exists()
        if m_status is True:
            m_title = pd.Series([p_title])
            m_description = pd.Series([p_description])
            m_keyword = pd.Series([p_keyword])

            m_title_vectorizer_data = self.__m_vectorizer.transform(m_title.values.astype('U'))
            m_description_vectorizer_data = self.__m_vectorizer.transform(m_description.astype('U'))
            m_keyword_vectorizer_data = self.__m_vectorizer.transform(m_keyword.astype('U'))

            m_title_vectorized = pd.DataFrame(m_title_vectorizer_data.toarray(), columns=self.__m_vectorizer.get_feature_names())
            m_description_vectorized = pd.DataFrame(m_description_vectorizer_data.toarray(), columns=self.__m_vectorizer.get_feature_names())
            m_keyword_vectorized = pd.DataFrame(m_keyword_vectorizer_data.toarray(), columns=self.__m_vectorizer.get_feature_names())

            m_dataframe = m_title_vectorized + m_description_vectorized + m_keyword_vectorized
            X = self.__m_feature_selector.transform(m_dataframe)

            m_predictions = self.__m_classifier.predict(X)
            return m_predictions
        else:
            print("CLASSIFIER NOT TRAINIED")

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_MODEL.S_PREDICT_CLASSIFIER:
            return self.__predict_classifier(p_data[0], p_data[1], p_data[2])
