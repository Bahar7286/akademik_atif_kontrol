import requests
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_web(params):
    """
    SerpAPI üzerinden Google araması yapar.
    'query' parametresi zorunludur.
    Sonuçlardan başlık, bağlantı ve snippet bilgilerini döndürür.
    """
    query = params.get("query", "").strip()
    if not query:
        print("Uyarı: Arama sorgusu boş.")
        return []

    url = "https://serpapi.com/search"
    payload = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google"
    }

    try:
        response = requests.get(url, params=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for result in data.get("organic_results", []):
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })

        return results

    except requests.exceptions.Timeout:
        print("Hata: Arama isteği zaman aşımına uğradı.")
    except requests.exceptions.RequestException as e:
        print(f"İstek hatası: {e}")
    except Exception as e:
        print(f"Genel hata: {e}")

    return []

def extract_pdf_from_search(results):
    """
    Web arama sonuçlarından ilk PDF bağlantısını çıkarır.
    .pdf uzantısı veya 'pdf', 'makale', 'tez', 'download' gibi anahtar kelimeler aranır.
    """
    for result in results:
        url = result.get("url", "").lower()
        if url.endswith(".pdf"):
            return url
        if any(keyword in url for keyword in ["pdf", "makale", "tez", "download"]):
            return url
    return None

def get_similarity(a, b):
    """
    Basit karakter düzeyinde benzerlik skoru (0.0 - 1.0)
    """
    return SequenceMatcher(None, a, b).ratio()