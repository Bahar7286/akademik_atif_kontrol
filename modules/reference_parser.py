import requests

def extract_references(text):
    start = text.lower().find("kaynakça")
    if start == -1:
        return []
    reference_text = text[start:]
    lines = reference_text.split("\n")
    references = [line.strip() for line in lines if len(line.strip()) > 5]
    return references

def extract_doi_or_title(reference):
    import re
    doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", reference, re.IGNORECASE)
    if doi_match:
        return doi_match.group(1)
    else:
        return reference[:80]  # İlk 80 karakteri eser adı olarak kullan

def get_pdf_link_from_crossref(doi_or_title):
    if doi_or_title.startswith("10."):
        url = f"https://api.crossref.org/works/{doi_or_title}"
    else:
        url = f"https://api.crossref.org/works?query.title={doi_or_title}"

    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()

    try:
        item = data["message"]["items"][0]
        for link in item.get("link", []):
            if link["content-type"] == "application/pdf":
                return link["URL"]
    except:
        return None