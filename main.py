from modules.file_reader import read_docx
from modules.sentence_splitter import split_sentences
from modules.citation_checker import has_citation
from modules.reference_parser import extract_references
from modules.similarity_model import get_similarity
from modules.ensemble_model import predict

text = read_docx("data/test_makale.docx")
sentences = split_sentences(text)
references = extract_references(text)

for i, sentence in enumerate(sentences):
    if not has_citation(sentence):
        continue
    # kaynakça eşleşmesi ve benzerlik analizi burada yapılır
    # örnek: features = [1, 1, 0.85]
    # karar = predict(features)