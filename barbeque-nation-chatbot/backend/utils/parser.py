from docx import Document

def parse_docx(path):
    doc = Document(path)
    content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return content
