import logging
from .pdf_loader import PdfLoader
from .csv_loader import CsvLoader

_logger = logging.getLogger(__name__)

def get_loader(file_or_path: str):
    _logger.info("In Get Loader %s" % file_or_path)
    if ".pdf" in file_or_path:
        _logger.info("PDF Loader Selected")
        return PdfLoader(file_or_path)
    elif ".csv" in file_or_path:
        _logger.info("CSV Loader Selected")
        return CsvLoader(file_or_path)
    else:
        _logger.info("Nothing Selected")
        return None