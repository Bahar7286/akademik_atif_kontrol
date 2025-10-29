from sentence_transformers import SentenceTransformer, util
from difflib import SequenceMatcher

# Birden fazla çok dilli model
model1 = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
model2 = SentenceTransformer('distiluse-base-multilingual-cased-v1')
model3 = SentenceTransformer('LaBSE')

def get_ensemble_similarity(sentence, source_text):
    """
    Birden fazla modelin çıktısını birleştirerek hibrit benzerlik skoru döndürür.
    """
    # Semantik skorlar
    emb1_1 = model1.encode(sentence, convert_to_tensor=True)
    emb2_1 = model1.encode(source_text, convert_to_tensor=True)
    score1 = float(util.cos_sim(emb1_1, emb2_1)[0][0])

    emb1_2 = model2.encode(sentence, convert_to_tensor=True)
    emb2_2 = model2.encode(source_text, convert_to_tensor=True)
    score2 = float(util.cos_sim(emb1_2, emb2_2)[0][0])

    emb1_3 = model3.encode(sentence, convert_to_tensor=True)
    emb2_3 = model3.encode(source_text, convert_to_tensor=True)
    score3 = float(util.cos_sim(emb1_3, emb2_3)[0][0])

    # Karakter düzeyinde skor
    char_score = SequenceMatcher(None, sentence, source_text).ratio()

    # Ağırlıklı ortalama
    final_score = (score1 * 0.3 + score2 * 0.3 + score3 * 0.3 + char_score * 0.1)
    return final_score

def find_sentence_in_pdf(sentence, pages):
    """
    Cümleyi PDF sayfaları arasında arar, en benzer sayfa ve skorunu döndürür
    """
    best_score = 0
    best_page = -1
    for i, page_text in enumerate(pages):
        score = get_ensemble_similarity(sentence, page_text)
        if score > best_score:
            best_score = score
            best_page = i + 1
    return best_score, best_page

def find_sentence_in_text(target_sentence, text_lines):
    """
    Cümleyi metin satırları (HTML, DOCX) arasında arar, en benzer satır ve skorunu döndürür
    """
    best_score = 0
    best_index = -1
    for i, line in enumerate(text_lines):
        score = get_ensemble_similarity(target_sentence, line)
        if score > best_score:
            best_score = score
            best_index = i
    return best_score, best_index + 1

def find_section_in_text(target_sentence, text_lines):
    """
    Cümleyi metin satırları arasında arar ve en benzer bölüm başlığını döndürür.
    """
    section_keywords = ["Giriş", "Literatür", "Yöntem", "Bulgular", "Sonuç", "Tartışma", "Kaynaklar"]
    current_section = "Bilinmiyor"
    section_scores = {}

    for i, line in enumerate(text_lines):
        for keyword in section_keywords:
            if keyword.lower() in line.lower():
                current_section = keyword
        score = get_ensemble_similarity(target_sentence, line)
        if current_section not in section_scores or score > section_scores[current_section]:
            section_scores[current_section] = score

    best_section = max(section_scores, key=section_scores.get)
    best_score = section_scores[best_section]
    return best_section, best_score