import logging
import os
import re
import shutil

# from langchain.vectorstores import SKLearnVectorStore
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.vectorstores.sklearn import SKLearnVectorStoreException

_logger = logging.getLogger(__name__)


class VectorStoreSkLearn:
    def __init__(self, storage_path, embeddings):
        self.storage_path = storage_path
        self.embeddings = embeddings
        self.path = os.path.join(self.storage_path, "iera.parquet")

    def get_or_create_collection(self):
        try:
            is_exist = os.path.exists(self.path)
            _logger.info("VectorStoreSkLearn Get or Create Collection: %s" % is_exist)
            if not is_exist:
                os.makedirs(self.storage_path, exist_ok=True)
                return None
            return SKLearnVectorStore(
                embedding=self.embeddings, persist_path=self.path, serializer="parquet"
            )
        except SKLearnVectorStoreException:
            _logger.error("SKLearnVectorStoreException in VectorStoreSkLearn Get or Create Collection")
            shutil.rmtree(self.storage_path)
            return None

    def store_docs_to_collection(self, docs, document_id, document_path):
        for doc in docs:
            doc.metadata['id'] = document_id
            doc.metadata['source'] = document_path
            for k, v in doc.metadata.items():
                if v is None:
                    doc.metadata[k] = ""
                else:
                    if k == 'source':
                        v = re.sub("files/\d+/\d+/\d+_\d+_\d+_\d+_\d+_\d+_\d+_", "", str(v))
                        v = v.strip()
                    doc.metadata[k] = str(v)
        vector_db = self.get_or_create_collection()
        _logger.info("VectorStoreSkLearn in Store Docs in Collection: %s" % vector_db)
        if vector_db is None:
            vector_db = SKLearnVectorStore.from_documents(
                documents=docs, embedding=self.embeddings, persist_path=self.path, serializer="parquet",
            )
            vector_db.persist()
            return True
        vector_db.add_documents(docs)
        vector_db.persist()
        return True

    def delete_document_from_collection(self, doc_id):
        vector_db = self.get_or_create_collection()
        _logger.info("VectorStoreSkLearn in Delete Document From Collection: %s" % vector_db)
        if vector_db is None:
            return False
        document_ids = []
        try:
            for ix, item in enumerate(vector_db._metadatas):
                if item["id"] == str(doc_id):
                    document_ids.append(ix)
            if len(document_ids) > 0:
                vector_db._metadatas = [md for ix, md in enumerate(vector_db._metadatas) if ix not in document_ids]
                vector_db._texts = [md for ix, md in enumerate(vector_db._texts) if ix not in document_ids]
                vector_db._embeddings = [md for ix, md in enumerate(vector_db._embeddings) if ix not in document_ids]
                vector_db._ids = [md for ix, md in enumerate(vector_db._ids) if ix not in document_ids]
                if len(vector_db._embeddings) > 0:
                    vector_db._update_neighbors()
                    vector_db.persist()
                else:
                    shutil.rmtree(self.storage_path)
            return True
        except Exception as e:
            _logger.error("Exception in VectorStoreSkLearn Delete Document Collection : %s" % e)
            return False

    def get_similar_docs(self, query, num_docs):
        vector_db = self.get_or_create_collection()
        _logger.info("VectorStoreSkLearn in Get Similar Docs: %s Num Docs: %s" % (vector_db, num_docs))
        if vector_db is None:
            return []
        if num_docs >= len(vector_db._texts):
            num_docs = len(vector_db._texts)
        return vector_db.similarity_search_with_score(query, k=num_docs)
