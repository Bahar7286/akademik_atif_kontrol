import re

def has_citation(sentence):
    """
    Cümlede APA, IEEE veya MLA stilinde atıf olup olmadığını kontrol eder.
    """
    apa = re.search(r"\([A-ZÇĞİÖŞÜ][a-zçğıöşü]+, \d{4}\)", sentence)
    ieee = re.search(r"\[\d+\]", sentence)
    mla = re.search(r"\b[A-ZÇĞİÖŞÜ][a-zçğıöşü]+ \d{4}\b", sentence)
    return bool(apa or ieee or mla)

def extract_author_year(sentence):
    """
    APA stilindeki atıftan yazar ve yıl bilgisini çıkarır.
    """
    match = re.search(r"\(([A-ZÇĞİÖŞÜ][a-zçğıöşü]+), (\d{4})\)", sentence)
    return match.groups() if match else (None, None)

def extract_mla_author_year(sentence):
    """
    MLA stilindeki atıftan yazar ve yıl bilgisini çıkarır.
    """
    match = re.search(r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+) (\d{4})\b", sentence)
    return match.groups() if match else (None, None)

def extract_ieee_index(sentence):
    """
    IEEE stilindeki atıftan [n] içindeki sayıyı çıkarır.
    """
    match = re.search(r"\[(\d+)\]", sentence)
    return match.group(1) if match else None

def match_reference(author, year, references):
    """
    APA ve MLA stilinde yazar ve yıl bilgisiyle kaynak eşleştirir.
    """
    if not author or not year:
        return None
    for ref in references:
        if author.lower() in ref.lower() and year in ref:
            return ref
    return None

def match_ieee_reference(index, references):
    """
    IEEE stilinde [5] → 5. kaynak (index 4) ile eşleşir.
    """
    try:
        return references[int(index) - 1]
    except:
        return None

def detect_citation_style(sentence):
    """
    Cümledeki atıf stilini tanımlar: APA, IEEE, MLA veya Bilinmiyor.
    """
    if re.search(r"\([A-ZÇĞİÖŞÜ][a-zçğıöşü]+, \d{4}\)", sentence):
        return "APA"
    elif re.search(r"\[\d+\]", sentence):
        return "IEEE"
    elif re.search(r"\b[A-ZÇĞİÖŞÜ][a-zçğıöşü]+ \d{4}\b", sentence):
        return "MLA"
    else:
        return "Bilinmiyor"

def extract_doi_or_title(reference):
    """
    Referanstan DOI çıkarır, yoksa başlık tahmini yapar.
    Yayınevi, yıl, parantez, noktalama temizlenir.
    """
    match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", reference, re.IGNORECASE)
    if match:
        return match.group(1)

    cleaned = reference
    cleaned = re.sub(r"\(.*?\)", "", cleaned)  # Parantez içi
    cleaned = re.sub(r"\b\d{4}\b", "", cleaned)  # Yıl
    cleaned = re.sub(
        r"(Bilim Yayınları|Akademik Basım|Etik Yayınları|Eğitim Teknolojileri Dergisi|Öğrenme Yayınları)",
        "", cleaned, flags=re.IGNORECASE
    )  # Yayınevi
    cleaned = re.sub(r"[^\w\s]", "", cleaned)  # Noktalama
    cleaned = re.sub(r"\s+", " ", cleaned)  # Fazla boşluk

    return cleaned.strip()

def extract_pdf_from_search(results):
    """
    Web arama sonuçlarından en uygun PDF bağlantısını çıkarır.
    .pdf uzantısı veya 'pdf', 'makale', 'tez', 'download' gibi anahtar kelimeler aranır.
    """
    keywords = ["pdf", "makale", "tez", "download", "fulltext", "article", "view", "dosya", "indir"]

    for result in results:
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()

        if url.endswith(".pdf"):
            return url

        if any(kw in url for kw in keywords) or any(kw in title for kw in keywords) or any(kw in snippet for kw in keywords):
            return url

    return None

def detect_source_type(reference_text):
    """
    Referans metninden kaynak türünü tahmin eder: kitap, makale, tez, bilinmiyor
    """
    text = reference_text.lower()

    if "tez merkezi" in text or "yüksek lisans" in text or "doktora" in text or "danışman" in text:
        return "tez"
    elif "isbn" in text or "yayınları" in text or "basım" in text or "kitabevi" in text:
        return "kitap"
    elif "dergi" in text or "journal" in text or "volume" in text or "issue" in text or "doi" in text:
        return "makale"
    else:
        return "bilinmiyor"