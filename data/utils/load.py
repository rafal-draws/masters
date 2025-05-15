import pandas as pd
import datetime
import os
import librosa as li
import torch.nn as nn

from . import feature_extraction

    
def import_data_science(scope):
    #todo add docstring
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import IPython.display as ipd
    import librosa as li
    import os as os

    scope['pd'] = pd
    scope['np'] = np
    scope['plt'] = plt
    scope['ipd'] = ipd
    scope['os'] = os
    scope['li'] = li

def find_file_by_upload_id(upload_id, upload_dir):

    files = os.listdir(upload_dir)
    actual_file = ""
    
    for file in files:
        split = file.split("-")
        if upload_id in split[-1]:
            actual_file=file
        else:
            print("Upload couldn't be found")
            
    return f"{upload_dir}{actual_file}"

def extract_signal_for_inference(filename_absolute_path):
    y, sr = li.load(filename_absolute_path)
    
    if feature_extraction.assert_at_least_minute(y, sr):
        try:
            y = feature_extraction.get_from_middle(y, sr, 15) # takes in signal, gets middle index, grabs 15//2 secs from each side
            y = feature_extraction.normalize_audio(y) # normalizes signal -1:1
            y = feature_extraction.get_hanned(1, y, sr, False)
            return y, sr
        except Exception as e:
            print(f"Error during slicing a record to a minute! {e}")
    else:
        print(f"Record {path} was not long enough.")



def load_records_dataset():
    pd.read_csv("datasets/records_ready.csv")

def load_music_dataset():
    return pd.read_json(check_os_get_artifacts_path() + "master_train.json") 


def load_fma_full():
    import os
    import re
    files = os.listdir("datasets")
    for file in files:
        if "fma_full" in file:
            latest = file
            break
    print(latest)
    return pd.read_csv(f"datasets/{latest}")

def load_tracks_with_paths():
    import os
    import re
    artifacts = check_os_get_artifacts_path()
    files = os.listdir(artifacts)
    for file in files:
        if "tracks_with_path" in file:
            latest = file
            break
    print(latest)
    return pd.read_parquet(f"{artifacts}{latest}")

def save_dataset(a: pd.DataFrame, name: str) -> str:
    
    _datasets = "datasets/"
    _artifacts = check_os_get_artifacts_path()
    _td = datetime.datetime.now().strftime("%y-%m-%d-%H%M")
    
    a.to_csv(f"{_datasets}/{name}.csv")
    a.to_parquet(f"{_artifacts}/{name}_{_td}.parquet")

def check_os_get_artifacts_path():
    #todo add docstring
    #todo tune
    import platform
    if platform.system() == "Windows":
        data_path = "G:\\artifacts\\"
    elif platform.system() == "Linux":
        data_path = "/mnt/g/artifacts/"       
    else: 
        print("undefined os")

    return data_path

def check_os_get_fma_metadata_path():
    #todo add docstring
    #todo tune
    import platform
    if platform.system() == "Windows":
        data_path = "G:\\fma_metadata"
    elif platform.system() == "Linux":
        data_path = "/mnt/g/fma_metadata"       
    else: 
        print("undefined os")

    return data_path


def check_os_get_root_path():
    #todo add docstring
    #todo tune
    import platform
    if platform.system() == "Windows":
        data_path = "G:\\"
    elif platform.system() == "Linux":
        data_path = "/mnt/g/"       
    else: 
        print("undefined os")

    return data_path

def load_random_sample(data_path: str):
    #todo add docstring
    import librosa
    import os
    import random
    song = random.choice(os.listdir(f"{data_path}/001/"))
    
    y, sr = librosa.load(f"{data_path}/001/{song}")
    print(f"song loaded: {song}")
    return y, sr