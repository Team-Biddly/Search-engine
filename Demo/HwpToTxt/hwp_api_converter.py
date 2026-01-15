import requests
import io
from typing import Optional, Tuple

class HwpApiConverter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "~~~~~"

    def hwp_to_txt_api(self, hwp_binary: bytes, filename: str = "document.hwp") -> Tuple[Optional[str], bool]:
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

            # Call API
            files = {'file': (filename, hwp_buffer, 'application/x-hwp')}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            data = {'output_format': 'txt', 'encoding': 'utf-8'}

            response = requests.post(
                self.api_url,
                files=files,
                headers=headers,
                data=data,
                timeout=60
            )

            if response.status_code == 200:
                text = response.content.decode("utf-8")
                return text, True
            else:
                return None, False

        except Exception as e:
            return None, False