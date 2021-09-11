import pickle

import pandas

from GenesisCrawlerServices.constants import constants, strings
from os import path


class topicClassifierModel:
    m_classifier_model = None
    m_classifier_vectorizer = None
    m_classifier_features = None
    m_last_log = strings.empty

    def __init__(self):
        pass

    def loadModel(self):
        if path.exists(constants.m_project_path + constants.m_classifier_pickle_path):
            self.m_classifier_model = pickle.load(open(constants.m_project_path + constants.m_classifier_pickle_path, 'rb'))
            self.m_classifier_vectorizer = pickle.load(open(constants.m_project_path + constants.m_vectorizer_pickle_path, 'rb'))
            self.m_classifier_features = pickle.load(open(constants.m_project_path + constants.m_features_pickle_path, 'rb'))

    def predictClassifier(self, p_text):
        if self.m_classifier_model is None or self.m_classifier_vectorizer is None or self.m_classifier_features is None:
            return None

        # PREPROCESS OF INPUT
        data = {'TEXT': [p_text]}
        temp_train_data = pandas.DataFrame(data, columns=['TEXT'])
        transformed_vector = self.m_classifier_vectorizer.transform(temp_train_data["TEXT"].values.astype('U'))
        transformed_dataframe = pandas.DataFrame(transformed_vector.toarray(), columns=self.m_classifier_vectorizer.get_feature_names())
        transformed_dataframe = transformed_dataframe[self.m_classifier_features]
        predictions = self.m_classifier_model.predict(transformed_dataframe)
        return predictions
