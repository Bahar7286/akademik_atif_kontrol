import nltk
nltk.download('punkt')

def split_sentences(text):
    from nltk.tokenize import sent_tokenize
    return sent_tokenize(text, language='turkish')
