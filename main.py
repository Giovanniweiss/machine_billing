import tools_process_csv as tpc
import tools_billing as tb
import pandas as pd


# Main function
if __name__ == "__main__":
    path = "./test_files/"
    file_path = tpc.test_file_path("wtf.csv")
    tpc.hex_cleanup(file_path)
    data_list = tpc.load_csv_to_list_of_dicts(file_path)
    if data_list is not None:
        for i in range(min(5, len(data_list))):
            print(data_list[i])
            
    df = pd.DataFrame.from_dict(data_list)
    df.to_excel(tpc.test_file_path('players.xlsx'), index=True)
    
    acervo = r"C:\Users\projeto6\Desktop\Desktop 2\Documentos\Acervo"
    destino = r"C:\Users\projeto6\Desktop\Desktop 2\Documentos\Destino2"

    tb.billing_folders(acervo, destino, data_list)