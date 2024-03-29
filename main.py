import tools_process_csv as tpc
import tools_billing as tb
import tools_gui as tg
import pandas as pd
import os, datetime, shutil

if __name__ == "__main__":
    # Obter informações do usuário.
    lista, destino, acervo, pastas_de_solda, solda_usinados_interna = tg.abrir_GUI()
    nome_planilha_csv = str(os.path.splitext(os.path.basename(lista))[0])
    if lista == "" or destino == "" or acervo == "":
        print("Input inválido.")
        exit()
    
    # Criar pastas conforme necessário.
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = current_time + "_" + nome_planilha_csv
    destino = os.path.join(destino, folder_name)
    if not os.path.exists(destino):
        os.makedirs(destino)
        print(f"Pasta '{folder_name}' criada com sucesso em '{destino}'.")
    
    # Abertura, importação e limpeza de csv do PDM.
    tpc.hex_cleanup(lista)
    data_list = tpc.load_csv_to_list_of_dicts(lista)
    if data_list is not None:
        for i in range(min(5, len(data_list))):
            print(data_list[i])
    else:
        print("Falha de leitura do arquivo csv.")
        exit()
    
    # Processamento 
    # Corrige quantidades dentro de montagens.
    data_list_adjusted = tb.correct_qty_in_assemblies(data_list)
    # Cria uma lista com sublistas de soldas e uma lista com avulsos.
    lista_billing, lista_avulsos = tb.billing_folders_and_list(data_list_adjusted)
    # Adiciona categoria a todos os elementos.
    lista_billing = tb.add_categories(lista_billing)
    # Resolve hierarquias, resultando em apenas uma lista resultante.
    # Essa lista pode ser usada para gerar a estrutura pela planilha macro.
    lista_macro_solved = tb.solve_hierarchy_in_list(lista_billing + lista_avulsos)
    
    # Processamento Condicional
    # Gera uma lista de listas de soldas compradas somente + itens avulsos + kit solda.
    lista_billing_solda_iterna = tb.solve_internal_welds(lista_billing)
    # Separa da lista acima o kit solda.
    lista_billing_solda_iterna, weld_kit = tb.separate_weld_kit_items(lista_billing_solda_iterna)
    # Do Kit Solda, separa somente os avulsos.
    loose_items = tb.get_only_loose_items_from_weld_kit(weld_kit)
    # Remover desenhos de solda interna.
    weld_kit = tb.remove_int_welds_from_weld_kit(weld_kit)
    
    # lista_billing_solda_iterna = lista de orçamento com solda interna, sem avulsos.
    # lista_billing = lista de orçamento contendo todas as soldas internas também.
    
    # Se o usuário vai fazer solda interna, 
    if solda_usinados_interna:
        lista_billing = lista_billing_solda_iterna
    if pastas_de_solda:
        for conjunto in lista_billing:
            tb.copiar_arquivos_solda_conjuntos(acervo, destino, conjunto)
        tb.copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos + loose_items)
    
    if solda_usinados_interna:
        lista_billing_solved = tb.solve_hierarchy_in_list(lista_billing_solda_iterna + lista_avulsos + loose_items)
    else:
        lista_billing_solved = tb.solve_hierarchy_in_list(lista_billing_solda_iterna + lista_avulsos + weld_kit)
    
    # Exportar Planilha
    df1 = pd.DataFrame.from_dict(data_list)
    df2 = pd.DataFrame.from_dict(lista_macro_solved)
    df3 = pd.DataFrame.from_dict(lista_billing_solved)
    filename2 = current_time + "_" + nome_planilha_csv + '_lista_de_orcamento.xlsx'
    Sheet1 = "Lista Original"
    Sheet2 = "Lista Macro"
    Sheet3 = "Lista de Orçamento"
    with pd.ExcelWriter(filename2) as writer:
        df1.to_excel(writer, sheet_name=Sheet1, index=True)
        df2.to_excel(writer, sheet_name=Sheet2, index=True)
        df3.to_excel(writer, sheet_name=Sheet3, index=True)
    shutil.move(filename2, os.path.join(destino, filename2))