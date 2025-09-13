import logging
import os
from app.models.user import Users
from app.models import Document

_logger = logging.getLogger(__name__)


class DocumentCRUD:
    """
    Handles document-related operations including upload, deletion,
    and checking the vectorstore processing status via Celery tasks.
    """

    def __init__(self):
        pass
    
    def upload_document(self, db, current_user, file_path):
        from app.workers.celery_workers import upload_document
        """
        Initiates a Celery task to upload and process a document.

        Args:
            params: An object containing file_path and document_id.

        Returns:
            dict: A response dictionary indicating success or failure, along with task_id if successful.
        """
        try:
            response = os.path.exists(file_path)
            if not response:
                _logger.error("file not found: The requested file does not exist ")
                return {
                    "success": False,
                    "msg": "file not found. Please ensure the file exists and the path is correct.",
                    "data": {}
                }
            document = Document(user_id = current_user.id)
            db.add(document)
            db.commit()
            db.refresh(document)
            doc_id = document.id
            task = upload_document.delay(file_path, doc_id, current_user.id)
            if task:
                _logger.info("Celery task submitted successfully. Task ID: %s", task.id)
                return {
                    "success": True,
                    "msg": "Document processing started successfully.",
                    "data": {"task_id": task.id}
                }
            return {
                "success": False,
                "msg": f"Failed to process document."
            }
        except Exception as e:
            _logger.exception("Exception occurred while uploading document: %s", str(e))
            return {
                "success": False,
                "Error": f"Error: {e}",
                "msg": "Failed to upload document."
            }

document = DocumentCRUD()