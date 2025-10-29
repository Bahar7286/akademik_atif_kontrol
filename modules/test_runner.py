from modules.file_reader import read_docx, read_pdf
from modules.sentence_splitter import split_sentences
from modules.reference_parser import extract_references
from modules.similarity_model import get_ensemble_similarity

def run_test_set_from_file(uploaded_file, threshold=0.8):
    """
    Yüklenen .docx veya .pdf dosyasından test seti oluşturur ve doğruluk analizi yapar.
    Her cümle kaynakça ile eşleştirilerek benzerlik skoru hesaplanır.
    """
    # 1. Dosya oku
    if uploaded_file.name.endswith(".docx"):
        text = read_docx(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        text = read_pdf(uploaded_file)
    else:
        return []

    # 2. Cümleleri ve kaynakçayı ayır
    sentences = split_sentences(text)
    references = extract_references(text)

    results = []

    for sentence in sentences:
        for ref in references:
            score = get_ensemble_similarity(sentence, ref)
            prediction = "doğru" if score >= threshold else "yanlış"
            results.append({
                "Cümle": sentence,
                "Referans": ref,
                "Skor": round(score, 3),
                "Tahmin": prediction,
                "Durum": "✅" if prediction == "doğru" else "❌"
            })

    return results