"""Extração e mapeamento determinístico de artigos DOCX/PDF/TXT para hipóteses testáveis."""
import re
from pathlib import Path

KEYWORDS = {
    "spatial": ["espaço-temporal","espacial","organização espacial","distribuição celular","densidade","cluster","migração"],
    "temporal": ["temporal","sincron","trajetória","coerência","ordem temporal","dinâmica"],
    "state": ["estado celular","diferenciação","proliferação","transição","fenótipo","progenitor","stem","célula-tronco"],
    "molecular": ["wnt","fgf","bmp","shh","hand2","sox2","pax6","expressão","marcador","transcriptômica"],
    "comparison": ["regeneração","controle","tumor","oncologia","câncer","lesão","tratamento","condição"]
}

def extract_text_from_bytes(name, data):
    ext=Path(name).suffix.lower()
    if ext==".txt" or ext==".md":
        return data.decode("utf-8", errors="ignore")
    if ext==".docx":
        from docx import Document
        import io
        doc=Document(io.BytesIO(data))
        parts=[p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(c.text for c in row.cells))
        return "\n".join(parts)
    if ext==".pdf":
        from pypdf import PdfReader
        import io
        reader=PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    raise ValueError("Formato não suportado. Use PDF, DOCX, TXT ou MD.")

def split_sentences(text):
    clean=re.sub(r"\s+"," ",text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+",clean) if len(s.strip())>=30]

def detect_hypotheses(text, max_items=12):
    sentences=split_sentences(text)
    candidates=[]
    for s in sentences:
        low=s.lower()
        score=sum(1 for group in KEYWORDS.values() if any(k in low for k in group))
        explicit=any(k in low for k in ["hipótese","hipotetizamos","propomos","prevemos","esperamos","sugerimos","é possível","pode ser descrito"])
        if score>=1 or explicit:
            candidates.append((score+(2 if explicit else 0),s))
    candidates.sort(key=lambda x:x[0], reverse=True)
    seen=set(); out=[]
    for _,s in candidates:
        key=re.sub(r"\W+"," ",s.lower())[:140]
        if key not in seen:
            seen.add(key); out.append(s)
        if len(out)>=max_items: break
    return out

def infer_test_family(hypothesis):
    h=hypothesis.lower()
    if any(k in h for k in KEYWORDS["molecular"]): return "molecular"
    if any(k in h for k in KEYWORDS["state"]): return "state"
    if any(k in h for k in KEYWORDS["temporal"]): return "temporal"
    if any(k in h for k in KEYWORDS["spatial"]): return "spatial"
    return "comparison"
