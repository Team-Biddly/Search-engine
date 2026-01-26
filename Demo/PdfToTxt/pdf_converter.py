import pdfplumber
import io

class PdfConverter: #추후 확장성을 위해  class로 작성
    def pdf_to_txt(self, file_bytes:bytes)->(str,bool):
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text=""
                for page in pdf.pages:
                    page_text=page.extract_text()

                    if page_text:
                        text+=page_text+"\n"
            return text.strip(), True
        except Exception as e:
            print(f"PDF Convert Error: {e}")
            return str(e), False