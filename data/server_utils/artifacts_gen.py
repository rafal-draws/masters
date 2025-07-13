import librosa 
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os 
import subprocess
from pathlib import Path


def assert_signal_length(y, sr, length):
    #todo add docstring
    if (len(y) / sr) > length:
        return True
    else:
        return False

def get_from_middle(y: np.ndarray, sr: int, amount: int) -> np.ndarray:
    
    if amount != 1:
        mid_song_index = len(y)//2
        start = mid_song_index - ((amount//2) * sr)
        end = mid_song_index + ((amount//2) * sr)
        
        
        return y[start:end]
    else:
        mid_song_index = len(y)//2
        start = mid_song_index - (sr // 2 )
        end = mid_song_index + (sr // 2)
        
        return y[start:end]


### ============= IO OPERATIONS

def validate_audio_files(server_data, upload_id):
    """
    Validate audio files in the server_data directory.
    """

    uploads = os.path.join(server_data, "uploads")
    
    
    audio_files = [f for f in os.listdir(uploads) if f.endswith('.wav') or f.endswith('.mp3') and f.startswith(upload_id)]
    
    
    
    return audio_files

def infer_signals(track):
    """
    Infer signals from audio tracks.
    """
    try:
        y, sr = librosa.load(track, sr=22050)
        return y
    except Exception as e:
        print(f"Error inferring signals for {track}: {e}")
        return None
    
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

def normalize_audio(y: np.ndarray) -> np.ndarray:
    return y / np.max(np.abs(y))


def extract_y_middle(y, seconds):
        """
        takes in path of a file, loads it, and returns a ndarray of samples
        """
        
        if assert_signal_length(y, 22050, seconds):
            
                # extract signal length * 22050
                y = get_from_middle(y, 22050, seconds)
                y = get_hanned(1, y, 22050, False)

                # normalization [0.0:1.0]
                y = normalize_audio(y)

                print(f"Record was sliced successfully.")
                print(f"Length of y_minute: {len(y)}")
                print(f"Length of y: {len(y) / 22050} seconds")
                print(f"y.max: {np.max(y)}")
                print(f"y.min: {np.min(y)}")
                print(f"y.mean: {np.mean(y)}")
                print(f"y.std: {np.std(y)}")
                print(f"y.shape: {y.shape}")
                return y
        else:
            print(f"Record {y} was not long enough.")
            raise ValueError("Validation wasn't executed properly")
        
import soundfile as sf

def generate_audio_from_frames(filename: str, signal, sampling_rate, server_data):
    
    os.makedirs(os.path.join(server_data, "30s"), exist_ok=True)
    
    
    if filename.endswith(".mp3"):
        filename = filename.replace(".mp3", ".wav")
    
    
    try:
        file_path = os.path.join(server_data, "30s", filename)
        sf.write(file_path, signal, sampling_rate)
        print(f"Audio file {file_path} generated successfully.")
    except Exception as e:
        print(f"Error generating audio file {file_path}: {e}")
    
    return os.path.join(server_data, "30s", filename)


def split_to_frames(y, frame_length=22050, hop_length=11025):
    """
    Split the audio signal into frames.
    """

    frames_amount = y.shape[0] // 22050
    
    if frames_amount < 1:
        print("Audio signal is too short to split into frames.")
        return []

    [x*11025 for x in range(1, frames_amount * 2 + 1)]
    if y is None or len(y) == 0:
        print("No audio signal provided.")
        return []
    
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length).T
    return frames


def save_feature_to_server_data(feature_name: str, server_data, upload_id, feature):
    
    upload_dir = os.path.join(server_data, "features", upload_id, feature_name)
    print(upload_dir)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    with open(f"{os.path.join(upload_dir)}/{feature_name}.npy", "wb") as f:
        np.save(f, feature)

    print(os.listdir(upload_dir))
    
        


### =============  IO OPERATIONS



### =============== SIGNALS TRANSFORMATIONS


def transform_to_ft(frames, metadata_path, normalized: bool):
    ft = []
    
    for i, frame in enumerate(frames):
        ft.append(np.abs(librosa.stft(frame, hop_length=256)))
        
    
    ft = np.array(ft).astype(np.float32)
    
    print(f"Shape of ft: {ft.shape}")
    print(f"Min/max of ft: {np.min(ft)}/{np.max(ft)}")
    
    if normalized:
        ft_mean = np.load(os.path.join(metadata_path, "ft_mean.npy"))
        ft_std = np.load(os.path.join(metadata_path, "ft_std.npy"))
    

        ft = np.log1p(ft)
        
        ft_mean = np.mean(ft, axis=(0, 1), keepdims=True)
        X = (ft - ft_mean) / (ft_std + 1e-8)

    else: 
        X = ft    
    
    print(f"Shape of ft normalized: {X.shape}")
    print(f"Min/max of ft normalized: {np.min(X)}/{np.max(X)}")
            
    return X


def transform_to_spectr(frames, metadata_path, normalized: bool):
    spectr = []
    
    for i, frame in enumerate(frames):
       spectr.append(librosa.amplitude_to_db(
                np.abs(librosa.stft(frame, hop_length=256)), ref=np.max))
    
    spectr = np.array(spectr).astype(np.float32)
    
    
    print(f"Shape of spectrogram: {spectr.shape}")
    print(f"Min/max of spectrogram: {np.min(spectr)}/{np.max(spectr)}")
    
    if normalized:
        spectr_mean = np.load(os.path.join(metadata_path, "spec_mean.npy"))
        spectr_std = np.load(os.path.join(metadata_path, "spec_std.npy"))
            
        spectr = (spectr - spectr_mean) / (spectr_std)
        
        print(f"Shape of spectrogram normalized: {spectr.shape}")
        print(f"Min/max of spectrogram normalized: {np.min(spectr)}/{np.max(spectr)}")
                
    return spectr


def transform_to_mel_spectr(frames, metadata_path, normalized: bool):
    spectr = []
    
    for i, frame in enumerate(frames):
       
        mel_spect = librosa.feature.melspectrogram(
                y=frame, sr=22050, n_fft=8192, hop_length=256, n_mels=1025)
        mel_spect = librosa.power_to_db(mel_spect, ref=np.max)

        spectr.append(mel_spect)
    
    spectr = np.array(spectr).astype(np.float32)
    
    
    print(f"Shape of mel spectrogram: {spectr.shape}")
    print(f"Min/max of mel spectrogram: {np.min(spectr)}/{np.max(spectr)}")
    
    if normalized:
        spectr_mean = np.load(os.path.join(metadata_path, "mel_spec_mean.npy"))
        spectr_std = np.load(os.path.join(metadata_path, "mel_spec_std.npy"))
            
        spectr = (spectr - spectr_mean) / (spectr_std)
        
        print(f"Shape of mel spectrogram normalized: {spectr.shape}")
        print(f"Min/max of mel spectrogram normalized: {np.min(spectr)}/{np.max(spectr)}")
                
    return spectr


def transform_to_power_spectr(frames, metadata_path, normalized: bool):

    spectr = []
    
    for i, frame in enumerate(frames):

        ft = librosa.stft(frame, hop_length=256)
        power_spec = np.abs(ft) ** 2
        power_db = librosa.power_to_db(power_spec, ref=np.max)
       
        spectr.append(power_db)
    
    spectr = np.array(spectr).astype(np.float32)
    
    
    print(f"Shape of power spectrogram: {spectr.shape}")
    print(f"Min/max of power spectrogram: {np.min(spectr)}/{np.max(spectr)}")
    
    if normalized:
        spectr_mean = np.load(os.path.join(metadata_path, "power_spec_mean.npy"))
        spectr_std = np.load(os.path.join(metadata_path, "power_spec_std.npy"))
            
        spectr = (spectr - spectr_mean) / (spectr_std)
        
        print(f"Shape of power spectrogram normalized: {spectr.shape}")
        print(f"Min/max of power spectrogram normalized: {np.min(spectr)}/{np.max(spectr)}")
                
    return spectr

def transform_to_mfcc(frames, metadata_path, normalized: bool):

    mfcc = []
    for i, frame in enumerate(frames):

        mfcc_x = librosa.feature.mfcc(
                y=frame, sr=22050, n_mfcc=12, hop_length=256)

        mfcc.append(mfcc_x)
    
    mfcc = np.array(mfcc).astype(np.float32)
    
    
    print(f"Shape of mfcc: {mfcc.shape}")
    print(f"Min/max of mfcc: {np.min(mfcc)}/{np.max(mfcc)}")
    
    if np.min(mfcc) <= -1.0 or np.max(mfcc) >= 1.0:
        print("Data needs normalization")

        if normalized:

            
            mfcc_mean = np.load(os.path.join(metadata_path, "mfcc_mean.npy"))
            mfcc_std = np.load(os.path.join(metadata_path, "mfcc_std.npy"))
            
            mfcc = (mfcc - mfcc_mean) / (mfcc_std)
            
            print(f"Shape of mfcc normalized: {mfcc.shape}")
            print(f"Min/max of mfcc normalized: {np.min(mfcc)}/{np.max(mfcc)}")
                
    return mfcc


def transform_to_chroma(frames, metadata_path, transformation:str, normalized: bool):

    chroma = []
    
    for i, frame in enumerate(frames):

        match transformation:
            case "stft":
                chroma_x = librosa.feature.chroma_stft(
                y=frame, sr=22050, n_chroma=12,
                hop_length=256, n_fft=2048)
            case "cens":
                chroma_x = librosa.feature.chroma_cens(
                y=frame, sr=22050, n_chroma=12,
                hop_length=512)

            case "cqt":
                chroma_x = librosa.feature.chroma_cqt(
                y=frame, sr=22050, n_chroma=12,
                hop_length=512)

        chroma.append(chroma_x)
    
    chroma = np.array(chroma).astype(np.float32)
    
    
    print(f"Shape of chroma {transformation} spectrogram: {chroma.shape}")
    print(f"Min/max of chroma {transformation} spectrogram: {np.min(chroma)}/{np.max(chroma)}")
    
    if np.min(chroma) <= -1.0 or np.max(chroma) >= 1.0:
        print("Data needs normalization")

        if normalized:

            chroma_mean = np.load(os.path.join(metadata_path, f"chroma_{transformation}_mean.npy"))
            chroma_std = np.load(os.path.join(metadata_path, f"chroma_{transformation}_std.npy"))
                
            chroma = (chroma - chroma_mean) / (chroma_std)
            
            print(f"Shape of chroma {transformation} normalized: {chroma.shape}")
            print(f"Min/max of chroma {transformation} normalized: {np.min(chroma)}/{np.max(chroma)}")
                
    return chroma

def transform_to_tonnetz(frames, metadata_path, normalized: bool):

    tonnetz = []
    
    for i, frame in enumerate(frames):

        
        chroma = librosa.feature.chroma_cqt(y=frame, sr=22050)
        tonnetz_x = librosa.feature.tonnetz(chroma=chroma, sr=22050)
        
        tonnetz.append(tonnetz_x)
    
    tonnetz = np.array(tonnetz).astype(np.float32)
    
    
    print(f"Shape of tonnetz: {tonnetz.shape}")
    print(f"Min/max of tonnetz: {np.min(tonnetz)}/{np.max(tonnetz)}")
    
    if np.min(tonnetz) <= -1.0 or np.max(tonnetz) >= 1.0:
        
        print("Data needs normalization")

        if normalized:
            tonnetz_mean = np.load(os.path.join(metadata_path, "tonnetz_mean.npy"))
            tonnetz_std = np.load(os.path.join(metadata_path, "tonnetz_std.npy"))
        
            tonnetz = (tonnetz - tonnetz_mean) / (tonnetz_std)
            
            print(f"Shape of tonnetz normalized: {tonnetz.shape}")
            print(f"Min/max of tonnetz normalized: {np.min(tonnetz)}/{np.max(tonnetz)}")
                
    return tonnetz


### =============== SIGNALS TRANSFORMATIONS



### ========= VIDEO GENERATION

def generate_video(server_data, upload_id, data_type, sample_location):
    
    match data_type:
        case "ft":
            
            print("ft_chosen")
            dir = os.path.join(server_data, "ft", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            print(f"list_of_files.__len__() {list_of_files.__len__()}")
            print(f"framerate: {framerate_real_time}")
            
            upload_dir = os.path.join(server_data, "ft", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            print(upload_dir)
            input_pattern = str(Path(dir) / "frame_%04d.png")
            

        case "spectr":
            
            print("spectr_chosen")
            dir = os.path.join(server_data, "spectr", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "spectr", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")

        case "mel_spectr":
            
            print("melspectr_chosen")
            dir = os.path.join(server_data, "mel_spectr", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "mel_spectr", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")

        case "power_spectr":
            
            print("power_spectr_chosen")
            dir = os.path.join(server_data, "power_spectr", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "power_spectr", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")
        
        case "mfcc":
            
            print("mfcc _ chosen")
            dir = os.path.join(server_data, "mfcc", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "mfcc", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")

        case "stft":
            
            print("stft _ chosen")
            dir = os.path.join(server_data, "stft", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "stft", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")

        case "cens":
            
            print("cens _ chosen")
            dir = os.path.join(server_data, "cens", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "cens", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")
        
        case "cqt":
            
            print("cqt _ chosen")
            dir = os.path.join(server_data, "cqt", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "cqt", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")
        
        case "tonnetz":
            
            print("tonnetz _ chosen")
            dir = os.path.join(server_data, "tonnetz", upload_id)
            list_of_files = sorted(os.listdir(dir))
            framerate_real_time = list_of_files.__len__() / 30
            
            print(f"framerate: {framerate_real_time}")
            upload_dir = os.path.join(server_data, "tonnetz", upload_id, "video")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            output = os.path.join(upload_dir, upload_id)
            
            print(upload_dir)
            
            input_pattern = str(Path(dir) / "frame_%04d.png")
        

        case _:
            raise ValueError(f"Unsupported data type: {data_type}")
            
        
    cmd = [
        "ffmpeg",
        "-framerate", f"{framerate_real_time:.2f}",
        "-y",
        "-i", input_pattern,
        "-i", sample_location,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        f"{output}.mp4"
    ]
    
    print("Running command:", ' '.join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed!", e)
        
    
### ========== IMAGE GENERATION    
        
def generate_ft_graphs(frames_ft, server_data, upload_id):
    """
    Generate and save ft images from the frames.
    """
    import matplotlib.pyplot as plt
    
    
    
    seconds_per_frame = 30 / frames_ft.__len__()

    if not os.path.exists(os.path.join(server_data, "ft")):
        os.makedirs(os.path.join(server_data, "ft"))
    
    if not os.path.exists(os.path.join(server_data, "ft", upload_id)):
        os.makedirs(os.path.join(server_data, "ft", upload_id))
    
    for i, ft in enumerate(frames_ft):
        plt.figure(figsize=(10, 4))
        plt.xlim(0, 512)
        plt.plot(ft)
        plt.xlabel('Hz')
        plt.ylabel('Amplituda')
        plt.xticks(np.arange(0, 513, 16))
        
        plt.grid(True)
        plt.title(f'Frame {i+1} | Fourier Transform ')
        plt.tight_layout()
        plt.savefig(os.path.join(server_data, "ft", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()
        
        
def generate_spectrogram_graphs(frames_spectr, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, "spectr")):
        os.makedirs(os.path.join(server_data, "spectr"))
    
    if not os.path.exists(os.path.join(server_data, "spectr", upload_id)):
        os.makedirs(os.path.join(server_data, "spectr", upload_id))
    
    for i, spectr in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(spectr, ax=ax,sr=22050, x_axis='time', y_axis='log')
        
        
        plt.title(f'Frame {i+1} | Spectrogram ')
        plt.savefig(os.path.join(server_data, "spectr", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()


def generate_mel_spectrogram_graphs(frames_spectr, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, "mel_spectr")):
        os.makedirs(os.path.join(server_data, "mel_spectr"))
    
    if not os.path.exists(os.path.join(server_data, "mel_spectr", upload_id)):
        os.makedirs(os.path.join(server_data, "mel_spectr", upload_id))
    
    for i, spectr in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(spectr, ax=ax,sr=22050, x_axis='time', y_axis='mel', fmax=8000)
        
        
        plt.title(f'Frame {i+1} | Mel Spectrogram ')
        plt.savefig(os.path.join(server_data,"mel_spectr", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()


def generate_power_spectrogram_graphs(frames_spectr, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, "power_spectr")):
        os.makedirs(os.path.join(server_data, "power_spectr"))
    
    if not os.path.exists(os.path.join(server_data, "power_spectr", upload_id)):
        os.makedirs(os.path.join(server_data, "power_spectr", upload_id))
    
    for i, spectr in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(spectr, ax=ax,sr=22050, x_axis='time', y_axis='hz', fmax=8000)
        
        
        plt.title(f'Frame {i+1} | Power Spectrogram ')
        plt.savefig(os.path.join(server_data,"power_spectr", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()


def generate_mfcc_graphs(frames_spectr, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, "mfcc")):
        os.makedirs(os.path.join(server_data, "mfcc"))
    
    if not os.path.exists(os.path.join(server_data, "mfcc", upload_id)):
        os.makedirs(os.path.join(server_data, "mfcc", upload_id))
    
    for i, mfcc in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(mfcc, ax=ax,sr=22050, x_axis='time')
        
        
        plt.title(f'Frame {i+1} | MFCC ')
        plt.savefig(os.path.join(server_data,"mfcc", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()


def generate_chroma_graphs(frames_spectr, transformation: str, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    if not transformation in ["cens", "cqt", "stft"]:
        raise ValueError(f"Given {transformation} as transformation, wrong paths will be produced. Aborting.")

    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, transformation)):
        os.makedirs(os.path.join(server_data, transformation))
    
    if not os.path.exists(os.path.join(server_data, transformation, upload_id)):
        os.makedirs(os.path.join(server_data, transformation, upload_id))
    
    for i, mfcc in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(mfcc, sr=22050,  x_axis='time', y_axis='chroma', cmap='coolwarm', ax=ax)
        
        plt.title(f'Frame {i+1} | Chroma ({transformation}) ')
        plt.savefig(os.path.join(server_data, transformation, upload_id, f'frame_{i+1:04d}.png'))
        plt.close()

def generate_tonnetz_graphs(frames_spectr, server_data, upload_id):
    """
    Generate and save spectrogram images from the frames.
    """
    import matplotlib.pyplot as plt
    
    seconds_per_frame = 30 / frames_spectr.__len__()
    
    if not os.path.exists(os.path.join(server_data, "tonnetz")):
        os.makedirs(os.path.join(server_data, "tonnetz"))
    
    if not os.path.exists(os.path.join(server_data, "tonnetz", upload_id)):
        os.makedirs(os.path.join(server_data, "tonnetz", upload_id))
    
    for i, tonnetz in enumerate(frames_spectr):
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        librosa.display.specshow(tonnetz, ax=ax,sr=22050, x_axis='time', y_axis='tonnetz', cmap='twilight_shifted')
        
        
        plt.title(f'Frame {i+1} | Tonnetz ')
        plt.savefig(os.path.join(server_data, "tonnetz", upload_id, f'frame_{i+1:04d}.png'))
        plt.close()

### ========= VIDEO GENERATION
