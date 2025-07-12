from back_end.config_settings import IMAGES_FOLDER
from src.image_store import ImageStore
from src.components import IMAGE_SERVER_PORT
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException

image_manager = ImageStore(IMAGES_FOLDER)

app = FastAPI()

app.state.image_manager = image_manager

@app.get("/get_image")
async def get_image(request: Request, filename: str):
    image_manager = request.app.state.image_manager

    image_response = image_manager.get_image_response(filename)
    if image_response is not None:
        return image_response
    else:
        raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=IMAGE_SERVER_PORT, reload=True)