import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from app.loader.base_loader import LoaderBase
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Changed import

import pdfplumber
from pytesseract import image_to_string
from PIL import Image

_logger = logging.getLogger(__name__)


class PdfLoader(LoaderBase):
    def __init__(self, file_or_link_path):
       self.path = file_or_link_path
    def extract_docs(self, chunk_size, overlap_chunk):

        loader = PyPDFLoader(self.path)
        pages = loader.load()
        if not pages:
            _logger.warning("PyPDFLoader found no pages. Trying fallback OCR method...")
            return self._try_ocr_fallback(chunk_size, overlap_chunk)
        
        combined_text = "\n".join([p.page_content for p in pages])
        if not combined_text:
            _logger.warning("PyPDFLoader found no combined_text. Trying fallback OCR method...")
            return self._try_ocr_fallback(chunk_size, overlap_chunk)
        # Use RecursiveCharacterTextSplitter instead
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_chunk,
            separators=["\n\n", "\n", " ", ""]  # More aggressive splitting
        )
        
        chunks = text_splitter.split_documents([Document(
            page_content=combined_text,
            metadata=pages[0].metadata
        )])
        
        # Validate chunk sizes
        for chunk in chunks:
            if len(chunk.page_content) > chunk_size * 1.5:  # Allow 50% overflow
                _logger.warning(f"Created a chunk of size {len(chunk.page_content)}, which is longer than the specified {chunk_size}")
        
        return {
            'success': True,
            'message': f'Created {len(chunks)} chunks',
            'pages': chunks
        }
    def _try_ocr_fallback(self, chunk_size, overlap_chunk):
        try:
            fallback_docs = []
            with pdfplumber.open(self.path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        img = page.to_image(resolution=300).original
                        text = image_to_string(img)
                    fallback_docs.append(Document(page_content=text, metadata={"page": i}))

            text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_chunk)
            split_docs = text_splitter.split_documents(fallback_docs)
            if split_docs:
                _logger.info(f"OCR fallback: {len(split_docs)} pages found using image OCR")
                return {'success': True, 'message': 'PDF Pages Found with OCR fallback', 'pages': split_docs}
            else:
                return {'success': False, 'message': 'OCR fallback failed to extract content'}

        except Exception as ocr_error:
            _logger.error("OCR fallback failed: %s" % ocr_error)
            return {'success': False, 'message': f'Could not load the PDF, OCR Error: {ocr_error}'}
    