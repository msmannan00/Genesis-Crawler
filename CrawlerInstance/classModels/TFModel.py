class tfModel:

    # Variables
    m_score = None
    m_word = None
    m_bigram={}

    # Initializations
    def __init__(self, p_word, p_score):
        self.m_word = p_word
        self.m_score = p_score

    def setBigram(self, p_score, p_word):
        self.m_bigram[p_word] = p_score
