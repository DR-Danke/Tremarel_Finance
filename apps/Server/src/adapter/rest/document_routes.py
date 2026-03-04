"""Document endpoint routes."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.document_service import document_service
from src.core.services.invoice_processor import invoice_processor
from src.interface.document_dto import (
    DocumentCreateDTO,
    DocumentResponseDTO,
    DocumentUpdateDTO,
)
from src.interface.invoice_dto import InvoiceProcessingResultDTO

router = APIRouter(prefix="/api/documents", tags=["Documents"])


def _to_response(document: object) -> DocumentResponseDTO:
    """Convert a Document model to DocumentResponseDTO with computed expiration_status."""
    return DocumentResponseDTO.model_validate(document, from_attributes=True)


@router.post("", response_model=DocumentResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_document(
    restaurant_id: UUID = Form(..., description="Restaurant UUID"),
    type: str = Form(..., min_length=1, max_length=100, description="Document type"),
    issue_date: Optional[date] = Form(None, description="Issue date"),
    expiration_date: Optional[date] = Form(None, description="Expiration date"),
    person_id: Optional[UUID] = Form(None, description="Person UUID"),
    description: Optional[str] = Form(None, description="Document description"),
    file: Optional[UploadFile] = File(None, description="Document file upload"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> DocumentResponseDTO:
    """
    Create a new document with optional file upload (multipart/form-data).

    Args:
        restaurant_id: Restaurant UUID
        type: Document type
        issue_date: Optional issue date
        expiration_date: Optional expiration date
        person_id: Optional person UUID
        description: Optional description
        file: Optional file upload
        db: Database session
        current_user: Current authenticated user

    Returns:
        DocumentResponseDTO: Created document information
    """
    print(f"INFO [DocumentRoutes]: Create document request from user {current_user['email']}")

    user_id = UUID(current_user["id"])

    # Build DTO from form fields
    data = DocumentCreateDTO(
        restaurant_id=restaurant_id,
        type=type,
        issue_date=issue_date,
        expiration_date=expiration_date,
        person_id=person_id,
        description=description,
    )

    # Handle file upload
    file_url = None
    if file and file.filename:
        file_url = document_service.save_upload_file(file)

    try:
        document = document_service.create_document(db, user_id, data, file_url)
        print(f"INFO [DocumentRoutes]: Document type '{document.type}' created successfully")
        return _to_response(document)
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/expiring", response_model=List[DocumentResponseDTO])
async def get_expiring_documents(
    restaurant_id: UUID = Query(..., description="Restaurant UUID"),
    days_ahead: int = Query(30, description="Number of days ahead to check"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[DocumentResponseDTO]:
    """
    Get documents expiring within N days for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        days_ahead: Number of days ahead to look
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of expiring DocumentResponseDTO objects
    """
    print(f"INFO [DocumentRoutes]: Expiring documents request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        documents = document_service.get_expiring_documents(db, user_id, restaurant_id, days_ahead)
        print(f"INFO [DocumentRoutes]: Returning {len(documents)} expiring documents")
        return [_to_response(d) for d in documents]
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("", response_model=List[DocumentResponseDTO])
async def list_documents(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to list documents for"),
    type: Optional[str] = Query(None, description="Filter by document type"),
    expiration_status: Optional[str] = Query(None, description="Filter by expiration status: valid, expiring_soon, expired"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[DocumentResponseDTO]:
    """
    List all documents in a restaurant, with optional filters.

    Args:
        restaurant_id: Restaurant UUID
        type: Optional document type filter
        expiration_status: Optional expiration status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of DocumentResponseDTO objects
    """
    print(f"INFO [DocumentRoutes]: List documents request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        documents = document_service.get_documents(db, user_id, restaurant_id, type, expiration_status)
        print(f"INFO [DocumentRoutes]: Returning {len(documents)} documents")
        return [_to_response(d) for d in documents]
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/{document_id}/process-invoice", response_model=InvoiceProcessingResultDTO)
async def process_invoice(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> InvoiceProcessingResultDTO:
    """
    Trigger OCR processing on a supplier invoice document.

    Extracts line items via OCR, matches to existing resources, updates costs,
    and creates inventory movements.

    Args:
        document_id: Document UUID to process
        db: Database session
        current_user: Current authenticated user

    Returns:
        InvoiceProcessingResultDTO: Processing results with matched/unmatched items
    """
    print(f"INFO [DocumentRoutes]: Process invoice request for document {document_id} from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        result = invoice_processor.process_invoice_document(db, user_id, document_id)
        print(f"INFO [DocumentRoutes]: Invoice processing completed for document {document_id}")
        return InvoiceProcessingResultDTO(**result)
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"ERROR [DocumentRoutes]: Document not found: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        print(f"ERROR [DocumentRoutes]: Invalid request: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get("/{document_id}/processing-result")
async def get_processing_result(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Retrieve the OCR processing result for a document.

    Args:
        document_id: Document UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict with processing_status and processing_result
    """
    print(f"INFO [DocumentRoutes]: Get processing result for document {document_id} from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        document = document_service.get_document(db, user_id, document_id)
        print(f"INFO [DocumentRoutes]: Returning processing result for document {document_id}")
        return {
            "document_id": str(document.id),
            "processing_status": document.processing_status,
            "processing_result": document.processing_result,
        }
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [DocumentRoutes]: Document not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{document_id}", response_model=DocumentResponseDTO)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> DocumentResponseDTO:
    """
    Get a specific document by ID.

    Args:
        document_id: Document UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        DocumentResponseDTO: Document information
    """
    print(f"INFO [DocumentRoutes]: Get document {document_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        document = document_service.get_document(db, user_id, document_id)
        print(f"INFO [DocumentRoutes]: Returning document type '{document.type}'")
        return _to_response(document)
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [DocumentRoutes]: Document not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{document_id}", response_model=DocumentResponseDTO)
async def update_document(
    document_id: UUID,
    data: DocumentUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> DocumentResponseDTO:
    """
    Update a document.

    Args:
        document_id: Document UUID
        data: Document update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        DocumentResponseDTO: Updated document information
    """
    print(f"INFO [DocumentRoutes]: Update document {document_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        document = document_service.update_document(db, user_id, document_id, data)
        print(f"INFO [DocumentRoutes]: Document type '{document.type}' updated successfully")
        return _to_response(document)
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [DocumentRoutes]: Document not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Delete a document.

    Args:
        document_id: Document UUID
        db: Database session
        current_user: Current authenticated user
    """
    print(f"INFO [DocumentRoutes]: Delete document {document_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        document_service.delete_document(db, user_id, document_id)
        print(f"INFO [DocumentRoutes]: Document {document_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [DocumentRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [DocumentRoutes]: Document not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
