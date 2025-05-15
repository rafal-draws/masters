import numpy as np
import librosa as li
from . import artifacts_gen

def one_hot_function(row):
    match row:
        case "Rock":
            return 0
        case "Hip-Hop":
            return 1
        case "Electronic":
            return 2
        case "Pop":
            return 3
        case _:
            return 4


def reverse_one_hot(pred):
    match pred:
        case 0:
            return "Rock"
        case 1:
            return "Hip-Hop"
        case 2:
            return "Electronic"
        case 3:
            return "Pop"
        case _:
            return "Classical"


def split_signal_to_frame_indexes(frame_size: int, hop_size: int, signal: np.array):
    """
    takes in frame size, hop size, signal (1 dim array of floats)

    returns list of tuples of frame indexes of (frame_size - hop_size, frame_size)
    """
    try:
        frame_count = signal.shape[0] // frame_size 
        fft_window_length = frame_size + hop_size
        
        
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


def stack_mfcc_power_spectro_mel_spectro(mfccs: np.ndarray, mels: np.ndarray, power: np.ndarray):
    stacked = np.stack([mfccs, mels, power], dtype=object)

    return stacked


def signal_to_features(y: np.array, sr: int = 22050, frame_size = 4096,
                       hop_size = 512, fft_window = 256, signal_duration = 14,
                      feature_shape = 20):
    try:
        print(y.shape[0])
        
        frames = split_signal_to_frame_indexes(frame_size, hop_size, y)
        
        mels = extract_mels(frames, y, fft_window, 20)
        power = extract_power_spectrograms(frames, y, sr, 20)
        mfccs = extract_mfccs(frames, y, sr, 20)
        
        
        return np.stack([mels, power, mfccs], dtype=object)
    except Exception as e:
        print(f"Couldn't extract the frames due to {e}")
        return np.nan


def signal_to_features_video(file_title: str, y: np.array, sr: int = 22050, frame_size = 4096,
                       hop_size = 512, fft_window = 512, signal_duration = 14,
                      feature_shape = 20, path: str = None,):

    import os
    
    if path is None:
        path = os.getcwd()
    
    frames = split_signal_to_frame_indexes(frame_size, hop_size, y)
    
    
    mels = extract_mels(frames, y, fft_window, 20)
    power = extract_power_spectrograms(frames, y, sr, 20)
    mfccs = extract_mfccs(frames, y, sr, 20)

    # generate audio
    song_filename = artifacts_gen.generate_audio_from_frames(file_title, y, 22050)
    
    # mel artifacts
    artifacts_gen.generate_mel_spec_images(file_title, mels, path)
    artifacts_gen.generate_video_from_mel_spec_images(file_title, frame_size, song_filename, len(frames), path)
 
    # power_spectrograms artifacts
    artifacts_gen.generate_power_spectr_spec_images(file_title, power, path)
    artifacts_gen.generate_video_from_power_spetr_images(file_title, frame_size, song_filename, len(frames), path)

    # mfcc artifacts
    artifacts_gen.generate_mfcc_images(file_title, mfccs, path)
    artifacts_gen.generate_video_from_mfcc_images(file_title, frame_size, song_filename, len(frames), path)

    
    
    return np.stack([mels, power, mfccs], dtype=object)