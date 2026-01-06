import logging
import uuid
from pathlib import Path

from fastapi import HTTPException

# Standard logger setup; using __name__ to keep logs scoped to this module for easier debugging later
logger = logging.getLogger(__name__)

# Ensures the upload directory exists on startup.
# in typical production environment, we would point this
# to a persistent volume mount like S3 buckets, google Cloud storage.
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# using a 5MB limit a a placeholder, it can be changed based on file constraints;
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]


async def save_file(file_content: bytes, filename: str, content_type: str) -> str:
    # We validate MIME type strictly to prevent users from uploading executable scripts disguised as images.
    if content_type not in ALLOWED_MIME_TYPES:
        logger.error(f"Invalid file type: {content_type}")
        raise HTTPException(
            status_code=400, detail="Only JPEG and PNG images are allowed."
        )

    # Ensures that the file size is within the limit set, we don't want any memory exhaustion attacks (DoS).
    if len(file_content) > MAX_FILE_SIZE:
        logger.error(f"File too large: {len(file_content)} bytes")
        raise HTTPException(status_code=400, detail="File size exceeds the 5MB limit.")

    # Using UUID4 to ensure randomness, this prevent user guessing and uniquely identifes each file..
    file_id = str(uuid.uuid4())
    file_extension = Path(filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_extension}"

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        logger.info(f"File saved successfully: {file_id}")
        return file_id
    except Exception as e:
        # Log the full error locally whiles giving the client a clean message.
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during file storage."
        )


async def get_file_path(image_id: str) -> Path:
    for f in UPLOAD_DIR.iterdir():
        # Matches the UUID prefix regardless of the extension (jpg/png).
        if f.name.startswith(image_id):
            return f
    raise HTTPException(status_code=404, detail=f"Image ID {image_id} not found.")
