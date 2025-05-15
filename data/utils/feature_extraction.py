import numpy as np
import librosa

def assert_at_least_minute(y, sr):
    #todo add docstring
    if len(y) / sr > 60:
        return True
    else:
        return False


def get_from_middle(y: np.ndarray, sr: int, amount: int) -> np.ndarray:
    
    mid_song_index = len(y)//2
    start = mid_song_index - ((amount//2) * sr)
    end = mid_song_index + ((amount//2) * sr)
    
    return y[start:end]

def get_from_middle_minus_one(y: np.ndarray, sr: int, amount: int) -> np.ndarray:
    
    mid_song_index = len(y)//2
    start = mid_song_index - ((amount//2) * sr)
    end = mid_song_index + ((amount//2) * sr)
    
    return y[start:end]

def normalize_audio(y: np.ndarray) -> np.ndarray:
    return y / np.max(np.abs(y))

def measure_peak_amplitude(y: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(y))
    print(f"Peak amplitude: {peak:.4f}")

def get_hanned(seconds: int, y, sampling_rate: int, debug: bool) -> np.ndarray :
    
    samples_amount = seconds * sampling_rate

    window = np.hanning(samples_amount)

    y_start = y[:samples_amount] * window 
    y_end = y[-samples_amount:] * window
    
    mid_sample_index = len(y_start)//2
    y_start = y_start[:mid_sample_index]
    y_end = y_end[mid_sample_index:]

    if debug == True:
        plt.figure(figsize=(12, 3))
        plt.title("Początek z oknem Hanninga")
        librosa.display.waveshow(y_start, sr=sampling_rate)
        plt.figure(figsize=(12, 3))
        plt.title("Koniec z oknem Hanninga")
        librosa.display.waveshow(y_end, sr=sampling_rate)
        plt.show()

    y_mod = np.copy(y)
    y_mod[0:len(y_start)] = y_start
    y_mod[-len(y_end):] = y_end
    
    
    return y_mod

def amplitude_envelope(signal, frame_size, hop_length):
    amplitude_envelope = []
    length = len(signal)
    for i in range (0, length, hop_length):
        current_frame_amplitude = max(signal[i:i+frame_size])
        amplitude_envelope.append(current_frame_amplitude)

    return np.array(amplitude_envelope)


def rms(signal, frame_size, hop_length):
    return librosa.feature.rms(y=signal, frame_length=frame_size, hop_length=hop_length)[0]

def zcr(signal, frame_size, hop_length):
    return librosa.feature.zero_crossing_rate(y=signal, frame_length=frame_size, hop_length=hop_length)[0]

