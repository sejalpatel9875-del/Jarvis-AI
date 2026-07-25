import os

def read_pdf_file(file_path: str, max_pages: int = 5) -> str:
    """Reads and extracts text from a PDF document."""
    path = os.path.abspath(file_path.strip())
    if not os.path.exists(path):
        return f"Sorry Boss, PDF file not found at path: '{path}'."
        
    print(f"[PDF Agent] Reading PDF file: {path}...")
    
    # Try pypdf first if available
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        num_pages = min(len(reader.pages), max_pages)
        extracted_text = []
        for i in range(num_pages):
            text = reader.pages[i].extract_text()
            if text:
                extracted_text.append(f"--- Page {i+1} ---\n" + text.strip())
        full_text = "\n\n".join(extracted_text)
        return full_text if full_text else "PDF opened but contains no readable text (scanned image PDF)."
    except ImportError:
        pass
    except Exception as ex:
        print(f"[PDF Agent Warning] pypdf failed: {ex}")
        
    # Fallback to pdfplumber if pypdf was missing
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            extracted_text = []
            for i, page in enumerate(pdf.pages[:max_pages]):
                text = page.extract_text()
                if text:
                    extracted_text.append(f"--- Page {i+1} ---\n" + text.strip())
            return "\n\n".join(extracted_text)
    except Exception:
        pass
        
    return "To read PDF files, please install pypdf: .venv\\Scripts\\pip.exe install pypdf"
