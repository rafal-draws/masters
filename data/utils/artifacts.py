import datetime
import json
import inspect
import pandas as pd

def generate_artifacts(artifacts_path: str, dataframe: pd.DataFrame, *args):
    
    data = {}

    data['date'] = datetime.datetime.now().strftime("%DT%TZ")
    data['columns'] = dataframe.columns
    data['shape'] = dataframe.shape
    data['nulls'] = dataframe.isnull().count()
    data['describe'] = dataframe.describe().to_json()
    data['stack'] = inspect.stack()[1]
    data['head'] = dataframe.head().to_json()
    
    for arg in args:
        if callable(arg):
            data[f'{arg}'] = arg()
        else:
            data[f'{arg}'] = arg
    
    # with open(f"{artifacts_path}/{datetime.datetime.now().strftime("%y%m%d")}.log", "a") as logfile:
    #         logfile.write(str(data))


# todo fix visualisation
def visualise(xtime: bool, hop_length: int, *args):
    import random
    import numpy as np
    import matplotlib.pyplot as plt
    import librosa

    colors = ["r", "g", "b", "m"]

    try:
        plt.figure(figsize=(12, 3))
        plt.subplots_adjust(hspace=0.3)

        for count, data in enumerate(args):
            plt.subplot(len(args), 1, count + 1)

            if not isinstance(data, np.ndarray):
                raise ValueError(f"Argument {count} is not a numpy array!")

            if xtime:
                frames = range(len(data))
                t = librosa.frames_to_time(frames, hop_length=hop_length)

                plt.plot(t, data, color=random.choice(colors))
                plt.title(f"Signal {count + 1} (with time axis)")
                plt.xlabel("Time (s)")
            else:
                plt.plot(data, color=random.choice(colors))
                plt.title(f"Signal {count + 1} (sample index)")

            plt.ylim((-1, 1))

        plt.show()

    except Exception as e:
        print(f"Exception occurred: {e}")
            

    

