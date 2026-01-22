from typing import Literal
from pathlib import Path
from fastapi import UploadFile

from HwpToTxt.hwp_olefile_converter import HwpOleFileConverter

# 파일 타입 정의
FileType = Literal["hwp", "doc", "pdf", "other"]

# Init
hwp_converter = HwpOleFileConverter()

class FileClassifier:
    # 허용된 확장자 목록
    ALLOWED_EXTENSIONS = {".hwp", ".hwpx", ".doc", ".docx", ".pdf"}

    # 파일 매핑 (dict에 파일 타입 명시)
    EXTENSION_MAP: dict[str, FileType] = {
        ".hwp": "hwp",
        ".hwpx": "hwp",
        ".doc": "doc",
        ".docx": "doc",
        ".pdf": "pdf",
    }

    def __init__(self):
        pass

    def classify(self, filename: str) -> FileType:
        """
        파일명에서 확장자를 추출하여 파일 타입 반환

        Args:
             filename: file name

        Returns:
            FileType: file type
        """
        extension = Path(filename).suffix.lower()
        file_type = self.EXTENSION_MAP.get(extension, "other")
        print(f"[File Classifier] {filename} -> {file_type} | {extension}")
        return file_type

    def is_allowed(self, filename: str) -> bool:
        """
        파일명에서 확장자를 추출하여 파일 타입 반환

        Args:
             filename: file name

        Returns:
            bool: 허용 여부
        """
        extension = Path(filename).suffix.lower()
        is_allowed = extension in self.ALLOWED_EXTENSIONS
        print(f"[File Classifier] {filename} -> {is_allowed} | {extension}")
        return is_allowed

async def process_hwp(file: UploadFile) -> dict:
    """
    HWP TO TXT 호출

    Args:
         file: Upload file

    Returns:
        dict: {"success":bool, "text":str, "message":str}
    """
    try:
        content = await file.read()
        print(f"[File Classifier] HWP {file.filename} -> {len(content)} bytes")
        converter = HwpOleFileConverter()
        text, success = converter.hwp_to_txt_ole(content, file.filename)

        if success and text:
            return {
                "success": True,
                "text": text,
                "message": "HWP Convert Success",
            }
        else:
            return {
                "success": False,
                "text": "",
                "message": "HWP Convert Failed",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "HWP Convert Failed",
        }


async def process_doc(file: UploadFile) -> dict:
    """
    DOC TO TXT 호출 // 구현 후 수정 필요

    Args:
         file: Upload file

    Returns:
        dict: {"success":bool, "text":str, "message":str}
    """
    try:
        content = await file.read()
        print(f"[File Classifier] DOC {file.filename} -> {len(content)} bytes")
        converter = HwpOleFileConverter()
        text, success = converter.hwp_to_txt_ole(content, file.filename)

        if success and text:
            return {
                "success": True,
                "text": text,
                "message": "DOC Convert Success",
            }
        else:
            return {
                "success": False,
                "text": "",
                "message": "DOC Convert Failed",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "DOC Convert Failed",
        }


async def process_pdf(file: UploadFile) -> dict:
    """
    PDF TO TXT 호출 // 구현 후 수정 필요

    Args:
         file: Upload file

    Returns:
        dict: {"success":bool, "text":str, "message":str}
    """
    try:
        content = await file.read()
        print(f"[File Classifier] PDF {file.filename} -> {len(content)} bytes")
        converter = HwpOleFileConverter()
        text, success = converter.hwp_to_txt_ole(content, file.filename)

        if success and text:
            return {
                "success": True,
                "text": text,
                "message": "PDF Convert Success",
            }
        else:
            return {
                "success": False,
                "text": "",
                "message": "PDF Convert Failed",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "PDF Convert Failed",
        }

async def process_other(file: UploadFile) -> dict:
    """
    지원하지 않는 파일 형식 처리

    Args:
         file: Upload file

    Returns:
        dict: {"success":bool, "text":str, "message":str}
    """
    extension = Path(file.filename).suffix.lower()
    return {
        "success": False,
        "text": "",
        "message": f"Can't Convert File {extension}",
        "extension": extension,
    }

async def process_file_by_type(file: UploadFile, file_type: FileType) -> dict:
    """
    파일에 따라 함수 호출

    Args:
         file: Upload file
         file_type: FileType

    Returns:
        dict: {"success":bool, "text":str, "message":str}
    """
    processors = {
        "hwp": process_hwp,
        "doc": process_doc,
        "pdf": process_pdf,
        "other": process_other,
    }

    processor = processors.get(file_type, process_other)
    result = await processor(file)

    return result