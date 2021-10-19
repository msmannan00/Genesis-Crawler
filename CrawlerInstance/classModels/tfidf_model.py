class TFIDFModel:

    # Variables
    m_tf_model = []

    # Initializations
    def __init__(self, p_term_frequency, p_document):
        self.m_tf_model[p_document] = p_term_frequency
