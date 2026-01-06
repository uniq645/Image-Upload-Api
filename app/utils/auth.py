import os

from dotenv import load_dotenv  #
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# using dotenv to load variables from the .env file at the root directory
load_dotenv()

# We pull the API_KEY from the environment to avoid hardcoding credentials in the repo.
# If the key is missing, this app will fail on startup. This is intentional to prevent unauthenticated access.
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def api_key_auth(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return True
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
