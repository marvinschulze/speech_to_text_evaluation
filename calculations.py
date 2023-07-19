import os
import configparser


from classes import CompareHandler


# Get relevant configs: input_path
config = configparser.ConfigParser()
config.read('config.ini')
ai_transcripts_path = config.get('DATACONFIG','output_dir')
original_dir = config.get('DATACONFIG','orig_transcripts_path')
results_dir = config.get('DATACONFIG','csv_results_path')


# GET List of Tuples:  [(ai_file, original_file), ...]
list_of_comparison_tuples = []
# iterate over output file dir
for out_file in os.listdir(ai_transcripts_path):
    ai_file = os.path.join(ai_transcripts_path, out_file)
    if out_file in os.listdir(original_dir):
        original_file = os.path.join(original_dir, out_file)
        list_of_comparison_tuples.append((ai_file, original_file))


# CALCULATE and SAVE as csv
for pair in list_of_comparison_tuples:
    # Take from input path: only filename & strip ext
    ai_file, original_file = pair
    print(pair)
    name = str(os.path.splitext(os.path.basename(ai_file))[0])
    print("Results for {}.".format(name))

    with open(original_file, 'r', encoding= 'unicode_escape') as f: original_f = f.read()
    with open(ai_file, 'r', encoding= 'unicode_escape') as f: ai_f = f.read()


    Comparison = CompareHandler(name, original_f, ai_f)
    Comparison.results_to_csv(results_dir)



