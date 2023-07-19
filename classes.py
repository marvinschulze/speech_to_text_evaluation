import os
import sys
import glob
import pathlib
from pydub import AudioSegment

#to check wether audio conversion to mono worked 
import wave

#Imports for vosk
from vosk import Model, KaldiRecognizer, SetLogLevel

import json #chungs return by Kaldi/vosk come in json format
import csv #for saving chunks as csv file
#NOTE: AUDIO CHECKING (e.g. for mono) is done in AudioHandler & VoskHandler. This is a little redundant (create parent clas?)

# for docx output
import docx
from docx.shared import RGBColor

# for distance calculations
from sklearn.feature_extraction.text import CountVectorizer 
import numpy as np 
from scipy.spatial import distance 

# Word Error Rate Calculation 
import werpy



class AudioHandler():
    def __init__(self, name, 
                input=None, 
                audio_format='.wav'):

        self.name = name

        self.input = input
        self.audio_format = audio_format

        self.accepted_audio_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.aiff', '.wma']

        #make this a list of tuples?
        self.audios_to_convert = list()

        self.input_dir = None
        self.convert_dir = None
  
    def __str__(self):
        return self.name

    def print_info(self):
        print("\n\n[INFO]INFOBLOCK ABOUT AudioHandler.")
        #Accepted audio formats
        print("[INFO]Currently supporting (.wav, .mp3, .m4a, .ogg, .aiff.\nThey are hard coded in the init. You can add any formats supported by ffmpeg.")

        #things to note
        print("[INFO]Every filename has to have a unique name.")

    #used during setup()
    def create_convert_dir(self):
        #Takes self.input_dir. Tries to create a dir 'convert' inside this dir.
        #If dir exists, it counts number of files in it.
        #Then prompts user input wether to clear the dir or abandon the script.
        #NOTE dir should be cleared at the end of the script

        #create dir to store converted files in
        target_convert_path = os.path.join(self.input_dir, 'convert')
        if os.path.isdir(target_convert_path):
            print("\n[WARNING]Tried to create dir for converted files at\n\t'{}'\t-- Directory already exists.".format(target_convert_path))
            #check if there are files in the dir
            num_files = len(os.listdir(target_convert_path))
            
            if num_files > 0:
                print("[INFO]There are {} files in the dir.".format(num_files))

                while True:
                    inp = input("[PROMPT]Enter 'yes' to delete all the files in the dir. Script will continue afterwards.\nEnter 'no' to abandon script.\n")
                    if str(inp).lower() == 'yes': 
                        #delete all files in target dir.
                        files = glob.glob(os.path.join(target_convert_path, '*'))
                        for f in files:
                            os.remove(f)
                        break
                    elif str(inp).lower() == 'no':
                        print("[FATAL]The script will be abandoned. Handle the dir manually and start again.\nDIR in question: ", target_convert_path)
                        exit()
                    else:
                        print("[WARNING]This was not a valid input.")
            else:
                print("[INFO]Directory is empty. Script will continue using this dir.")

        else:
            os.mkdir(target_convert_path)

        self.convert_dir = target_convert_path

    #actually does more than evaluation now... change name to setup()
    def setup(self):

        #for the input
        if os.path.isdir(self.input):
            #save in input_dir, so future handles are more easy
            self.input_dir = self.input

            input_iter = pathlib.Path(self.input)
            for item in input_iter.iterdir():
                if not item.is_dir():
                    ext = pathlib.Path(item).suffix
                    if ext in self.accepted_audio_formats:
                        self.audios_to_convert.append((item, ext))
        elif os.path.exists(self.input):
            #save parent dir in input_dir, so future handles are more easy
            path = pathlib.Path(self.input)
            self.input_dir = path.parent.absolute()

            ext = pathlib.Path(self.input).suffix
            if ext in self.accepted_audio_formats:
                self.audios_to_convert.append((self.input, ext))
        
        if len(self.audios_to_convert) == 0 :
            print('[FATAL]Either you specified an empty dir or the file does not exist.')
            # ERROR HANDLING IS NEEDED 
            sys.exit()
            
        print("[INFO]Theese are the files that will be converted...")
        for i in range(len(self.audios_to_convert)):
            print("\t[{}] '{}'.".format(i+1, self.audios_to_convert[i][0]))

        
        #WILL NOT Check for the format ...


        #call self.create_convert_dir() to CREATE a direcotry for the converted audios to be stored in
        self.create_convert_dir()

    def convert_audio_to_wav(self):
        #converts all audio stored in self.audios_to_convert
        #target conversion: .wav mono
        if len(self.audios_to_convert) == 0:
            print("[FATAL]Nothing to convert here. Did you run setup()?")
            quit()
        else: 
            for audio in self.audios_to_convert:
                aud = audio[0]
                ext = str(audio[1])
                print("[INFO]Starting to convert '{}'.".format(aud))
                #create audiosegment
                if ext == ".wav":
                    audio_seg = AudioSegment.from_wav(aud)
                elif ext == ".mp3":
                    audio_seg = AudioSegment.from_mp3(aud)
                
                else:
                    e = ext.removeprefix('.')
                    audio_seg = AudioSegment.from_file(aud, e)
                
                #EXPORT as wav file
                #Take audio_file_path - get only the filename - strip extension - add .wav as extension
                aud_file_export = str(os.path.splitext(os.path.basename(aud))[0] + '.wav')
                audio_seg.export(os.path.join(self.convert_dir, aud_file_export), format = 'wav')
            print("[INFO]Files are converted to '.wav' under directory: {}.".format(self.convert_dir))
                
    def convert_audio_to_mono(self):
        #Take the .wav files and convert them to mono .wav files
        #Files have to be converted to mono first
        if self.convert_dir is None:
            print("[ERROR]You have to convert the audio files first (e.g. using convert_audio). Method called to early. Quit...")
            exit()

        # iterate over convert_dir to convert each file to mono. Then safe in same dir.
        for a in os.listdir(self.convert_dir):
            #load file as AudioSegment
            try:
                stereo_a = AudioSegment.from_wav(os.path.join(self.convert_dir, a))
            except Exception as err:
                print("[FATAL]Couldn't create an AudioSegment object from a file in the convert dir.\nNOTE: run covert_audio_to_wav first & make sure there are only .wav files in the dir.")
                print(err)

            #convert to mono = set audio to one channel
            mono_a = stereo_a.set_channels(1)
            fl_name = str("mono_" + a)
            mono_a.export(os.path.join(self.convert_dir, fl_name), format='wav')
            os.remove(os.path.join(self.convert_dir, a))

        print("[INFO]Conversion to mono is done.")

    def check_convert_dir(self):
        #just printing the info about the conversion dir and its files respectively        
        dir_list = os.listdir(self.convert_dir)
        print("""
        \n[INFO]Checking the conversion dir & printing infos.
        Convert_DIR is {}
        DIR contains {} files:
        """.format(self.convert_dir, len(dir_list)))

        valid_audios = {}

        for f in range(len(dir_list)):
            file = dir_list[f]
            print("FILE: ", file)
            fl_name, ext = os.path.splitext(file)
            
            print("\t[{}] {}".format(f+1, file))
            #check if file is in wave format
            if ext != '.wav':
                print("[WARNING]This file is not in .wav format.")
                continue
            #if yes, check if its single channel (mono)
            else:
                #load file and check for mono characteristics
                wf = wave.open(os.path.join(self.convert_dir, file), "rb")
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    print("\t[WARNING]File is in .wav, but not converted to mono correctly.")
                    continue
            
            #Arrive here if all checks are good (move to a new func 'check audio')
            print("\tThis file is in the correct format & converted to mono correctly.") 

            #try to remove 'mono_' from the file name which is added during conversion
            #TODO Later take this out and just create the dict earlier?
            print(fl_name)
            fl_name = fl_name.removeprefix('mono_')
            

            # valid_audios is a dict: key=filename, value=full_path
            valid_audios[fl_name] = os.path.join(self.convert_dir, file)


        #if any items have been appended return list; else return None
        if len(valid_audios) != 0:
            return valid_audios
        else:
            return None
        
