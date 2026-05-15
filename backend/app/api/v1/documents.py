from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File, Query, status

from app.api.deps import get_current_user
from app.core.exceptions import http_400, http_404
from app.models.user import User
from app.repositories.document_repo import document_repo
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusResponse,
)
from app.services.document_service import document_service

router = APIRouter(prefix="/library", tags=["Document Library"])


def _format(doc) -> DocumentResponse:
    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        created_at=doc.created_at,
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document (PDF, DOCX, TXT).
    Processing happens in the background — poll /library/{id}/status for progress.
    """
    try:
        doc = await document_service.upload(file, str(current_user.id), background_tasks)
        return _format(doc)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise http_400(f"{type(e).__name__}: {str(e)}")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """List all documents uploaded by the current user."""
    skip = (page - 1) * page_size
    docs = await document_repo.get_by_user(str(current_user.id), skip, page_size)
    total = await document_repo.count_by_user(str(current_user.id))
    return DocumentListResponse(
        documents=[_format(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, current_user: User = Depends(get_current_user)):
    """Get metadata for a specific document."""
    doc = await document_repo.get_by_id(doc_id)
    if not doc or str(doc.user_id) != str(current_user.id):
        raise http_404("Document not found.")
    return _format(doc)


@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    doc_id: str, current_user: User = Depends(get_current_user)
):
    """Poll processing status for a recently uploaded document."""
    doc = await document_repo.get_by_id(doc_id)
    if not doc or str(doc.user_id) != str(current_user.id):
        raise http_404("Document not found.")
    return DocumentStatusResponse(
        id=str(doc.id),
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, current_user: User = Depends(get_current_user)):
    """Delete a document and all its chunks."""
    deleted = await document_service.delete(doc_id, str(current_user.id))
    if not deleted:
        raise http_404("Document not found.")
