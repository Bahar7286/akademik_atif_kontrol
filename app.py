import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
load_dotenv()

# ✅ Sayfa yapılandırması
st.set_page_config(page_title="Akademik Atıf Kontrol", layout="wide")

# 📦 Modül importları
from modules.file_reader import read_docx, read_pdf, read_source_pdf_from_url
from modules.sentence_splitter import split_sentences
from modules.citation_checker import (
    has_citation,
    extract_author_year,
    match_reference,
    detect_citation_style,
    extract_ieee_index,
    match_ieee_reference,
    extract_mla_author_year,
    extract_doi_or_title,
    extract_pdf_from_search,
    detect_source_type
)
from modules.reference_parser import (
    extract_references,
    get_pdf_link_from_crossref
)
from modules.similarity_model import find_sentence_in_pdf, find_section_in_text
from modules.pdf_search import get_pdf_link_from_sources
from modules.test_runner import run_test_set
import io

# 🧪 Test seti bölümü
st.markdown("### 🧪 Test Seti Sonuçları")
test_results = run_test_set()
df_test = pd.DataFrame(test_results)
st.dataframe(df_test)

accuracy = df_test["Durum"].value_counts().get("✅", 0) / len(df_test)
st.metric("🎯 Doğruluk Oranı", f"%{round(accuracy * 100)}")

# 📄 Dosya yükleme bölümü
st.markdown("---")
st.title("📚 Akademik Atıf Kontrol Sistemi")

uploaded_file = st.file_uploader("📄 Lütfen bir .docx veya .pdf dosyası yükleyin", type=["docx", "pdf"])

if uploaded_file:
    # Dosya okuma
    if uploaded_file.name.endswith(".docx"):
        text = read_docx(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        text = read_pdf(uploaded_file)
    else:
        st.error("Sadece .docx veya .pdf dosyaları destekleniyor.")
        st.stop()

    # Cümleleri ve kaynakçayı ayır
    sentences = split_sentences(text)
    references = extract_references(text)
    st.write("📘 Kaynakça:", references)

    results = []

    for i, sentence in enumerate(sentences):
        if not has_citation(sentence):
            continue

        citation_style = detect_citation_style(sentence)
        matched_ref = None
        source_type = "bilinmiyor"
        section = "bilinmiyor"
        score = 0
        page = "-"
        uyarı = "❌ Atıf doğrulanamadı"

        if citation_style == "APA":
            author, year = extract_author_year(sentence)
            matched_ref = match_reference(author, year, references)
        elif citation_style == "IEEE":
            index = extract_ieee_index(sentence)
            matched_ref = match_ieee_reference(index, references)
        elif citation_style == "MLA":
            author, year = extract_mla_author_year(sentence)
            matched_ref = match_reference(author, year, references)

        if matched_ref:
            source_type = detect_source_type(matched_ref)
            kaynak_durumu = f"✅ Eşleşen kaynak: {matched_ref}"
            doi_or_title = extract_doi_or_title(matched_ref)

            # PDF bağlantısı bulma
            pdf_url = get_pdf_link_from_crossref(doi_or_title)
            if not pdf_url:
                pdf_url = get_pdf_link_from_sources(doi_or_title)

            if pdf_url:
                source_pages = read_source_pdf_from_url(pdf_url)
                score, page = find_sentence_in_pdf(sentence, source_pages)
                section, _ = find_section_in_text(sentence, source_pages)

                if score >= 0.8:
                    uyarı = f"✅ Atıf doğru (Sayfa {page})"
                elif score >= 0.5:
                    uyarı = f"⚠️ Benzer ama doğruluğu kontrol edilmeli (Sayfa {page})"
                else:
                    uyarı = f"❌ Atıf hatalı olabilir (Sayfa {page})"
            else:
                uyarı = "📘 PDF bağlantısı bulunamadı"
        else:
            kaynak_durumu = f"❌ Kaynakçada eşleşme yok"

        results.append({
            "Cümle No": i + 1,
            "Cümle": sentence,
            "Atıf Türü": citation_style,
            "Kaynak Türü": source_type,
            "Kaynak Var mı": "✅" if matched_ref else "❌",
            "Geçtiği Bölüm": section,
            "Kaynak Durumu": kaynak_durumu,
            "Benzerlik (%)": round(score * 100, 2),
            "Sayfa No": page,
            "Uyarı": uyarı
        })

    # 📊 Tablo gösterimi
    st.markdown("### 📊 Analiz Sonuçları")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    # 📈 Benzerlik Skoru Grafiği
    st.markdown("### 📈 Benzerlik Skoru Grafiği")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Cümle No:O", title="Cümle No", sort="ascending"),
        y=alt.Y("Benzerlik (%):Q", title="Benzerlik Skoru"),
        color=alt.Color("Atıf Türü:N", title="Atıf Stili"),
        tooltip=[
            "Cümle", "Benzerlik (%)", "Sayfa No", "Uyarı",
            "Atıf Türü", "Kaynak Türü", "Kaynak Durumu"
        ]
    ).properties(width=700, height=400).interactive()

    st.altair_chart(chart, use_container_width=True)

    # 📘 Kaynak Türü Dağılımı
    st.markdown("### 📘 Kaynak Türü Dağılımı")
    type_counts = df["Kaynak Türü"].value_counts().reset_index()
    type_chart = alt.Chart(type_counts).mark_bar().encode(
        x=alt.X("index:N", title="Kaynak Türü"),
        y=alt.Y("Kaynak Türü:Q", title="Sayı"),
        color="index:N"
    ).properties(width=400, height=300)

    st.altair_chart(type_chart)

    # 🧠 Atıf Stili Dağılımı
    st.markdown("### 🧠 Atıf Stili Dağılımı")
    style_counts = df["Atıf Türü"].value_counts().reset_index()
    style_chart = alt.Chart(style_counts).mark_bar().encode(
        x=alt.X("index:N", title="Atıf Stili"),
        y=alt.Y("Atıf Türü:Q", title="Sayı"),
        color="index:N"
    ).properties(width=400, height=300)

    st.altair_chart(style_chart)

    # 📥 Dışa Aktarma
    st.markdown("### 📥 Sonuçları Dışa Aktar")
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📄 CSV olarak indir",
        data=csv_buffer.getvalue(),
        file_name="analiz_sonuclari.csv",
        mime="text/csv"
    )