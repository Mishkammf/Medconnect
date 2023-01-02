import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable

from fastapi import UploadFile

from exceptions.custom_exceptions import FileSavingException


def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    Path(destination).parent.mkdir(exist_ok=True, parents=True)
    try:
        upload_file.file.seek(0)
        with Path(destination).open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

    except OSError:
        raise FileSavingException

    finally:
        upload_file.file.close()


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        upload_file.file.seek(0)
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)

    except OSError:
        raise FileSavingException

    finally:
        upload_file.file.close()
    return tmp_path


def handle_upload_file(
        upload_file: UploadFile, handler: Callable[[Path], None]
) -> None:
    tmp_path = save_upload_file_tmp(upload_file)
    try:
        handler(tmp_path)  # Do something with the saved temp file
    finally:
        tmp_path.unlink()  # Delete the temp file
