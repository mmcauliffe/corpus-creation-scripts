from pathlib import Path
import librosa
import numpy as np
import soundfile as sf

root_dir = Path(r"D:\Data\speech\model_training_corpora\spanish\m_ailabs_spanish")
output_dir = Path(r"D:\Data\speech\model_training_corpora\spanish\m_ailabs_spanish_recombined")

padding = 0.5
if __name__ == '__main__':
    output_dir.mkdir(parents=True,exist_ok=True)
    for speaker_folder in root_dir.iterdir():
        if not speaker_folder.is_dir():
            continue
        current_file_name = None
        current_audio = None
        for file in sorted(speaker_folder.iterdir()):
            if not file.suffix == '.wav':
                continue
            root_file_name = '_'.join(file.stem.split('_')[:-1])
            print(file)
            if current_file_name is None:
                current_file_name = root_file_name
            if current_file_name == root_file_name:
                #audio, sr = librosa.load(file, sr=None, mono=False)
                audio, sr = sf.read(file)
                padded_samples = int(padding * sr)
                #audio = audio[padded_samples:-padded_samples+1]
                begin_index = 0
                end_index = -1
                for i in range(padded_samples):
                    if abs(audio[i]) != 0:
                        begin_index = i
                        break
                for i in range(padded_samples):
                    if abs(audio[-i]) != 0:
                        end_index = -i
                        break
                audio = audio[begin_index:end_index+1]
                if current_audio is None:
                    current_audio = audio
                else:
                    current_audio = np.append(current_audio, audio)
            else:
                print(root_file_name)
                output_path = output_dir.joinpath(f"{root_file_name}.wav")
                sf.write(output_path, current_audio, sr)
