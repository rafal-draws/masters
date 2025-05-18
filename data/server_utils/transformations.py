import os
import librosa as li
import numpy as np
import soundfile as sf

import matplotlib.pyplot as plt
import matplotlib

from . import utilities


def generate_audio_from_frames(filename: str, signal, sampling_rate, artifacts_path):
    if filename.endswith(".mp3"):
        x = filename.replace(".mp3", ".wav")
    sf.write(utilities.normalize_path(f"{artifacts_path}/slices/{x}"), signal, sampling_rate)
    return f"{artifacts_path}/slices/{x}"

def generate_npy_array_from_frames(filename: str, signal, artifacts_path, logger):

    logger.info(filename)

    if filename.endswith(".mp3"):
        x = filename.replace(".mp3", ".npy")

    if filename.endswith(".wav"):
        x = filename.replace(".wav", ".npy")

    with open(f'{artifacts_path}/transformed_signals/{x}', 'wb') as f:
        np.save(f, signal)

    return f"{artifacts_path}/transformed_signals/{x}"



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


def extract_mels_and_generate_artifacts(frames, signal: np.array, filename: str, artifacts_dir: str, frame_size: int, song_location: str, logger):
    logger.info("Extracting mels")
    mels = extract_mels(frames, signal)
    logger.info("generating mel images")
    generate_mel_spec_images(filename, mels, artifacts_dir)
    logger.info("generating mel video")
    mp4 = generate_video_from_mel_spec_images(filename, song_location, len(frames), artifacts_dir)
    return mp4

def extract_power_spectrograms_and_generate_artifacts(frames, signal: np.array, filename: str, artifacts_dir: str, frame_size: int, song_location: str, logger):
    logger.info("Extracting power spectrograms")
    power_spectrograms = extract_power_spectrograms(frames, signal)
    logger.info("Generating power spectrograms images")
    generate_power_spectr_spec_images(filename, power_spectrograms, artifacts_dir)
    logger.info("Generating a video")
    mp4 = generate_video_from_power_spetr_images(filename, song_location, len(frames), artifacts_dir)

    return mp4

def extract_mfcc_and_generate_artifacts(frames, signal: np.array, filename: str, artifacts_dir: str, frame_size: int, song_location: str, logger):
    logger.info("Extractings mfccs")
    mfcc = extract_mfccs(frames, signal)
    logger.info("Generating mfcc images")
    generate_mfcc_images(filename, mfcc, artifacts_dir)
    logger.info("Genearting mfcc video")
    mp4 = generate_video_from_mfcc_images(filename, song_location, len(frames), artifacts_dir)
    return mp4




def generate_mel_spec_images(filename, song_mels, server_data_path):
    
    matplotlib.use('Agg')
    
    fmin = 0
    fmax = 8000
    vmin = -80  # common min for dB
    vmax = 0 
    
    fig = plt.figure()
    
    for index, i in enumerate(song_mels):
        fig, ax = plt.subplots()
        S_dB = li.power_to_db(i, ref=np.max)
        img = li.display.specshow(S_dB,
                          x_axis='frames',
                          y_axis='mel',
                          sr=22050,
                          fmax=fmax,
                          ax=ax,
                          vmin=vmin, vmax=vmax)  # fix color scale

        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set(title='Mel-frequency spectrogram')
        plt.savefig(utilities.normalize_path(f"{server_data_path}/mels/{filename}-{index}.png"))
        plt.close(fig)


def generate_video_from_mel_spec_images(filename, song_filename, frames_length, server_data_path):
    
    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {server_data_path}/mels/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{server_data_path}/videos/mel-{filename}.mp4"
    )

    return f"{server_data_path}/videos/mel-{filename}.mp4"


def generate_power_spectr_spec_images(filename, power_spectrograms, server_data_path):
    vmin = 0
    vmax = 1
    
    
    for index, i in enumerate(power_spectrograms): ## TODO FIXIT
        fig = plt.figure()

        li.display.specshow(i, y_axis='chroma', x_axis='time', 
                          # fmax=fmax,
                          vmin=vmin, vmax=vmax)
        plt.colorbar()  # optional, shows scale
        plt.title("Chroma Power Spectrogram (Short Fourier Transform)")
        plt.savefig(f"{server_data_path}/power/{filename}-{index}.png")
        plt.close(fig)

def generate_video_from_power_spetr_images(filename: str, song_filename, frames_length, server_data_path):

    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {server_data_path}/power/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{server_data_path}/videos/power-{filename}.mp4"
    )

    return f"{server_data_path}/videos/power-{filename}.mp4"



def generate_mfcc_images(filename, mfccs, server_data_path):

    # global_min = min(mfcc.min() for mfcc in mfccs)
    # # global_max = max(mfcc.max() for mfcc in mfccs)
    # global_max = 1000
    
    for index, i in enumerate(mfccs): 
        fig = plt.figure()

        li.display.specshow(i, x_axis='time', 
                            # vmin=global_min,
                            # vmax=global_max
                           )
        plt.ylim(0, 20)
        plt.colorbar()  # optional, shows scale
        plt.title("Mel-Frequency Cepstral Coefficients (MFCCs)")
        plt.savefig(f"{server_data_path}/mfcc/{filename}-{index}.png")
        plt.close(fig)


def generate_video_from_mfcc_images(filename, song_filename, frames_length, server_data_path):
    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {server_data_path}/mfcc/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{server_data_path}/videos/mfcc-{filename}.mp4"
    )

    return f"{server_data_path}/videos/mfcc-{filename}.mp4"


def extract_mels(frames_indexes, signal: np.array, sr: int = 22050, fft_window: int = 256, feature_shape: int = 20):
    mels = []
    for i in frames_indexes:
        current_frame = signal[i[0]:i[1]]
        mels.append(li.feature.melspectrogram(y=current_frame, sr=sr, n_fft=fft_window, n_mels=feature_shape))
    
    return np.array(mels)

def extract_power_spectrograms(frames_indexes, signal: np.array, sr: int = 22050, feature_shape: int = 20):
    power_spectograms = []
    for i in frames_indexes:
        current_frame = signal[i[0]:i[1]]
        power_spectograms.append(li.feature.chroma_stft(y=current_frame, sr=sr, n_chroma=feature_shape))
    
    return np.array(power_spectograms)

def extract_mfccs(frames_indexes, signal: np.array, sr: int = 22050, feature_shape: int = 20):
    mels = []
    for i in frames_indexes:
        current_frame = signal[i[0]:i[1]]
        mels.append(li.feature.mfcc(y=current_frame, sr=22050, n_mfcc=feature_shape))
    
    return np.array(mels)


def split_signal_to_frame_indexes(frame_size: int, hop_size: int, signal: np.array):
    """
    takes in frame size, hop size, signal (1 dim array of floats)

    returns list of tuples of frame indexes of (frame_size - hop_size, frame_size)
    """
    try:
        frame_count = signal.shape[0] // frame_size 
        
        
        frames = []
        for i in range (0, frame_count):
            if i == 0:
                start, stop = 0, frame_size + hop_size
            else:
                start, stop = (i*frame_size - hop_size, (i+1)*frame_size)
        
            frames.append((start,stop))
        return frames
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return np.nan