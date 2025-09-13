from abc import ABC, abstractmethod


class LoaderBase(ABC):
    def __init__(self, file_or_link_path):
        self.path = file_or_link_path

    @abstractmethod
    def extract_docs(self, chunk_size, overlap_chunk):
        """
        returns docs from path
        """
        raise NotImplementedError
