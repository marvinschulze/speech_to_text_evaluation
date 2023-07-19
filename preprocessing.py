import sys
import os
import pickle
import configparser

# class imports
from classes import AudioHandler


# Get relevant configs: input_path
config = configparser.ConfigParser()
config.read('config.ini')
input_path = config.get('DATACONFIG','input_path')


#*** ----- STEP1: AudioHandler --> READ & CONVERT AUDIO ----- ***#

    # CONFIGURATE AudioHandler
AudioHandle = AudioHandler('data1', input_path)
AudioHandle.setup()

    # AudioConversion: target: .wav mono
AudioHandle.convert_audio_to_wav()
AudioHandle.convert_audio_to_mono()

    # Return Dictionary of converted files
    # key=filename (no ext); value=absolute_path
# TODO setup differently; should work when self.convert_dir is set
converted_audios = AudioHandle.check_convert_dir()

    # Check if conversion returned results
if converted_audios is None:
    print("[FATAL] There are no converted audios to transcribe.")
    sys.exit()


# Save Dict of converted audios 
with open(os.path.join(input_path, 'coversion_dict.pkl'), 'wb') as f:
    pickle.dump(converted_audios, f)

print('[INFO]Conversion is done.')
