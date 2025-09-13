import logging
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from .base_loader import LoaderBase
_logger = logging.getLogger(__name__)



class CsvLoader(LoaderBase):
    def __init__(self, file_or_link_path):
        super().__init__(file_or_link_path)

    def extract_docs(self, chunk_size, overlap_chunk):
        try:
            loader = CSVLoader(self.path)
            text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_chunk)
            pages = loader.load_and_split(text_splitter)
            if not pages:
                _logger.info("CSVLoader Extract Docs No Pages")
                return {'success': False, 'message': f'Could not load the data of the CSV'}
            return {'success': True, 'message': 'CSV Pages Found', 'pages': pages}
        except Exception as e:
            _logger.error("Exception in CSVLoader Extract Docs: %s" % e)
            return {'success': False, 'message': f'Could not load the data of the CSV, Error: {e}'}
