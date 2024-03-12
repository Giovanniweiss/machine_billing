import tools_process_csv as tpc
import tools_billing as tb
import tools_gui as tg
import pandas as pd
import os, datetime, shutil

if __name__ == "__main__":
    lista, destino, acervo, pastas_de_solda, solda_usinados_interna = tg.abrir_GUI()
    current_time = datetime.datetime.now()
    # Abertura, importação e limpeza de csv do PDM.
    tpc.hex_cleanup(lista)
    data_list = tpc.load_csv_to_list_of_dicts(lista)
    if data_list is not None:
        for i in range(min(5, len(data_list))):
            print(data_list[i])
    df = pd.DataFrame.from_dict(data_list)
    filename1 = current_time.strftime("%Y-%m-%d_%H-%M-%S") + '_planilha_original.xlsx'
    df.to_excel(filename1, index=True)
    shutil.move(filename1, os.path.join(destino, filename1))

    # Processamento 
    lista_billing, lista_avulsos, adicionados = tb.billing_folders_and_list(data_list)
    if solda_usinados_interna:
        lista_billing = tb.solve_internal_welds(lista_billing)
        lista_billing, weld_kit = tb.separate_weld_kit_items(lista_billing)
    if pastas_de_solda:
        for conjunto in lista_billing:
            tb.copiar_arquivos_solda_conjuntos(acervo, destino, conjunto)
        tb.copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos)
    lista_billing = tb.add_categories(lista_billing)
    lista_billing_solved = tb.solve_hierarchy_in_list(lista_billing + lista_avulsos)
    df2 = pd.DataFrame.from_dict(lista_billing_solved)
    filename2 = current_time.strftime("%Y-%m-%d_%H-%M-%S") + '_lista_de_orcamento.xlsx'
    df2.to_excel(filename2, index=True)
    shutil.move(filename2, os.path.join(destino, filename2))