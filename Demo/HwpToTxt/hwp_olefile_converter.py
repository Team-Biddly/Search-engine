import olefile
import zlib
import struct
import io
from typing import Optional, Tuple

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

            # PrvText
            if ole.exists('PrvText'):
                print("[PrvText read]")
                encoded_text = ole.openstream('PrvText').read()
                print(f"[PrvText encoded size] {len(encoded_text)}")
                decoded_text = encoded_text.decode("utf-16")
                print(f"[PrvText decoded size] {len(decoded_text)}")
                all_texts.append(decoded_text)
            else:
                print("[PrvText not exist]")

            # # BodyText
            # print("[BodyText read]")
            # section_num = 0
            #
            # while ole.exists(f'BodyText/Section{section_num}'):
            #     print(f"[BodyText section {section_num}]")
            #     try:
            #         stream = ole.openstream(f'BodyText/Section{section_num}')
            #         data = stream.read()
            #         print(f"[BodyText size] {len(data)}")
            #
            #         # unzip
            #         try:
            #             decompressed = zlib.decompress(data, -15)
            #             print(f"[BodyText decompressed size] {len(decompressed)}")
            #             all_texts.append(decompressed)
            #             section_text = self._extract_text_from_bodytext(decompressed)
            #         except zlib.error as e:
            #             print("[BodyText not zip]")
            #             section_text = self._extract_text_from_bodytext(data)
            #
            #         if section_text.strip():
            #             all_texts.append(section_text)
            #             print(f"[BodyText size] {len(all_texts)}")
            #     except Exception as e:
            #         print(f"[BodyText section {section_num} error] {str(e)}")
            #
            #     section_num += 1

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
            cleaned_text = ''
            for char in text:
                code = ord(char)
                if code > 32 or char in '\n\r\t':
                    cleaned_text += char
                elif code == 13:
                    cleaned_text += "\n"

            return cleaned_text
        except Exception as e:
            return ""