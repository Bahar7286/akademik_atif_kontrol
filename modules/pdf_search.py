from modules.web_search import search_web
from modules.similarity_model import get_ensemble_similarity

def extract_pdf_from_search(results):
    """
    Web arama sonuçlarından en uygun PDF bağlantısını çıkarır.
    .pdf uzantısı veya 'pdf', 'makale', 'tez', 'download' gibi anahtar kelimeler aranır.
    """
    keywords = ["pdf", "makale", "tez", "download", "fulltext", "article", "view"]

    if not results:
        return None

    for result in results:
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()

        if url.endswith(".pdf"):
            return url

        if any(kw in url for kw in keywords) or any(kw in title for kw in keywords):
            return url

    return None

def search_pdf_sources(query):
    """
    Verilen başlık/DOI için DergiPark, YÖK Tez, OpenAccess gibi kaynaklarda PDF araması yapar.
    En uygun PDF bağlantısını döndürür.
    """
    sources = [
        "site:dergipark.org.tr",
        "site:tez.yok.gov.tr",
        "site:openaccess.hacettepe.edu.tr",
        "site:books.google.com"
    ]

    best_url = None
    best_score = 0

    for site in sources:
        full_query = f"{query} {site}"
        try:
            results = search_web({"query": full_query})
            pdf_url = extract_pdf_from_search(results)

            if pdf_url:
                score = get_ensemble_similarity(query, pdf_url)
                if score > best_score:
                    best_score = score
                    best_url = pdf_url
        except Exception as e:
            print(f"Arama hatası ({site}):", e)

    return best_url

def get_pdf_link_from_sources(title_or_doi: str) -> str:
    """
    Dışarıdan çağrılabilir fonksiyon: başlığa göre en uygun PDF bağlantısını döndürür.
    """
    return search_pdf_sources(title_or_doi)