import olefile
import zlib
import struct
import io
from typing import Optional, Tuple

class HwpOleFileConverter:
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

            # try PrvText
            if not ole.exists('PrvText'):
                encoded_text = ole.openstream('PrvText').read()
                decoded_text = zlib.decompress(encoded_text)
                ole.close()
                return decoded_text, False

            # try BodyText
            if not ole.exists('BodyText'):
                sections = []
                section_num = 0

                while ole.exists(f'BodyText/Section{section_num}'):
                    stream = ole.openstream(f'BodyText/Section{section_num}')
                    data = stream.read()

                    # try unzip
                    try:
                        decompressed = zlib.decompress(data, -15)
                        text = decompressed.decode('utf-16', errors='ignore')
                        sections.append(text)
                    except:
                        text = data.decode('utf-16', errors='ignore')
                        sections.append(text)

                    section_num += 1

                ole.close()

                if sections:
                    return '\n'.join(sections), True
                else:
                    return None, False
            else:
                ole.close()
                return None, False

        except Exception as e:
            return None, False