import pandas as pd
import codecs

def load_csv_to_list_of_dicts(csv_file):
    try:
        encoding = 'utf_16_le'
        separator = ";"
        df = pd.read_csv(csv_file, encoding=encoding, sep=separator)
        df = df.fillna('') 
        dict_list = df.to_dict(orient='records')
        return dict_list
    
    except Exception as e:
        print("Error while reading csv:", e)
        return None


def hex_cleanup(file_path):
    # Cleans up faulty hex files generated by Solidworks.
    # No clue why this nonsense is broken, but this fixes it.
    cleanup = [["20002000", ""]]
    with open(file_path, 'rb') as file:
        content = file.read()
    for i in cleanup:
        content = content.replace(codecs.decode(i[0], 'hex'), codecs.decode(i[1], 'hex'))
    with open(file_path, 'wb') as file:
        file.write(content)
        

def test_file_path(filename):
    test_files_folder = "./test_files/"
    return test_files_folder + filename

