import io,re
def extract_article_text(name,data):
    if name.lower().endswith('.docx'):
        from docx import Document
        return '\n'.join(p.text for p in Document(io.BytesIO(data)).paragraphs if p.text.strip())
    if name.lower().endswith('.pdf'):
        from pypdf import PdfReader
        return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(data)).pages)
    raise ValueError('Formato não suportado')
def detect_hypotheses(text):
    patterns=[('RSC-H1','Organização espacial',r'organiza[cç][aã]o espacial|distribui[cç][aã]o celular|espa[cç]o-temporal',['x','y','time','cell_id'],'organização espacial','Permutação espacial'),('RSC-H2','Coordenação temporal',r'coordena[cç][aã]o temporal|sincroniza[cç][aã]o|coer[eê]ncia temporal',['cell_id','time','x','y'],'coerência temporal','Permutação temporal'),('RSC-H3','Transições celulares',r'transi[cç][aã]o.*estado|estado celular|diferencia[cç][aã]o',['cell_id','time','cell_state'],'ordenação de estados','Permutação de estados'),('RSC-H4','Coordenação molecular',r'WNT|FGF|BMP|SHH|HAND2|marcadores moleculares',['marker','expression','x','y','time'],'acoplamento molecular','Permutação de marcadores')]
    out=[]
    for hid,name,pat,v,t,n in patterns:
        if re.search(pat,text or '',re.I): out.append({'id':hid,'name':name,'hypothesis':f'O texto contém elementos relacionados a {name.lower()}.','prediction':'Definir previamente um padrão observável e mensurável.','variables':v,'test':t,'null_model':n})
    return out