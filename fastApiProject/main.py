import os

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import zipfile
from io import BytesIO
from PIL import Image

from ai import is_valid_image

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_image = "data/base.jpeg"
comment_images =  ["data/comment/comment_1.jpeg"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/base-image/")
async def get_base_image():
    image_path = "data/base.jpeg"  # Specify your image path here

    # Check if the file exists
    if not os.path.exists(image_path):
        return {"error": "Image not found"}

    # Return the image file
    return FileResponse(image_path, media_type="image/jpeg")

@app.get("/get-images/")
async def get_images():
    image_dir = "data/comment/"  # Replace with your directory path

    # Create a zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for image_file in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image_file)
            zip_file.write(image_path, image_file)

    zip_buffer.seek(0)

    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=images.zip"})

@app.post("/upload-image/")
async def upload_comment(file: UploadFile = File(...)):
    content = await file.read()
    save_directory = "data/comment/"

    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, file.filename)
    convertedImage = Image.open(BytesIO(content))

    if is_valid_image(base_image, comment_images, convertedImage):
        with open(file_path, "wb") as f:
            comment_images.append(f'data/comment/{file.filename}')
            f.write(content)
        return {"status": "success"}

    return {"status": "failure"}



