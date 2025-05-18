import os
import librosa as li
import numpy as np
import soundfile as sf


def generate_audio_from_frames(filename, signal, sampling_rate, artifacts_path):
    sf.write(f"{artifacts_path}slices/{filename}.wav", signal, sampling_rate)
    return f"{artifacts_path}slices/{filename}.wav"




def find_file_by_upload_id(upload_id, upload_dir, logger):

    files = os.listdir(upload_dir)
    logger.info(files)
    actual_file = ""
    
    for file in files:
        logger.info(file)
        try: 
            if file.startswith(upload_id):
                actual_file=file
                logger.info(actual_file)
                return f"{upload_dir}/{actual_file}"
        except:
            return FileNotFoundError


def extract_signal_for_inference(filename_absolute_path, length, logger):

    logger.info(f"{filename_absolute_path} found, extracting init")
    logger.info(os.path.isfile(filename_absolute_path))
    y, sr = li.load(filename_absolute_path)
    logger.info(f"{filename_absolute_path} found, extraction completed")
    

    if assert_at_least_minute(y, sr):
        
        logger.info(f"{filename_absolute_path} is at least one minute long")
        try:
            y = get_from_middle(y, sr, length) # takes in signal, gets middle index, grabs 15//2 secs from each side
            logger.info(f"{filename_absolute_path} - Extracted {length} from middle")
            
            y = normalize_audio(y) # normalizes signal -1:1
            
            logger.info(f"{filename_absolute_path} - normalized")
            y = get_hanned(1, y, sr, False)

            logger.info(f"{filename_absolute_path} - hanned")

            
            logger.info(f"returning {filename_absolute_path} as signal ")
            return y, sr
        except Exception as e:
            print(f"Error during slicing a record to a minute! {e}")
    else:
        print(f"Record {filename_absolute_path} was not long enough.")

def assert_at_least_minute(y, sr):
    
    if len(y) / sr > 60:
        return True
    else:
        return False
    
def get_from_middle(y: np.ndarray, sr: int, amount: int) -> np.ndarray:
    
    mid_song_index = len(y)//2
    start = mid_song_index - ((amount//2) * sr)
    end = mid_song_index + ((amount//2) * sr)
    
    return y[start:end]

def normalize_audio(y: np.ndarray) -> np.ndarray:
    return y / np.max(np.abs(y))

def get_hanned(seconds: int, y, sampling_rate: int, debug: bool) -> np.ndarray :
    
    samples_amount = seconds * sampling_rate

    window = np.hanning(samples_amount)

    y_start = y[:samples_amount] * window 
    y_end = y[-samples_amount:] * window
    
    mid_sample_index = len(y_start)//2
    y_start = y_start[:mid_sample_index]
    y_end = y_end[mid_sample_index:]

    y_mod = np.copy(y)
    y_mod[0:len(y_start)] = y_start
    y_mod[-len(y_end):] = y_end
    
    
    return y_mod
