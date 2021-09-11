import os
import os.path
import re
import numpy as np
import sklearn
import shutil
import pickle
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from GenesisCrawlerServices.constants import constants, strings
from GenesisCrawlerServices.helperService.SpellCheckHandler import SpellCheckHandler
from tkinter import Tcl
from os import path


class topicClassifierTrainer:
    m_classifier = None
    m_open_vpn = None
    m_last_log = strings.empty
    m_catagories = {'1':'Biological Physics','2':'Accelerator Physics','3':'Emerging Technologies','4':'Spectral Theory','5':'Strongly Correlated Electrons','6':'Cellular Automata and Lattice Gases','7':'Metric Geometry','8':'Hardware Architecture','9':'Computer Vision and Pattern Recognition','10':'Programming Languages','11':'Cosmology and Nongalactic Astrophysics','12':'Image and Video Processing','13':'Category Theory','14':'Neural and Evolutionary Computing','15':'Distributed, Parallel, and Cluster Computing','16':'Data Analysis, Statistics and Probability','17':'Mathematical Software','18':'Econometrics','19':'Pattern Formation and Solitons','20':'Sound','21':'Subcellular Processes','22':'Information Theory','23':'Nuclear Theory','24':'Classical Physics','25':'Physics Education','26':'Geometric Topology','27':'Disordered Systems and Neural Networks','28':'Other Condensed Matter','29':'Representation Theory','30':'Genomics','31':'Discrete Mathematics','32':'Dynamical Systems','33':'History and Philosophy of Physics','34':'High Energy Physics - Lattice','35':'Software Engineering','36':'General Literature','37':'Mesoscale and Nanoscale Physics','38':'Physics Mathematical Physics','39':'General Physics','40':'Combinatorics','41':'Geophysics','42':'Computation and Language','43':'Rings and Algebras','44':'Physics and Society','45':'Group Theory','46':'Logic in Computer Science','47':'Computation','48':'Fluid Dynamics','49':'Methodology','50':'Chemical Physics','51':'Atmospheric and Oceanic Physics','52':'Optics','53':'Machine Learning','54':'General Relativity and Quantum Cosmology','55':'Math Information Theory','56':'Probability','57':'Statistics Theory','58':'Molecular Networks','59':'Analysis of PDEs','60':'Popular Physics','61':'Multiagent Systems','62':'Populations and Evolution','63':'Quantitative Methods','64':'Other Quantitative Biology','65':'Computational Engineering, Finance, and Science','66':'Signal Processing','67':'Superconductivity','68':'Statistical Finance','69':'Multimedia','70':'Atomic and Molecular Clusters','71':'Algebraic Topology','72':'Functional Analysis','73':'Cryptography and Security','74':'Logic','75':'General Topology','76':'Data Structures and Algorithms','77':'Computational Finance','78':'Information Retrieval','79':'Symbolic Computation','80':'General Finance','81':'Quantum Physics','82':'Instrumentation and Methods for Astrophysics','83':'Portfolio Management','84':'Other Statistics','85':'Symplectic Geometry','86':'Human-Computer Interaction','87':'Materials Science','88':'Numerical Analysis','89':'Social and Information Networks','90':'Trading and Market Microstructure','91':'Optimization and Control','92':'Other Computer Science','93':'Commutative Algebra','94':'Complex Variables','95':'Nuclear Experiment','96':'Applied Physics','97':'Artificial Intelligence','98':'Robotics','99':'Cell Behavior','100':'Plasma Physics','101':'Mathematical Finance','102':'Systems and Control','103':'Digital Libraries','104':'Applications','105':'Solar and Stellar Astrophysics','106':'Pricing of Securities','107':'High Energy Physics - Phenomenology','108':'K-Theory and Homology','109':'Quantum Algebra','110':'Databases','111':'Computational Geometry','112':'Graphics','113':'Audio and Speech Processing','114':'Risk Management','115':'Mathematical Physics','116':'Chaotic Dynamics','117':'Classical Analysis and ODEs','118':'Neurons and Cognition','119':'High Energy Physics - Experiment','120':'Biomolecules','121':'Medical Physics','122':'Exactly Solvable and Integrable Systems','123':'Space Physics','124':'Computational Complexity','125':'Statistical Mechanics','126':'Astrophysics of Galaxies','127':'History and Overview','128':'High Energy Physics - Theory','129':'Networking and Internet Architecture','130':'Computers and Society','131':'Adaptation and Self-Organizing Systems','132':'Formal Languages and Automata Theory','133':'Computational Physics','134':'High Energy Astrophysical Phenomena','135':'Algebraic Geometry','136':'Instrumentation and Detectors','137':'Operator Algebras','138':'Operating Systems','139':'Soft Condensed Matter','140':'Tissues and Organs','141':'Differential Geometry','142':'Number Theory','143':'Performance','144':'Economics','145':'Earth and Planetary Astrophysics','146':'Quantum Gases','147':'Computer Science and Game Theory','148':'Atomic Physics','149':'Astrophysics','150':'General Mathematics'}

    # Reference
    # Recreation
    # Sports
    # Computers
    # Adult
    # Drug
    # Business
    # Games
    # Health
    # Warning
    # Science
    # General
    # Shopping
    # Illegal
    # News

    def __init__(self):
        pass

    def generateClassifier(self):
        self.m_classifier = None
        self.initDict()
        # self.clearParsedDataset()
        # self.readDataset()
        self.trainModel()
        pass

    def isClassifierGenerated(self):
        if self.m_classifier is None:
            return False
        else:
            return True

    def initDict(self):
        SpellCheckHandler.getInstance().initDict()

    def trainModel(self):
        self.train()

    def clearParsedDataset(self):
        if path.exists(constants.m_project_path + constants.m_web_classifier_dataset_parsed):
            shutil.rmtree(constants.m_project_path + constants.m_web_classifier_dataset_parsed)
        os.makedirs(constants.m_project_path + constants.m_web_classifier_dataset_parsed)
        self.createTopicDetectionDataset("PREDICTION" + "," + "TEXT", "\\training_data" + ".csv")

    def readDataset(self):
        try:
            file_list = os.listdir(constants.m_web_classifier_dataset)
            file_list = Tcl().call('lsort', '-dict', file_list)
            for folder in file_list:

                if self.m_catagories[folder] != "News" and self.m_catagories[folder] != "Business" and self.m_catagories[folder] != "Illegal" and self.m_catagories[folder] != "Shopping":
                    folder = '3'
                self.m_last_log = "Parsing : " + self.m_catagories[folder] + " : " + folder
                print(self.m_last_log)
                data_list = os.listdir(constants.m_web_classifier_dataset + "\\" + folder)
                data_list = Tcl().call('lsort', '-dict', data_list)

                m_counter = 0
                max_counter = 5000
                if self.m_catagories[folder] == "General":
                    max_counter = 100
                for data_list_file in data_list:
                    m_path = constants.m_web_classifier_dataset + "\\" + folder + "\\" + data_list_file
                    m_counter += 1
                    try:
                        with open(m_path, encoding="utf8", errors='ignore') as f:
                            m_data = f.read()
                            m_status, m_data = self.clean_data(m_data)
                            if m_status and m_counter<max_counter:
                                self.createTopicDetectionDataset(self.m_catagories[folder] + "," + m_data,"\\training_data" + ".csv")  # + str(ceil(int(folder)/100))

                    except Exception as e:
                        print("Parsing : Error : Breaking : " + str(e))
        except Exception as e:
            print("Parsing : Error : Breaking : " + str(e))

    def clean_data(self, p_text):
        # New Line and Tab Remover
        p_text = ' '.join(p_text.split())
        p_text = p_text.replace('\\n', ' ')
        p_text = p_text.replace('\\t', ' ')
        p_text = p_text.replace('\\r', ' ')

        # Tokenizer
        word_list = p_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        incorrect_word, correct_word = SpellCheckHandler.getInstance().validationHandler(word_list)

        if len(correct_word)>3:
            return True,' '.join(correct_word)
        else:
            return False,' '.join(correct_word)

    def createTopicDetectionDataset(self, p_line, p_file_name):
        with open(constants.m_project_path + constants.m_web_classifier_dataset_parsed + "\\" + p_file_name, 'a') as file:
                file.write(p_line)
                file.write('\n')
                file.close()

    def train(self):
        # READ COMMENTS
        print("READING...")
        train_data = pd.read_csv("C://Workspace//Genesis-Crawler-Python//GenesisCrawlerServices//classifiers//training_data.csv")
        # train_data = pd.read_csv(constants.m_project_path + constants.m_classifier_path + "training_data.csv")
        print("READING FINISHED... : " + str(train_data.shape))

        # CLEANING
        print("CLEANING...")
        train_data['TEXT'] = train_data['TEXT'].replace(np.nan, '')
        train_data['TEXT'] = train_data['TEXT'].map(lambda x: re.sub(r'[^A-Za-z ]+', '', x))
        print("CLEANING FINISHED...")

        # READ COMMENTS
        print("SHUFFLING...")
        np.random.shuffle(train_data.values)
        print("SHUFFLING FINISHED...")

        # CREATE VECTORIZER
        print("VECTORIZING...")
        count_vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), stop_words=None,token_pattern='[a-zA-Z]+')
        transformed_vector = count_vectorizer.fit_transform(train_data["TEXT"].values.astype('U'))
        dataframe = pd.DataFrame(transformed_vector.toarray(), columns=count_vectorizer.get_feature_names())
        pickle.dump(count_vectorizer, open(constants.m_project_path + constants.m_vectorizer_pickle_path, "wb"))
        print("VECTORIZING FINISHED...")

        # SELECT KBEST
        print("SELECTING...")
        selector = SelectKBest(score_func=chi2, k=2000)
        selector.fit(dataframe, train_data["PREDICTION"])
        extracted_feature = np.asarray(count_vectorizer.get_feature_names())[selector.get_support()]
        dataframe = dataframe[extracted_feature]
        pickle.dump(extracted_feature, open(constants.m_project_path + constants.m_features_pickle_path, 'wb'))
        self.m_last_log = "SELECTING FINISHED..."
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
        # model = RandomForestClassifier(max_depth=150, random_state=10) # False
        # model = Perceptron(tol=1e-3, random_state=0) # False
        model = MultinomialNB(alpha=1.0, fit_prior=True) # 0.91 - 0.87 - 0.87
        # model = MultinomialHMM(n_components=2, startprob_prior=1.0, transmat_prior=1.0) # False
        # model = MLPClassifier(alpha=1e-05, hidden_layer_sizes=(2,), random_state=1, solver='lbfgs')
        # model = LDA(5)

        print("CREATING MODEL FINISHED...")

        # TRAIN MODEL
        print("TRAINING MODEL...")
        trainedModel = model.fit(train_features, train_labels)
        print("TRAINING MODEL FINISHED...")

        # PREDICTION
        print("PREDICTING...")
        predictions = trainedModel.predict(test_features)
        print("PREDICTING FINISHED...")

        # SAVING
        print("SAVING MODEL...")
        pickle.dump(trainedModel, open(constants.m_project_path + constants.m_classifier_pickle_path, 'wb'))
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
