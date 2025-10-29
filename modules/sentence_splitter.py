import nltk
from nltk.tokenize import sent_tokenize

# Punkt verisi eksikse indir
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def split_sentences(text):
    return sent_tokenize(text, language="turkish")