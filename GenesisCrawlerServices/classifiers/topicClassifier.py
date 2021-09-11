# Local Imports
from GenesisCrawlerServices.classifiers.topicClassifierModel import topicClassifierModel
from GenesisCrawlerServices.classifiers.topicClassifierTrainer import topicClassifierTrainer

class topicClassifier:
    __instance = None
    m_classifier_trainer = None
    m_classifier = None
    m_generator_thread = None

    # Initializations
    @staticmethod
    def getInstance():
        if topicClassifier.__instance is None:
            topicClassifier()
        return topicClassifier.__instance

    def __init__(self):
        topicClassifier.__instance = self
        self.m_classifier_trainer = topicClassifierTrainer()
        self.m_classifier = topicClassifierModel()

    def generateClassifier(self):
        # self.m_classifier_trainer.generateClassifier()
        self.initialize()
        # print("FUCK : " + str(self.predictClassifier("hello how are you")))

    def initialize(self):
        self.m_classifier.loadModel()

    def predictClassifier(self, p_text):
        return self.m_classifier.predictClassifier(p_text)
