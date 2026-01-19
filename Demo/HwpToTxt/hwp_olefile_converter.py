import olefile
import zlib
import io
from typing import Optional, Tuple
import re
import unicodedata

class HwpOleFileConverter:
    def __init__(self):
        pass

    def hwp_to_txt_ole(self, hwp_binary: bytes, filename: str = "document.hwp") -> Tuple[Optional[str], bool]:
        """
        HWP 바이너리를 TXT로 변환
        Args:
            hwp_binary : HWP Binary
            filename: filename (default: "document.hwp")

        RETURN:
            (변환된 TXT, 반환 성공 여부)
        """
        try:
            # Memory To Buffer
            hwp_buffer = io.BytesIO(hwp_binary)

            # Read Hwp File
            ole = olefile.OleFileIO(hwp_buffer)

            print("[stream list]")
            for entry in ole.listdir():
                print(f"   - {'/'.join(entry)}")

            all_texts = []

            # # PrvText 현재 미사용
            # if ole.exists('PrvText'):
            #     print("[PrvText read]")
            #     encoded_text = ole.openstream('PrvText').read()
            #     print(f"[PrvText encoded size] {len(encoded_text)}")
            #     decoded_text = encoded_text.decode("utf-16")
            #     print(f"[PrvText decoded size] {len(decoded_text)}")
            #     all_texts.append(decoded_text)
            # else:
            #     print("[PrvText not exist]")

            # BodyText
            print("[BodyText read]")
            section_num = 0

            while ole.exists(f'BodyText/Section{section_num}'):
                print(f"[BodyText section {section_num}]")
                try:
                    stream = ole.openstream(f'BodyText/Section{section_num}')
                    data = stream.read()
                    print(f"[BodyText size] {len(data)}")

                    # unzip
                    try:
                        decompressed = zlib.decompress(data, -15)
                        print(f"[BodyText decompressed size] {len(decompressed)}")
                        section_text = self._extract_text_from_bodytext(decompressed)
                        all_texts.append(section_text)
                    except zlib.error as e:
                        print("[BodyText not zip]")
                        section_text = self._extract_text_from_bodytext(data)

                    if section_text.strip():
                        all_texts.append(section_text)
                        print(f"[BodyText size] {len(all_texts)}")
                except Exception as e:
                    print(f"[BodyText section {section_num} error] {str(e)}")

                section_num += 1

            ole.close()

            return "".join(all_texts), True

        except Exception as e:
            return None, False

    def _extract_text_from_bodytext(self, data: bytes) -> Optional[str]:
        """
        BodyText binary data에서 txt 추출

        Args:
            data: 압축 해제 된 BodyText

        Returns:
            추출된 TXT
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
            return cleaned5_text
        except Exception as e:
            return ""
