# Libraries
import atexit
import json
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Perceptron
from sklearn.metrics import recall_score, precision_score, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB

from CrawlerInstance.classModels.IndexModel import UrlObjectEncoder
from CrawlerInstance.duplicationHandlerService.DuplicationHandlerManager import DuplicationHandlerManager
from GenesisCrawler.controllers.crawlerSubprocess import crawlerSubprocess
from GenesisCrawlerServices.classifiers.topicClassifier import topicClassifier
from GenesisCrawlerServices.constants import keys, strings
from GenesisCrawlerServices.constants.enums import CrawlerInterfaceCommands, ErrorMessages, ServerResponse, MongoDBCommands, ProcessStatus
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod
from GenesisCrawlerServices.mongoDBService.mongoDBController import mongoDBController
from GenesisCrawler.controllers.sessionData import sessionData


# python manage.py runserver --insecure
# for /f "tokens=5" %a in ('netstat -aon ^| find "8000"') do taskkill /f /pid %a
# Application Server Entry Point
class ServerController:
    __instance = None
    m_subprocess_list = {}
    m_session_data = {}
    m_thread_last_id = 0

    # Initializations
    @staticmethod
    def getInstance():
        if ServerController.__instance is None:
            ServerController()
        return ServerController.__instance

    def __init__(self):
        if ServerController.__instance is not None:
            raise Exception(ErrorMessages.singleton_exception)
        else:
            ServerController.__instance = self
            atexit.register(self.exit_handler)

    # External Reuqest Callbacks
    def invokeServer(self, p_command, p_data):
        m_data = json.loads(p_data)

        if p_command == CrawlerInterfaceCommands.get_data.value:
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), ServerResponse.response010.value])

        elif p_command == CrawlerInterfaceCommands.clear_data_command.value:
            mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_clear_data_invoke, strings.empty)
            DuplicationHandlerManager.getInstance().clearData()
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), ServerResponse.response004.value])

        elif p_command == CrawlerInterfaceCommands.fetch_title_command.value:
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_get_unique_title,strings.empty_json)])

        elif p_command == CrawlerInterfaceCommands.fetch_thread_catagory_command.value:
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_get_unique_category,strings.empty_json)])

        elif p_command == CrawlerInterfaceCommands.force_stop_command.value:
            m_request = HelperMethod.createJson([keys.m_data,keys.m_command],[strings.empty_json, CrawlerInterfaceCommands.force_stop_command.value])
            self.m_subprocess_list[m_data[keys.m_thread_name]].forcedStop(m_request)
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), ServerResponse.response002.value])

        elif p_command == CrawlerInterfaceCommands.fetch_error_logs_command.value or p_command == CrawlerInterfaceCommands.fetch_info_logs_command.value:
            m_request = HelperMethod.createJson([keys.m_data,keys.m_command],[strings.empty_json, p_command])
            status, m_result = self.m_subprocess_list[m_data[keys.m_thread_name]].write(m_request)
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[json.dumps(json.loads(self.getSessionInfo())), json.loads(m_result)])

        elif p_command == CrawlerInterfaceCommands.create_crawler_instance_command.value:

            # Create Crawlerf
            m_crawl_instance = crawlerSubprocess()
            m_crawl_instance.onStart()
            self.m_thread_last_id += 1

            # Check Name Duplication
            if m_data[keys.m_thread_name] in self.m_subprocess_list.keys():
                m_data[keys.m_thread_name] = m_data[keys.m_thread_name]+"_"+str(self.m_thread_last_id)

            # Saving Crawler
            self.m_subprocess_list[m_data[keys.m_thread_name]] = m_crawl_instance
            self.m_session_data[m_data[keys.m_thread_name]] = sessionData(m_data[keys.m_thread_name], self.m_thread_last_id, m_data[keys.m_max_crawler_count], m_data[keys.m_max_crawling_depth], m_data[keys.m_thread_catagory], m_data[keys.m_thread_repeatable], m_data[keys.m_filter_catagory], m_data[keys.m_filter_type], m_data[keys.m_filter_token])

            # Start Crawler
            m_data = self.appendDefaultSettings(m_data)
            m_request = HelperMethod.createJson([keys.m_data,keys.m_command],[m_data, CrawlerInterfaceCommands.create_command.value])
            m_status, m_crawler_response = m_crawl_instance.write(m_request)
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[self.getSessionInfo(), m_crawler_response])

        else:
            m_request = HelperMethod.createJson([keys.m_data,keys.m_command],[strings.empty_json, p_command])
            status, m_result = self.m_subprocess_list[m_data[keys.m_thread_name]].write(m_request)
            m_response = HelperMethod.createJson([keys.m_session_info,keys.m_result],[json.dumps(json.loads(self.getSessionInfo())), m_result])

        return m_response

    # Helper Methods
    def getSessionInfo(self):
        m_keys = self.m_session_data.keys()
        for m_thread_name in list(m_keys):
            if self.m_subprocess_list[m_thread_name].getProcessStatus() == ProcessStatus.stop or self.m_subprocess_list[m_thread_name].getProcessStatus() == ProcessStatus.terminate:
                del self.m_subprocess_list[m_thread_name]
                del self.m_session_data[m_thread_name]

        return UrlObjectEncoder().encode(self.m_session_data)

    def appendDefaultSettings(self, p_data):
        p_data[keys.m_thread_id] = str(self.m_thread_last_id)
        return p_data

    def exit_handler(self):
        m_keys = self.m_session_data.keys()
        for m_thread_name in list(m_keys):
            m_request = HelperMethod.createJson([keys.m_data,keys.m_command],[strings.empty_json, CrawlerInterfaceCommands.force_stop_command.value])
            print(self.m_subprocess_list[m_thread_name].forcedStop(m_request))

    def train(self):
        # READ COMMENTS
        print("READING...")
        train_data = pd.read_csv("C://Workspace//Genesis-Crawler//GenesisCrawlerServices//classifiers//training_data.csv")
        #train_data = pd.read_csv(constants.m_project_path + constants.m_classifier_path + "training_data.csv")
        print("READING FINISHED... : " + str(train_data.shape))

        # CLEANING
        print("CLEANING...")
        train_data['TEXT'] = train_data['TEXT'].replace(np.nan, '')
        # train_data['TEXT'] = train_data['TEXT'].map(lambda x: re.sub(r'[^A-Za-z ]+', '', x))
        print("CLEANING FINISHED...")

        # READ COMMENTS
        print("SHUFFLING...")
        np.random.shuffle(train_data.values)
        print("SHUFFLING FINISHED...")

        # CREATE VECTORIZER
        print("VECTORIZING...")
        count_vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), stop_words=None)
        transformed_vector = count_vectorizer.fit_transform(train_data["TEXT"].values.astype('U'))
        dataframe = pd.DataFrame(transformed_vector.toarray(), columns=count_vectorizer.get_feature_names())
        print("VECTORIZING FINISHED...")

        # SELECT KBEST
        print("SELECTING...")
        # selector = SelectKBest(score_func=chi2, k=5000)
        # selector.fit(dataframe, train_data["PREDICTION"])
        # extracted_feature = np.asarray(count_vectorizer.get_feature_names())[selector.get_support()]
        # dataframe = dataframe[extracted_feature]
        # self.m_last_log = "SELECTING FINISHED..."
        print("SELECTING FINISHED...")


        # INITIALIZATION
        print("INITIALIZATION...")
        tokens_list = dataframe.columns.values
        print("INITIALIZATION FINISHED...")

        # SPLIT TEST TRAIN
        print("SPLITING...")
        data = dataframe[tokens_list[0:len(tokens_list)]]
        label = train_data["PREDICTION"]
        train_features, test_features, train_labels, test_labels = train_test_split(data, label, test_size=0.2,shuffle=True)
        print("SPLITING FINISHED...")

        # CREATE MODEL
        print("CREATING MODEL...")
        # model = RandomForestClassifier(max_depth=50, random_state=10) # False
        # model = Perceptron(tol=1e-3, random_state=0) # False
        model = MultinomialNB(alpha=1.0, fit_prior=True) # 0.91 - 0.87 - 0.87
        # model = MultinomialHMM(n_components=2, startprob_prior=1.0, transmat_prior=1.0) # False
        # model = MLPClassifier(random_state=1, max_iter=300)
        # model = LinearDiscriminantAnalysis()
        # model = LDA(5)

        print("CREATING MODEL FINISHED...")

        # TRAIN MODEL
        print("TRAINING MODEL...")
        # trainedModel = model.fit(train_features, train_labels)
        trainedModel = OneVsRestClassifier(model).fit(train_features, train_labels)
        print("TRAINING MODEL FINISHED...")

        # PREDICTION
        print("PREDICTING...")
        predictions = trainedModel.predict(test_features)
        print("PREDICTING FINISHED...")

        # SAVING
        print("SAVING MODEL...")
        #pickle.dump(trainedModel, open(constants.m_project_path + constants.m_classifier_pickle_path, 'wb'))
        print("SAVING MODEL FINISHED FINISHED...")

        # SHOW PREDICTIONS
        print("SHOWING PREDICTION...")
        print(sklearn.metrics.accuracy_score(test_labels, predictions))
        print('F1 Score - ', {f1_score(test_labels, predictions, average='macro')})
        print(precision_score(test_labels, predictions, average='macro'))
        print(recall_score(test_labels, predictions, average='macro'))
        print("SHOWING PREDICTION FINISHED...")

        # SHOW ACCURACY
        print("ACCURACY...")
        print(accuracy_score(test_labels, predictions))
        print("ACCURACY FINISHED...")


# ServerController.getInstance().train()
# mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_clear_data_invoke, strings.empty)
# ServerController.getInstance().invokeServer(CrawlerInterfaceCommands.create_crawler_instance_command.value, '{"m_max_crawling_depth":"3","m_max_crawler_count":"15","m_filter_token":"none","m_filter_type":"none","m_filter_catagory":"none","m_thread_catagory":"general","m_thread_repeatable":"false","m_thread_name":"c_default","m_start_url":"http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=onion+links"}')
topicClassifier.getInstance().generateClassifier()
# m_content_type = topicClassifier.getInstance().predictClassifier("money grocery iphone milk eggs")
# print(m_content_type)
# topicClassifier.getInstance().generateClassifier()
# topicClassifier.getInstance().trainModel()
