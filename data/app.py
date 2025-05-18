import os
import json
import numpy as np

from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv

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
    

@app.post("/transform/step_1")
def transform_item_step_1(file_path: Annotated[str | None, Header()] = None,
                   filename: Annotated[str | None, Header()] = None):
    

    try:
        file_path = utilities.normalize_path(file_path)
        filename = filename

        logger.info(file_path)
        signal, sr = transformations.extract_signal_for_inference(filename_absolute_path=file_path,
                                                                  length=15,
                                                                  logger=logger)
        logger.info(f"transformed signal: {signal}, {signal.shape}")
        logger.info(f"{filename} - TRANSFORMED")

        slice_nparray = transformations.generate_npy_array_from_frames(filename=filename,
                                                                        signal=signal,
                                                                        artifacts_path=server_data_location,
                                                                        logger=logger)
        
        logger.info(f"slice np array is under {slice_nparray}")

        sound_location = transformations.generate_audio_from_frames(filename=filename,
                                                                     signal=signal,
                                                                     sampling_rate=sr,
                                                                     artifacts_path=server_data_location)
        logger.info(f"SOUND FILE LOCATION: {sound_location}")
        


        return {
            "progress": "34%",
            "sound_location": utilities.normalize_path(sound_location),
            "signal": utilities.normalize_path(slice_nparray),
            "sampling_rate": sr,
            "filename": filename
        }
        
    except HTTPException as e:
        raise e 
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    




@app.post("/transform/step_2")
def transform_item_step_2(sound_location: Annotated[str | None, Header()] = None,
                   signal: Annotated[str | None, Header()] = None,
                   frame_size: Annotated[str | None, Header()] = None,
                   hop_size: Annotated[str | None, Header()] = None,
                   filename: Annotated[str | None, Header()] = None):
    

    try:
        sound_location = utilities.normalize_path(sound_location)
        signal_location = utilities.normalize_path(signal)
        frame_size = int(frame_size)
        hop_size = int(hop_size)

        logger.info(sound_location)
        logger.info(signal)

        with open(signal, 'rb') as f:
            signal_np = np.load(signal_location)

        logger.info(signal_np.shape)

        frames = transformations.split_signal_to_frame_indexes(frame_size, hop_size, signal_np)

        mels_mp4 = transformations.extract_mels_and_generate_artifacts(
            frames = frames,
            frame_size = frame_size,
            signal = signal_np,
            filename = filename,
            artifacts_dir=server_data_location,
            song_location=sound_location,
            logger = logger
        )

        power_mp4 = transformations.extract_power_spectrograms_and_generate_artifacts(
            frames = frames,
            frame_size = frame_size,
            signal = signal_np,
            filename = filename,
            artifacts_dir=server_data_location,
            song_location=sound_location,
            logger = logger
        )

        mfcc_mp4 = transformations.extract_mfcc_and_generate_artifacts(
            frames = frames,
            frame_size = frame_size,
            signal = signal_np,
            filename = filename,
            artifacts_dir=server_data_location,
            song_location=sound_location,
            logger = logger
        )



        return {
            "progress": "45%",
            "sound_location": sound_location,
            "signal": signal,
            "power_mp4": power_mp4,
            "mel_mp4": mels_mp4,
            "mfcc_mp4": mfcc_mp4
        }
        
    except HTTPException as e:
        raise e 
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

