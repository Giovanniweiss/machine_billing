import tools_process_csv as tpc
import tools_billing as tb
import pandas as pd

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
    destino = r"./Destino"

    lista_billing, lista_avulsos = tb.billing_folders_and_list(acervo, destino, data_list)
    for conjunto in lista_billing:
        tb.copiar_arquivos_solda_conjuntos(acervo, destino, conjunto)
    tb.copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos)
    
    lista_billing_solved = tb.solve_hierarchy_in_list(lista_billing + lista_avulsos)
    
    df2 = pd.DataFrame.from_dict(lista_billing_solved)
    df2.to_excel(tpc.test_file_path('players2.xlsx'), index=True)