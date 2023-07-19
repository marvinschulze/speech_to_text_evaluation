import sys
import os
import json
import pickle
import configparser

# class imports
from classes import VoskHandler, DataHandler


# Get relevant configs: input_path
config = configparser.ConfigParser()
config.read('config.ini')
input_path = config.get('DATACONFIG','input_path')
output_dir = config.get('DATACONFIG','output_dir') #MAYBE TAKE OUT EVERYWHERE; RELEVANT METHODS IN CLASS ARENT USED ANYMORE
ai_transcripts_path = config.get('DATACONFIG','output_dir')
wd_path = config.get('DATACONFIG','word_dicts_path')
model_path = config.get('MODELCONFIG','model_path')



#*** ----- STEP2: VoskHandler & DataHandler --> Setup VoskModel & specify output path ----- ***#
    # load dict of converted_audio_paths
with open(os.path.join(input_path, 'coversion_dict.pkl'), 'rb') as f:
    converted_audios = pickle.load(f)


    # initialize Vosk-Model
vosky = VoskHandler("vosky", model_path, output_dir)
vosky.initialize_model()

    # Specify output_dir where all files should be stored
DataHandle = DataHandler("data", output_dir)

#*** ----- STEP3: VoskHandler & DataHandler --> Extract & Handle Data ----- ***#
    #VoskHandler takes one file at a time
for file in converted_audios:
    abs_path = converted_audios[file]

    #Transcribe audio to text & get json data dumb in list as result
    res = vosky.transcribe_audio_to_text(abs_path)
    if res is None:
        print(f"[ERROR]Failure during recognizing audio with name {file}.")
        continue

    #convert res into (i) pure_text & (ii) list of word dicts
    data = DataHandle.convert_to_text_and_list_of_word_dicts(res)
    pure_text, word_dicts = data[0], data[1]

 

    #!!!!! HARD CODED SHIT TAKE OUT
    with open("{}/{}".format(wd_path, file), 'w') as fout:
        json.dump(word_dicts, fout)
    
    with open("{}/{}.txt".format(ai_transcripts_path, file), 'w') as fout:
            fout.write(pure_text)

print("[INFO] All done.")