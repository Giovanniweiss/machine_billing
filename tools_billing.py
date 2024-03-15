import os, shutil, glob

def listar_desenhos(Acerv, types = ('\*.pdf', '\*.dxf', '\*.step')):
    # Lista todos os arquivos na pasta escolhida dos tipos escolhidos.
    files_grabbed = []
    for files in types:
         files_grabbed.extend(glob.glob(Acerv + files, recursive=True))
    return files_grabbed


def solve_hierarchy_in_list(lista):
    output = []
    for item in lista:
        if type(item) == list:
            output.extend(solve_hierarchy_in_list(item))
        else:
            output.append(item)
    return output


# A partir da lista recuada do PDM, gera a lista de orçamento.
def billing_folders_and_list(lista):    
    '''
    Input: Lista de dicionários.
    
    Output: Lista de dicionários filtrada com somente soldas e itens associados e disposta em sublistas hierarquicas.
    '''
    
    # Função recursiva. Separa a hierarquia de soldas na lista de acordo com preestabelecido pela coluna nível.
    def rec_hierarquizar(conjunto, itens_do_conjunto):
        adicionados = []
        output = []
        adicionados.append(conjunto)
        output.append(conjunto)
        for i in itens_do_conjunto:
            if str(i["SAP"]).startswith("520-") and i not in adicionados:
                # Filter out the items already added to the output
                itens_do_subconjunto = [item for item in itens_do_conjunto if item["Nível"].startswith(i["Nível"] + ".") and item != i and item not in adicionados]
                a, b = rec_hierarquizar(i, itens_do_subconjunto)
                if itens_do_subconjunto != []:
                    output.append(a)
                    adicionados.extend(b)
            elif i not in adicionados:  
                output.append(i)
                adicionados.append(i)
        return output, adicionados
    
    # Gerar nomes.
    for item in lista:
        item.update({"NOME_ARQUIVO" : (item["SAP"] + " - " + item["DESENHO"])})
    
    # Obter os conjuntos da lista (que interessam).
    conjuntos = [linha for linha in lista if str(linha["SAP"]).startswith("520-")]
    adicionados = []
    
    # Resolver os conjuntos e criar hierarquias.
    for index, linha in enumerate(conjuntos):
        if not any(linha["Nível"] == i["Nível"] for i in adicionados):
            itens_no_conjunto = [item for item in lista if item["Nível"].startswith(linha["Nível"] + ".") and item != linha]
            conjuntos[index], b = rec_hierarquizar(linha, itens_no_conjunto)
            adicionados.extend(b)
        else:
            conjuntos[index] = None
    conjuntos = [i for i in conjuntos if i != None]
    
    # Localizar itens avulsos.
    avulsos = []
    tolerated_SAPs = ["110-", "120-", "140-"]
    for j in tolerated_SAPs:
        k = [i for i in lista if i not in adicionados and str(i['SAP']).startswith(j)]
        avulsos.extend(k)
    for item in avulsos:
        item.update({"CATEGORIA" : "Avulso"})
        
    return conjuntos, avulsos


# Copiar os arquivos às pastas de destino, recursivamente.
def copiar_arquivos_solda_conjuntos(acervo, destino, lista_hierarquizada = None):
    arquivos_acervo = listar_desenhos(acervo)
    # Primeiro, criar o caminho à pasta destino.
    # Em seguida, coletar o que precisa ser copiado.
    nome_pasta = lista_hierarquizada[0]['NOME_ARQUIVO'] + " - " + lista_hierarquizada[0]['TIPO DO ITEM']
    full_path = os.path.join(destino, nome_pasta)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        print(f"Pasta '{lista_hierarquizada[0]['NOME_ARQUIVO']}' criada com sucesso em '{destino}'.")
    else:
        print(f"Pasta '{lista_hierarquizada[0]['NOME_ARQUIVO']}' já existe em '{destino}'.")
    # A recursão ali serve para tratar de subconjuntos correspondentemente.
    copiar = []
    for item in lista_hierarquizada:
        if isinstance(item, list):
            copiar_arquivos_solda_conjuntos(acervo, full_path, item)
        else:
            copiar.append(item)
        
    # Finalmente, copiar os arquivos à pasta de destino.
    for file in arquivos_acervo:
        for item in copiar:
            if item['NOME_ARQUIVO'] in file:
                try:
                    shutil.copy(file, full_path)
                    item.update({"COPIADO" : "SIM"})
                except:
                    print(f"did not copy {file}")
                    item.update({"COPIADO" : "NÃO"})
    return lista_hierarquizada


def copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos):
    arquivos_acervo = listar_desenhos(acervo)
    for file in arquivos_acervo:
        for item in lista_avulsos:
            if item['NOME_ARQUIVO'] in file:
                try:
                    shutil.copy(file, destino)
                    item.update({"COPIADO" : "SIM"})
                except:
                    item.update({"COPIADO" : "NÃO"})
    return lista_avulsos
            

def solve_internal_welds(lista_hierarquizada):
    '''
    Função recursiva que deve acessar os conjuntos e "dissolver" aqueles que são Solda Interna.
    Elementos dissolvidos são movidos à montagem superior.
    '''
    lista_filtrada = []
    for item in lista_hierarquizada:
        if type(item) == list:
            if item[0]['TIPO DO ITEM'] == "Soldado Internamente":
                lista_filtrada.extend(solve_internal_welds(item))
            else:
                lista_filtrada.append(item)
        else:
            lista_filtrada.append(item)
            
    return lista_filtrada


def add_categories(lista_hierarquizada):
    tolerated_SAPs = ["110-", "120-", "140-"]
    for item in lista_hierarquizada:
        if type(item) == list:
            if item[0]['TIPO DO ITEM'] == "Soldado Internamente":
                add_categories(item)
            else:
                item[0].update({"CATEGORIA" : "Conjunto"})
        else:
            if any(item["SAP"].startswith(i) for i in tolerated_SAPs):
                item.update({"CATEGORIA" : "Avulso"})
            elif item["SAP"].startswith("520-"):
                item.update({"CATEGORIA" : "Solda Interna"})
            else:
                item.update({"CATEGORIA" : "Kit Solda"})
    return lista_hierarquizada


def separate_weld_kit_items(lista_hierarquizada):
    weld_kit = [item for item in lista_hierarquizada if type(item) != list]
    filtered_lista = [item for item in lista_hierarquizada if item not in weld_kit]
    return filtered_lista, weld_kit


def get_only_loose_items_from_weld_kit(weld_kit):
    loose_items = [item for item in weld_kit if item["CATEGORIA"] == "Avulso"]
    return loose_items


def correct_qty_in_assemblies(lista):
    montagens = [linha for linha in lista if str(linha["SAP"]).startswith("800-") or str(linha["SAP"]) == ""]
    for item in montagens:
        for subitem in lista:
            if subitem["Nível"].startswith(item["Nível"] + ".") and item != subitem:
                subitem["QTD"] = subitem["QTD"] * item["QTD"]
    lista_sem_montagens = [item for item in lista if item not in montagens]
    return lista_sem_montagens


def remove_int_welds_from_weld_kit(weld_kit):
    return [item for item in weld_kit if item["CATEGORIA"] != "Solda Interna"]