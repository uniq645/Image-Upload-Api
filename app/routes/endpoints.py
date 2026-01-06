import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services import analysis, storage
from app.utils.auth import api_key_auth

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Pydantic Models ---
# These models acts like our "Public Contract."
# Any change here needs to be addressed accordingly on the frontend side.


class UploadResponse(BaseModel):
    image_id: str


class AnalysisRequest(BaseModel):
    image_id: str


class AnalysisResponse(BaseModel):
    image_id: str
    skin_type: str
    issues: List[str]
    confidence: float


# --- Our Endpoints ---
@router.post(
    "/upload", response_model=UploadResponse, dependencies=[Depends(api_key_auth)]
)
async def upload_image(file: UploadFile = File(...)):
    """Entry point for user uploads.
    Uploads an image and returns a unique image_id."""

    # Basic sanity check. FastAPI's UploadFile is usually reliable,
    # but we guard against edge cases where the client might send an empty multipart request.
    if file.filename is None or file.content_type is None:
        logger.error("Upload attempt with missing filename or content type.")
        raise HTTPException(
            status_code=400,
            detail="Invalid file upload: Missing filename or content type.",
        )

    content = await file.read()

    # 2. Passes off validated strings to the storage service
    image_id = await storage.save_file(
        file_content=content, filename=file.filename, content_type=file.content_type
    )

    return {"image_id": image_id}


@router.post(
    "/analyze", response_model=AnalysisResponse, dependencies=[Depends(api_key_auth)]
)
async def analyze_image(request: AnalysisRequest):
    """Retrieves analysis results for a specific image_id."""
    try:
        # Verify if the file exists locally first
        await storage.get_file_path(request.image_id)
    except HTTPException:
        # Re-raise known HTTP exceptions from the storage service
        raise
    except Exception as e:
        logger.error(f"Error checking file path: {str(e)}")
        raise HTTPException(status_code=404, detail="Unknown image_id.")

    result = await analysis.perform_analysis(request.image_id)
    return result