class VoskHandler():

    def __init__(self, name, model_path, log_level=int(-1), recognition_frame_rate=4000):
        
        self.name = name 
        self.model_path = model_path
        self.log_level = log_level #Set to 0 to get a vosk-log

        self.frame_rate = recognition_frame_rate #default rate when working with Kaldi


        #Will be initialized
        self.model = None

    def initialize_model(self):
        # Set log level (Set to 0 to get a vosk-log)
        #TODO buggy when using self.loglevel
        SetLogLevel(-1)

        #Check if path exists
        if not os.path.exists(self.model_path):
            print(f"[FATAL]Please download the model from https://alphacephei.com/vosk/models and unpack as {self.model_path}")
            sys.exit()
        #Read the vosk model
        print(f"[INFO]Reading your vosk model '{self.model_path}'...")
        self.model = Model(self.model_path)
        print(self.model)
        print(f"[INFO]'{self.model_path}' model was successfully read.")
        
    
    def check_audio(self, audio_path):
        #Check wether path exists
        if not os.path.exists(audio_path):
            print(f"[ERROR]File '{audio_path}' doesn't exist")
            return None
        
        #Try to read the audio & check wether its mono
        try:
            wf = wave.open(audio_path, "rb")
            print(f"[INFO]'{audio_path}' file was successfully read")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                print("[ERROR]Audio file must be WAV format mono PCM.")
                return None
        except:
            print(f"[ERROR]There was an error reading the audio file under '{audio_path}'.")
            return None

        return wf



    # BETTER CALL IT TRANSCRIBE AUDIO TO DATA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def transcribe_audio_to_text(self, audio_path):
        #check audio first to reduce errors of Transcription
        check = self.check_audio(audio_path)
        if check is None:
            print(f"[ERROR]AudioCheck returned negative for '{audio_path}'.")
            return None 
        else:
            wf = check
        
        #Initialize KalidRecognizer with framerate of audio file
        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        
        #Word Recognitiion (always True)
        recognizer.SetWords(True)
        #TODO Enable for modification options here

        #recognize speech using vosk model
        results = [] #empty list, being filled with the partial results for each framerate respectively

        #iterate through audio file in specified framrate (default:4000)
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                part_result = json.loads(recognizer.Result())
                results.append(part_result)
        # add last chunk of data to the results
        part_result = json.loads(recognizer.Result())
        results.append(part_result)

        #Recognition finished, return list of data stored in results
        print(f"[INFO]Finished transcribing file under '{audio_path}'.")
        return results

