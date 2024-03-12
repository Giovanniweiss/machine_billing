import tools_process_csv as tpc
import tools_billing as tb
import pandas as pd

if __name__ == "__main__":
    # Abertura, importação e limpeza de csv do PDM.
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

    # Processamento 
    lista_billing, lista_avulsos, adicionados = tb.billing_folders_and_list(data_list)
    only_external_welds = True
    if only_external_welds:
        destino = r"./Destino_int"
        lista_billing = tb.solve_internal_welds(lista_billing)
        lista_billing, weld_kit = tb.separate_weld_kit_items(lista_billing)
    for conjunto in lista_billing:
        tb.copiar_arquivos_solda_conjuntos(acervo, destino, conjunto)
    tb.copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos)
    
    lista_billing = tb.add_categories(lista_billing)
    lista_billing_solved = tb.solve_hierarchy_in_list(lista_billing + lista_avulsos)
    
    df2 = pd.DataFrame.from_dict(lista_billing_solved)
    df2.to_excel(tpc.test_file_path('players2.xlsx'), index=True)