from dotenv import load_dotenv
import os

from typing import Annotated
from fastapi import FastAPI, HTTPException, Header

from server_utils import utilities, transformations

import platform 

load_dotenv()

if platform.system() == "Linux":
    server_data_location = os.getenv("SERVER_DATA")
else:
    server_data_location = "G:\\server_data"

app = FastAPI(title=os.getenv("APP_NAME"))
logger = utilities.setup_logging(True)


@app.get("/")
def read_root():
    return {
        "hi"
    }

@app.post("/transform/check/{file_name}")
def transform_item(file_name: str):
    try:
        file_found = utilities.normalize_path(
            transformations.find_file_by_upload_id(file_name, f"{server_data_location}/uploads", logger)
            )

        if file_found is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {
            "progress": "7%",
            "file_found": file_found
        }
    except HTTPException as e:
        raise e 
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.post("/transform/")
def transform_item(file_path: Annotated[str | None, Header()] = None,
                   filename: Annotated[str | None, Header()] = None):
    

    try:
        file_path = utilities.normalize_path(file_path)
        filename = filename

        logger.info(file_path)
        signal, sr = transformations.extract_signal_for_inference(filename_absolute_path=file_path,
                                                                  length=15,
                                                                  logger=logger)
        logger.info(f"{filename} - TRANSFORMED")
        sound_location = transformations.generate_audio_from_frames(filename=filename,
                                                                     signal=signal,
                                                                     sampling_rate=sr,
                                                                     artifacts_path=server_data_location)
        logger.info(f"SOUND FILE LOCATION: {sound_location}")

        

        if file_path or filename is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {

        }
    except HTTPException as e:
        raise e 
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")