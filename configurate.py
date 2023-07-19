from configparser import ConfigParser
import os
import sys


# ------- ENTER CONFIG HERE --------
input_dir = 'data/deutsche-welle/'
input_path = 'data/deutsche-welle/langsam'
orig_transcripts = 'data/deutsche-welle/Transkripte'


model_path = '../vosk_models/vosk-model-de-tuda-0.6-900k'

# ------- END --------

# Create output_dir
output_dir = os.path.join(input_dir, 'ai_transcripts')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# Create word_dicts dir
word_dicts_path = os.path.join(input_dir, 'word_dicts')
if not os.path.isdir(word_dicts_path):
    os.mkdir(word_dicts_path)

# Create csv_results dir
csv_results = os.path.join(input_dir, 'csv_results')
if not os.path.isdir(csv_results):
    os.mkdir(csv_results)

# Check if model path exists
if not os.path.isdir(model_path):
    print("[Error] model_path does not exist.")
    sys.exit()

#Get the configparser object
config_object = ConfigParser()
# Specify paths
config_object["DATACONFIG"] = {
    'input_path': input_path,
    'output_dir': output_dir,
    'word_dicts_path': word_dicts_path,
    'orig_transcripts_path': orig_transcripts,
    'csv_results_path': csv_results,
}

# Specify model
config_object["MODELCONFIG"] = {
    "model_path": model_path,
}

#Write the above sections to config.ini file
with open('config.ini', 'w') as conf:
    config_object.write(conf)