# Image Processing Backend for Mobile

This is a FastAPI-based backend service designed to handle mobile image uploads and perform mock skin analysis with relevant json results. It demonstrates professional backend patterns like asynchronous request handling, structured data validation, and secure API key authentication.

## How to Run on your local machine

### Option A: Using `uv` (Recommended)

This project is optimized for `uv` for lightning-fast dependency management and environment isolation.

1. **Prerequisites**: Ensure you have `uv` installed. You can install it conveniently via `pip` using PowerShell or your terminal:

```
pip install uv
```

For more details, check the [official installation reference](https://docs.astral.sh/uv/getting-started/installation/#pypi).
2. **Sync & Start**:

```
# Sync dependencies and create virtual environment
uv sync

# Start the server
uv run uvicorn app.main:app --reload
```

### Option B: Using `pip` & Virtual Environments

If you prefer standard Python tools, follow these steps:

1. **Create Virtual Environment**:

```
python -m venv venv
# Activate on Windows:
.\venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```
2. **Install Dependencies**:

```
pip install fastapi uvicorn python-multipart python-dotenv
```
3. **Start the Server**:

```
uvicorn app.main:app --reload
```

## API Key Configuration

Create a `.env` file in the project root to store your API key:

```
API_KEY=your_secret_key_here
```

The service will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## The Available Endpoints

All endpoints require the `X-API-Key` header for authentication.

### 1. Upload Image

`POST /upload`

- **Body**: `multipart/form-data` with a `file` field.
- **Validation**: Accepts JPEG/PNG only. Max size 5MB.
- **Response**: `{ "image_id": "uuid-string" }`

### 2. Analyze Image

`POST /analyze`

- **Body**: `{ "image_id": "uuid-string" }`
- **Response**: `{ "image_id": "...", "skin_type": "...", "issues": [...], "confidence": 0.87 }`
- **Note**: The analysis is mock logic. Specific results can be triggered by using prefixes like `mock_oily` or `mock_dry` in the image ID.

##  Why I built it this way (Assumptions)

- **Safety First**: I included basic API Key security and made sure error messages don't leak private server info to the public.
- **Memory-First Processing**: Since files are small (under 5MB), I keep them in memory during the upload. It's much faster than writing to a temp file first.  I assume that reading the file directly into memory is the most performant choice for low-latency responses, though a streaming approach would have been mandatory for very high-resolution imaging.
- **Simple Storage**: I used the local filesystem as a "mini-database.". The system assumes the local filesystem acts as its registry, if the file exists in the `uploads` folder then the ID is valid. This keeps the project lightweight and easy to run.
- **Smart Errors**: I assume that "Detailed Errors" are for us developers, not clients. The app returns simple messages like `Unknown image_id` to the user so we don't accidentally reveal how our server's internal folders are structured.
- **Temporary Files**: I'm treating the `uploads` folder as a temporary workspace. I prioritized making the files available immediately for analysis rather than worrying about long-term archival for this mock setup.
**Stateless Auth**: I used a "Shared Secret" (API Key) because it's simple and lets the server stay stateless. This means we can easily scale up to handle more users without needing a complex database just to check who is logged in.


## Areas for Production Improvement

If this were a production-level service, I would implement the following:

1. **Non-Blocking I/O**: Right now, the server waits for files to finish writing to the disk before doing anything else. In a real app, I'd use `aiofiles` or background workers so the API stays snappy even when lots of people are uploading at once.
2. **Database Integration**: Instead of the "slow O(N)" approach of scanning every file in a folder to find an image, I’d use a database like PostgreSQL. This makes finding data near-instant (O(1)) and keeps things organized as the app grows.
3. **Streaming Uploads**: For bigger files, I would stream the data directly to storage instead of loading it all into RAM first. This prevents the server from running out of memory and crashing when users upload high-quality photos.
4. **Cloud Storage**: : I will migrate from the local file system to a scalable object store like AWS S3, Google Cloud Storage, oe even Supabase. These services handle persistence and scaling automatically so we never lose a user's image.
5. **Rate Limiting**: I'd add "throttling" (probably using Redis) to stop people from spamming the API. This protects us from brute-force attacks on the API key and ensures the server doesn't get overwhelmed during traffic spikes.
6. **Containerization & Secure Cloud**:

- **Docker Setup**: I'd wrap the app in a Docker container so it runs exactly the same way on my machine, your machine, and the cloud. It's the best way to kill "it works on my machine" bugs.
- **Secret Management**: Instead of a `.env` file, I’d use a proper Secret Manager (like AWS Secrets Manager). This keeps our keys encrypted and safe, rather than sitting in plain text on a server.
