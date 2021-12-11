class shared_constants:
    S_PROJECT_PATH = "C:\\Workspace\\Genesis-Crawler"

class mongo_constants:
    S_DATABASE_NAME = 'genesis'
    S_DATABASE_PORT = 27017
    S_DATABASE_IP = 'localhost'

class spell_check_constants:
    S_SPELL_CHECK_LANGUAGE = "english"
    S_DICTIONARY_PATH = shared_constants.S_PROJECT_PATH + "\\genesis_crawler_services\\raw\\dictionary"
    S_DICTIONARY_MINI_PATH = shared_constants.S_PROJECT_PATH + "\\genesis_crawler_services\\raw\\dictionary_small"

class classifier_constants:
    S_CLASSIFIER_FOLDER_PATH = "\\genesis_crawler_services\\raw\\classifier_output"
    S_CLASSIFIER_PICKLE_PATH = "\\genesis_crawler_services\\raw\\classifier_output\\web_classifier.sav"
    S_VECTORIZER_PATH = "\\genesis_crawler_services\\raw\\classifier_output\\class_vectorizer.csv"
    S_SELECTKBEST_PATH = "\\genesis_crawler_services\\raw\\classifier_output\\feature_vector.sav"
    S_TRAINING_DATA_PATH = "\\genesis_crawler_services\\raw\\classifier_output\\training_data.csv"