class DataHandler():
    def __init__(self, name, output_dir):
        self.name = name

        #output_dir
        #Check wether path for Output_dir exists, if not ask wether to create it
        if not os.path.exists(output_dir):
            print(f"[WARNING]DIR '{output_dir}' doesn't exist")
            create_dir = input("[PROMPT]Should a new dir be created under this path? (Yes/No)\n")
            if create_dir.lower() == 'yes':
                try:
                    os.mkdir(output_dir)
                    print(f"[INFO]New dir under this path '{output_dir}' was created.")
                    self.output_dir = output_dir
                except Exception as err:
                    print(f"[FATAL]No dir under this path '{output_dir}' could be created. Exit...")
                    sys.exit()
            elif create_dir.lower() == 'no':
                print("[FATAL]Please create the dir or enter a different path. Exiting...")
                sys.exit()
            else:
                print("[FATAL]This was not a valid input.")
                sys.exit()
        else:
            self.output_dir = output_dir
            print("[INFO]Path to output dir accepted.")


    def save_text(self, text, filename):
        #All data is safed under output dir
        #add .txt as extension to the file name (remove ext before in case it was provided)
        filename = 'pure_text_' + os.path.splitext(filename)[0] + '.txt'

        target_path = os.path.join(self.output_dir, filename)

        if os.path.exists(target_path):
            rem = input(f"[PROMPT]A file under the name '{filename}' already exists in the output dir. Overwrite this file? (Yes/No)\n")
            if rem.lower() ==  'no':
                print("[FATAL]Please provide a different filename.")
                sys.exit()
            elif rem.lower() != 'yes':
                print("[FATAL]This was not a valid input.")
                sys.exit()


        print(f"[INFO]Saving pure text to '{target_path}'...")
        with open(target_path, "w") as text_file:
            text_file.write(text)
        print(f"[INFO]Text successfully saved as '{filename}'.")

    def save_as_csv(self, data, filename):
         #All data is safed under output dir
        #add .csv as extension to the file name (remove ext before in case it was provided)
        filename = 'csv_' + os.path.splitext(filename)[0] + '.csv'

        #TODO DUPLICATE CODE FIX THAT IN FUNCTION!
        target_path = os.path.join(self.output_dir, filename)

        if os.path.exists(target_path):
            rem = input(f"[PROMPT]A file under the name '{filename}' already exists in the output dir. Overwrite this file? (Yes/No)\n")
            if rem.lower() ==  'no':
                print("[FATAL]Please provide a different filename.")
                sys.exit()
            elif rem.lower() != 'yes':
                print("[FATAL]This was not a valid input.")
                sys.exit()

        # Save values in a csv file
        print(f"[INFO]Saving csv info to '{filename}'...")
        fields = ["WORD", "START", "END", "CONF"]
        with open(target_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            writer.writerows(data)

        print("[INFO]Saved csv data under:  ", target_path)


    def convert_to_text_and_list_of_word_dicts(self, data, autosave=False):
        #takes json dumb stored in list as input
        #As both would need to iterate over all the data, this method creates a text file and a csv file from the data simultaneously

        #create empty list: yields one dict for each word (word, start, end, conf)
        list_word_dicts = []
        #create empty string to add the single words to
        pure_text = ''

        #iterate over each sentence in the data
        for sentence in data:
            if len(sentence) == 1:
                # sometimes there are bugs in recognition 
                # and it returns an empty dictionary
                # {'text': ''}
                continue
            for obj in sentence['result']:
                # create a dict with infos & append it to list
                list_word_dicts.append({
                        "WORD" : obj['word'], 
                        "START" : obj['start'], 
                        "END" : obj['end'],
                        "CONF" : obj['conf'],
                }) 
                #add the word to the pure_text string
                pure_text += obj['word'] + ' '

        #If autosave is set, automatically call the methods to save data
        #TODO make this later. Need a way to handle filenames

        #returns a tuple of (pure_text, list_word_dicts)
        return (pure_text, list_word_dicts)

class CompareHandler():
    # Takes two transcribed files and compares
    def __init__(self, name, original, ai_transcribed):
        self.name = str(name)

        # normailze input data 
        self.original = werpy.normalize(original)
        self.ai_transcript = werpy.normalize(ai_transcribed)

        # create corpus as tuple
        self.corpus = (self.original, self.ai_transcript)

        # initialize Vecotrizer
        self.vectorizer = CountVectorizer()

        # transform Corupus into csrMatrix
        self.csrMatrix = self.vectorizer.fit_transform(self.corpus) 
        self.csrMatrix.toarray()

        # Convert each Matrix (of text) to an array
        # returns nested list with each matrix row converted to an array
        self.row_0 = self.csrMatrix.getrow(0).toarray()[0]
        self.row_1 = self.csrMatrix.getrow(1).toarray()[0]
    
    
    # display matrix
    def display_matrix(self):
        try:
            print("Displaying the matrix for {}.".format(self.name))
            print(self.row_0)
            print(self.row_1)
        except Exception as err:
            print("[ERROR]Something went wrong displaying the matrix.\n", err)
        
    # check basic infos: len of text
    def get_len_infos(self):
        # Get Length of files
        len_original = len(self.original.split())
        # print(len_original)
        len_ai = len(self.ai_transcript.split())
        return len_original, len_ai

    
    #--- CALCULATE DISTANCES --#
    # euclidean Distance
    def calculate_euclidean(self):
        dist = distance.euclidean(self.row_0, self.row_1)
        return dist

    # cosine Distance
    def calculate_cosine(self):
        dist = distance.cosine(self.row_0, self.row_1)
        return dist

    # jaccard Distance
    def calculate_jaccard(self):
        dist = distance.jaccard(self.row_0, self.row_1)
        return dist
 
    #--- CALCULATE Word Error Rate (WER) --#
    def calculate_wer(self):
        wer = werpy.wer(self.original, self.ai_transcript)
        return wer
    
    def calculate_wer_summary(self):
        wer_res = werpy.summary(self.original, self.ai_transcript)
        # Since it is only 1 column it will give the dict nested 
            # {0: {...}}
        wd = wer_res.to_dict('index')[0]

        # Create wer_res_dict as formatted dictionary
        wer_res_dict = {
            'wer': wd['wer'],
            'ld': wd['ld'], 
            'm': wd['m'], 
            'insertions': wd['insertions'],
            'deletions': wd['deletions'], 
            'substitutions': wd['substitutions']
        }

        return wer_res_dict
    

    # takes one file & writes resullt to csv
    # TODO all columns in one row --> multiple results in one csv file
    # TODO add more basic infos (audio-length, etc.)
    def results_to_csv(self, output_dir, euc_cos_jac=True, wer=True):
        filename = os.path.join(output_dir, self.name + ".csv")
        
        # -- BASIC INFO -- (Only len for now)
        len_orig, len_ai = self.get_len_infos()
        len_data = {'LEN Original': len_orig, 
                    'LEN AI-Transcript': len_ai}
        len_fields = list(len_data.keys())

        # -- Euclidean, Cosine & Jaccard -- 
        ecj_data = {'Euclidean': self.calculate_euclidean(),
                    'Cosine': self.calculate_cosine(),
                    'Jaccard': self.calculate_jaccard()}
        ecj_fields = list(ecj_data.keys())

        # -- WER Infos --
        wer_data = self.calculate_wer_summary()  # get Dicitonary of wer-results to save
        wer_fields = list(wer_data.keys())

        def write_to_csv(f, fields, data):
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            writer.writerow(data)
            
        

        with open(filename, 'w') as f:
            # Setup 'empty' writer to insert blank rows
            blank_writer = csv.writer(f)

            # Write BASIC INFOS + Empty row
            write_to_csv(f, len_fields, len_data)
            blank_writer.writerow("") #emptyrow

            # Write EUCLIDEAN, COSINE, JACCARD + Empty row
            write_to_csv(f, ecj_fields, ecj_data)
            blank_writer.writerow("") #emptyrow

            # Write WER - RESULTS
            write_to_csv(f, wer_fields, wer_data)
