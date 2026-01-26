import olefile
import io
from typing import Optional, Tuple
import re
import unicodedata

class DocConverter:
    def __init__(self):
        pass

    def doc_to_txt(self, doc_binary: bytes, filename: str = "document.doc") -> Tuple[Optional[str], bool]:
        """
        DOC 바이너리를 TXT로 변환
        Args:
            doc_binary : DOC Binary
            filename: filename (default: "document.doc")

        RETURN:
            (변환된 TXT, 반환 성공 여부)
        """
        # WordDocument
        print("[WordDocument read]")
        try:
            with olefile.OleFileIO(io.BytesIO(doc_binary)) as ole:
                if not ole.exists('WordDocument'):
                    return None, False

                with ole.openstream('WordDocument') as stream:
                    data = stream.read()

                clean_text = self._extract_text_from_bodytext(data)
                return clean_text, True

        except Exception as e:
                print(e)
                return None, False

    def _extract_text_from_bodytext(self, data: bytes) -> Optional[str]:
        """
        data에서 정제된 text 추출

        Args:
            data: 추출할 data

        Returns:
            추출 및 정제된 TXT
        """
        try:
            text = data.decode("utf-16", errors="ignore")
            # 중국어 정제
            cleaned1_text = re.sub(r'[\u4e00-\u9fff]+', '', text)
            # 제어 문자 제거 (C 카테고리)
            cleaned2_text = ''.join(char for char in cleaned1_text if unicodedata.category(char)[0] != "C")
            # 유니코드 제거
            cleaned3_text = re.sub(r'[^가-힣a-zA-Z0-9\s.,\[\]\(\)\:\-\~\%\/]', '', cleaned2_text)
            # 연속 공백 제거
            cleaned4_text = re.sub(r' +', ' ', cleaned3_text)
            cleaned5_text = re.sub(r'\t+', ' ', cleaned4_text)
            # 3자 이상 동일 문자 제거
            cleaned6_text = re.sub(r'(.)\1{2,}', r'\1\1', cleaned5_text)
            return cleaned6_text
        except Exception as e:
            return ""
