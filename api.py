from fastapi import FastAPI, Query
from modules.citation_checker import detect_citation_style, match_reference, extract_author_year
from modules.reference_parser import extract_references
from modules.similarity_model import find_sentence_in_pdf
from modules.file_reader import read_source_pdf_from_url

app = FastAPI()

@app.get("/detect_style")
def detect_style(sentence: str = Query(..., description="Atıf içeren cümle")):
    style = detect_citation_style(sentence)
    return {"sentence": sentence, "style": style}

@app.get("/match_reference")
def match(sentence: str, references: str):
    """
    Cümle ve kaynakça verildiğinde eşleşme kontrolü yapar.
    references → virgülle ayrılmış kaynaklar
    """
    style = detect_citation_style(sentence)
    ref_list = [r.strip() for r in references.split(",")]

    if style == "APA":
        author, year = extract_author_year(sentence)
        matched = match_reference(author, year, ref_list)
    else:
        matched = None

    return {
        "sentence": sentence,
        "style": style,
        "matched": matched if matched else "eşleşme yok"
    }

@app.get("/find_in_pdf")
def find_in_pdf(sentence: str = Query(...), pdf_url: str = Query(...)):
    """
    Verilen cümleyi PDF içinde arar ve benzerlik skorunu döndürür.
    """
    try:
        source_pages = read_source_pdf_from_url(pdf_url)
        score, page = find_sentence_in_pdf(sentence, source_pages)
        return {
            "sentence": sentence,
            "pdf_url": pdf_url,
            "score": round(score, 3),
            "page": page
        }
    except Exception as e:
        return {"error": str(e)}