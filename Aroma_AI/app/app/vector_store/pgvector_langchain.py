import logging
from langchain_community.vectorstores import PGVector

from app.core.config import settings
_logger = logging.getLogger(__name__)

class VectorStorePostgresVector:
    """
    Handles interaction with a PostgreSQL-backed vector store (PGVector)
    using LangChain's PGVector integration.
    """

    def __init__(self, collection_name, embeddings):
        """
        Initialize the vector store client.

        Args:
            collection_name (str): The name of the vector collection.
            embeddings: The embedding function to encode document content.
        """
        self.collection_name = collection_name
        self.pgvector_connection_string = settings.VECTOR_CONNECTION_STRING
        self.embeddings = embeddings

    def get_or_create_collection(self):
        """
        Returns an instance of the PGVector collection. Creates one if it doesn't exist.

        Returns:
            PGVector: A vector store object.
        """
        _logger.info("Getting or creating vector store collection: %s", self.collection_name)
        return PGVector(
            collection_name=self.collection_name,
            connection_string=self.pgvector_connection_string,
            embedding_function=self.embeddings,
        )

    def store_docs_to_collection(self, docs, document_id, document_path):
        """
        Stores documents into the PGVector collection with associated metadata.

        Args:
            docs (List[Document]): A list of LangChain Document objects.
            document_id (str): ID of the source document.
            document_path (str): File path or source identifier of the document.

        Returns:
            bool: True if storage was successful, False otherwise.
        """ 
        try:
            _logger.info("VectorStorePostgresVector store docs to collection")
            for doc in docs:
                inner_metadata = {
                    'id': document_id, 'source': document_path
                }
                for k, v in doc.metadata.items():
                    if k in ['id', 'page', 'source', 'page_number', 'row']:
                        if v is None:
                            inner_metadata[k] = ""
                        else:
                            if k == 'page_number':
                                k = 'page'
                                v = int(v) - 1
                            if k == 'source':
                                if v != document_path:
                                    v = document_path
                                v = v.strip()
                            inner_metadata[k] = str(v)
                doc.metadata = inner_metadata
            vector_db = self.get_or_create_collection()
            texts, metadatas, ids = [], [], []
            for doc in docs:
                texts.append(doc.page_content)
                metadatas.append(doc.metadata)
                ids.append(f"{self.collection_name}_document_id_{document_id}")
            vector_db.add_texts(texts, metadatas, ids=ids)
            _logger.info("Successfully stored documents into vector store.")
            return True
        except Exception as e:
            _logger.error("Exception in VectorStorePostgresVector Store Docs to Collection: %s" % e)
            raise VectorStorePostgresVector(f"exception in store_docs_to_collection: {str(e)}")
    
    def delete_document_from_collection(self, document_id):
        try:
            vector_db = self.get_or_create_collection()
            vector_db.delete([f"{self.collection_name}_document_id_{document_id}"])
            _logger.info("VectorStorePostgresVector delete document from collection: %s" % document_id)
            return True
        except Exception as e:
            _logger.error("Exception in VectorStorePostgresVector Store Docs to Collection: %s" % e)
            return False

    def get_similar_docs(self, query: str, k: int = 5):
        """
        Perform similarity search for a given query.

        Args:
            query (str): The query text to find similar documents.
            k (int): Number of top similar documents to retrieve.

        Returns:
            List[Document]: A list of LangChain Document objects ranked by similarity.
        """
        try:
            _logger.info("Performing similarity search for query: %s", query)
            vector_db = self.get_or_create_collection()
            similar_docs = vector_db.similarity_search(query, k=k)
            return similar_docs
        except Exception as e:
            _logger.error("Exception in similarity search: %s", e)
            return []