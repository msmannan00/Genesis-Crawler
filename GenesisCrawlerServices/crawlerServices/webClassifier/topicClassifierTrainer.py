import os
import os.path
import re
import shutil

import numpy as np
import sklearn
import pickle
import pandas as pd

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from GenesisCrawlerServices.constants import constants, strings
from GenesisCrawlerServices.constants.enums import MONGODB_COMMANDS, TOPIC_CLASSFIER_TRAINER
from GenesisCrawlerServices.helperServices.spellCheckerHandler import spell_checker_handler
from GenesisCrawlerServices.sharedModel.requestHandler import RequestHandler
from GenesisCrawlerServices.crawlerServices.mongoDB.mongoController import mongo_controller


class topicClassifierTrainer(RequestHandler):

    def __init__(self):
        pass

    def __generate_classifier(self):
        self.__init_dict()
        self.__clear_existing_data()
        self.__read_dataset()
        self.__train_model()
        pass

    def __init_dict(self):
        spell_checker_handler.get_instance().init_dict()

    def __clear_existing_data(self):
        if os.path.isdir(constants.S_PROJECT_PATH + constants.S_CLASSIFIER_FOLDER_PATH):
            shutil.rmtree(constants.S_PROJECT_PATH + constants.S_CLASSIFIER_FOLDER_PATH)
        os.mkdir(constants.S_PROJECT_PATH + constants.S_CLASSIFIER_FOLDER_PATH)

    def __read_dataset(self):
        m_result = mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_GET_PARSE_URL, None)

        if Path(constants.S_PROJECT_PATH + constants.S_TRAINING_DATA_PATH).exists():
            os.remove(constants.S_PROJECT_PATH + constants.S_TRAINING_DATA_PATH)

        m_url_list = ["url,description,title,keywords,prediction"]
        for m_service in m_result:
            m_url = self.__clean_data(m_service['m_url'])
            m_description = self.__clean_data(m_service['m_description'])
            m_title = self.__clean_data(m_service['m_title'])
            m_keyword = self.__clean_data(' '.join(m_service['m_keyword']))
            m_content_type = m_service['m_content_type']

            if m_url == strings.S_EMPTY:
                m_url = "None"
            if m_description == strings.S_EMPTY:
                m_description = "None"
            if m_title == strings.S_EMPTY:
                m_title = "None"
            if m_keyword == strings.S_EMPTY:
                m_keyword = "None"
            if m_content_type == strings.S_EMPTY:
                m_content_type = "None"

            m_item = m_url + "," + m_description + "," + m_title + "," + m_keyword + "," + m_content_type
            m_url_list.append(m_item)

        m_count = 0
        with open(constants.S_PROJECT_PATH + constants.S_TRAINING_DATA_PATH, 'w', encoding="utf-8") as f:
            for item in m_url_list:
                if m_count < len(m_url_list) - 1:
                    f.write("%s\n" % item)
                else:
                    f.write("%s" % item)
                m_count += 1

    def __clean_data(self, p_text):
        # New Line and Tab Remover
        p_text = p_text.replace('\\n', ' ')
        p_text = p_text.replace('\\t', ' ')
        p_text = p_text.replace('\\r', ' ')

        # Tokenizer
        word_list = p_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        incorrect_word, correct_word = spell_checker_handler.get_instance().validation_handler(word_list)

        if len(correct_word)>3:
            return ' '.join(correct_word)
        else:
            return ' '.join(correct_word)

    def __train_model(self):

        # READ COMMENTS
        print("READING...")
        m_dataframe = pd.read_csv(constants.S_PROJECT_PATH + constants.S_TRAINING_DATA_PATH)
        m_dataframe.dropna(inplace=True)
        label = m_dataframe["prediction"]
        print("READING FINISHED...")

        if len(m_dataframe)<=0:
            print("DATASET EMPTY")
            return

        # CLEANING
        print("CLEANING...")
        m_dataframe['description'] = m_dataframe['description'].replace(np.nan, '')
        m_dataframe['description'] = m_dataframe['description'].map(lambda x: re.sub(r'[^A-Za-z ]+', '', x))
        m_dataframe['title'] = m_dataframe['title'].replace(np.nan, '')
        m_dataframe['title'] = m_dataframe['title'].map(lambda x: re.sub(r'[^A-Za-z ]+', '', x))
        print("CLEANING FINISHED...")

        # READ COMMENTS
        print("SHUFFLING...")
        np.random.shuffle(m_dataframe.values)
        print("SHUFFLING FINISHED...")

        print("VECTORIZING...")
        vectorizer = TfidfVectorizer()

        vectorizer.fit(m_dataframe['keywords'])
        X = vectorizer.transform(m_dataframe['keywords'])
        pickle.dump(vectorizer, open(constants.S_PROJECT_PATH + constants.S_VECTORIZER_PATH, "wb"))
        m_keyword = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())

        X = vectorizer.transform(m_dataframe['title'])
        m_title = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())
        m_title *= 2

        X = vectorizer.transform(m_dataframe['description'])
        m_description = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())
        m_description *= 1.5

        m_dataframe = m_title + m_description + m_keyword
        print("VECTORIZING FINISHED...")

        # SELECT KBEST
        print("SELECTING...")
        X = m_dataframe.loc[:, m_dataframe.columns != 'prediction']
        Y = label
        m_select = SelectKBest(chi2, k=2)
        m_select.fit(X, Y)
        pickle.dump(m_select, open(constants.S_PROJECT_PATH + constants.S_SELECTKBEST_PATH, 'wb'))
        X = m_select.transform(X)
        print("SELECTING FINISHED...")

        # SPLIT TEST TRAIN
        print("SPLITING...")
        train_features, test_features, train_labels, test_labels = train_test_split(X, Y, test_size=0.2,shuffle=True)
        print("SPLITING FINISHED...")

        # CREATE MODEL
        print("CREATING MODEL...")
        # sharedModel = RandomForestClassifier(max_depth=150, random_state=10) # False
        # sharedModel = Perceptron(tol=1e-3, random_state=0) # False
        # sharedModel = LogisticRegression(random_state=0)
        # sharedModel = SVC(gamma='auto')
        model = MultinomialNB(alpha=1.0, fit_prior=True) # 0.91 - 0.87 - 0.87
        # sharedModel = MultinomialHMM(n_components=2, startprob_prior=1.0, transmat_prior=1.0) # False
        # sharedModel =  MLPClassifier(random_state=1, max_iter=300)
        # sharedModel = LDA(5)
        print("CREATING MODEL FINISHED...")

        # TRAIN MODEL
        print("TRAINING MODEL...")
        trainedModel = model.fit(train_features, np.ravel(train_labels))
        print("TRAINING MODEL FINISHED...")

        # PREDICTION
        print("PREDICTING...")
        predictions = trainedModel.predict(test_features)
        print("PREDICTING FINISHED...")

        # SAVING
        print("SAVING MODEL...")
        pickle.dump(trainedModel, open(constants.S_PROJECT_PATH + constants.S_CLASSIFIER_PICKLE_PATH, 'wb'))
        print("SAVING MODEL FINISHED FINISHED...")

        # SHOW PREDICTIONS
        print("SHOWING PREDICTION...")
        print("PREFORMANCE SCORE (ACCURACY) : ", sklearn.metrics.accuracy_score(test_labels, predictions))
        print("PREFORMANCE SCORE (F1 SCORE) : ", {f1_score(test_labels, predictions, average='macro')})
        print("PREFORMANCE SCORE (PERCISION) : ", str(precision_score(test_labels, predictions, average='macro')))
        print("PREFORMANCE SCORE (RECALL) : ", str(recall_score(test_labels, predictions, average='macro')))
        print("SHOWING PREDICTION FINISHED...")

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_TRAINER.S_GENERATE_CLASSIFIER:
            self.__generate_classifier()
        if p_command == TOPIC_CLASSFIER_TRAINER.S_CLEAN_DATA:
            self.__clean_data(p_data[0])
