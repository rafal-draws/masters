import librosa as li
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os 



def generate_audio_from_frames(filename, signal, sampling_rate, artifacts_path):
    sf.write(f"{artifacts_path}slices/{filename}.wav", signal, sampling_rate)
    return f"{artifacts_path}slices/{filename}.wav"

# MEL 

def generate_mel_spec_images(filename, song_mels, path):
    
    import matplotlib.pyplot as plt
    import matplotlib
    
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
        plt.savefig(f"{path}mels/{filename}-{index}.png")
        plt.close(fig)


def generate_video_from_mel_spec_images(filename, frame_size, song_filename, frames_length, artifacts_path):
    
    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {artifacts_path}mels/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{artifacts_path}videos/mel-{filename}.mp4"
    )


def generate_power_spectr_spec_images(filename, power_spectrograms, artifacts_dir):
    vmin = 0
    vmax = 1
    
    
    for index, i in enumerate(power_spectrograms): ## TODO FIXIT
        fig = plt.figure()

        li.display.specshow(i, y_axis='chroma', x_axis='time', 
                          # fmax=fmax,
                          vmin=vmin, vmax=vmax)
        plt.colorbar()  # optional, shows scale
        plt.title("Chroma Power Spectrogram (Short Fourier Transform)")
        plt.savefig(f"{artifacts_dir}power/{filename}-{index}.png")
        plt.close(fig)


def generate_video_from_power_spetr_images(filename, frame_size, song_filename, frames_length, artifacts_dir):
    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {artifacts_dir}power/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{artifacts_dir}videos/power-{filename}.mp4"
    )



def generate_mfcc_images(filename, mfccs, artifacts_dir):

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
        plt.savefig(f"{artifacts_dir}mfcc/{filename}-{index}.png")
        plt.close(fig)


def generate_video_from_mfcc_images(filename, frame_size, song_filename, frames_length, artifacts_dir):
    os.system(
    # f"ffmpeg -framerate 5.355 -y " 4096 frames 
    f"ffmpeg -framerate {(frames_length/14):.2f} -y " 
    f"-i {artifacts_dir}mfcc/{filename}-%d.png "
    f"-i {song_filename} "
    # f" -vf minterpolate='fps=10' "  makes clunky
    f"-c:v libx264 -pix_fmt yuv420p "
    f"-c:a aac -b:a 192k -shortest "
    f"{artifacts_dir}videos/mfcc-{filename}.mp4"
    )