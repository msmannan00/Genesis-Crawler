# Generic
onion_extention = ".onion"
onion_str = "onion"
empty = ""
space = " "
linebreak = "\n"
http_protocol_slashed = "http://"
utf_8 = "ISO-8859-1"
python = "python"
empty_json = "{}"

# Spell Check
stopword_language = "english"

# Tor Strings
new_circuit_success = "Circuit Successfully Generated"
new_circuit_fail = "Error Generating Circuit"
bootstrapped = "Bootstrapped 100% (done): Done"
interrupt = "Interrupt: exiting cleanly."
ascii_str = "ascii"
sock_http_proxy = "socks5h://127.0.0.1:"
sock_https_proxy = "socks5h://127.0.0.1:"

# Logs Strings
invoking_thread = "Invoking Threads"
invoked_status = "Invoked Status"

# Web Request Handler
url_processing_error = "ERROR PROCESSING"
image_parsed = "[1] Successfully Parsed Image"
url_parsed = "[1] Successfully Parsed URL"
backup_parsed = "[1] Successfully Saved Backup URL"

# MongoDB Handler
MongoDB_clear_message = 'Data Cleared Successfully'
MongoDB_index_model = 'index_model'
MongoDB_backup_model = 'backup_model'
MongoDB_tfidf_model = 'tfidf_model'
MongoDB_backup_type_general = 'general'

# ICrawler Thread
i_crawl_deadlock = "Crawler Deadlock Reached"

# Spell Checker
stop_words = ['about', 'above', 'across', 'ill', 'after', 'again', 'against', 'all', 'almost', 'alone',
              'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any',
              'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask',
              'asked', 'asking', 'asks', 'at', 'away', 'back', 'backed', 'backing', 'backs', 'be',
              'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being',
              'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can',
              'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd',
              'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed',
              'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending',
              'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything',
              'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds',
              'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering',
              'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives',
              'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped',
              'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself',
              'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however',
              'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is',
              'it', 'its', 'itself', 'just', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows',
              'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like',
              'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may',
              'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much',
              'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never',
              'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing',
              'now', 'nowhere', 'number', 'numbers', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on',
              'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered',
              'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'part', 'parted', 'parting',
              'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points',
              'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put',
              'puts', 'quite', 'rather', 'really', 'right', 'right', 'room', 'rooms', 'said', 'same',
              'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems',
              'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side',
              'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone',
              'something', 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take',
              'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these',
              'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought',
              'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward',
              'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up', 'upon', 'us',
              'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way',
              'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which',
              'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work',
              'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young',
              'younger', 'youngest', 'your', 'yours', 'z', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
              'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
              'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
              'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
              'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
              'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
              'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
              'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
              'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
              'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
              'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
              'can', 'will', 'just', 'don', 'should', 'now']
