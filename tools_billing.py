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


def billing_folders_and_list(lista):
    '''
    Input:
        Acervo - local onde os arquivos estão armazenados. Deve ser um string com endereço de pasta.
        Destino - local onde serão criadas as pastas de orçamento. Deve ser um string com endereço de pasta.
        Lista - lista de materiais recuada conforme gerada pelo PDM, formatada como lista de dicionários. Processar com hex_cleanup antes.
    
    Output esperado:
        Diversas pastas, cada uma com nome em formato SAP - SÉRIE - TIPO DE ITEM, contendo os arquivos .PDF, .DXF e .STEP dos arquivos do projeto.
        Se aplicável, devem haver subpastas também, de acordo com a estrutura hierarquica definida em projeto.
        Exportar uma lista de orçamento.
    '''
    
    # Função recursiva. Separa a hierarquia de soldas na lista de acordo com preestabelecido pela coluna nível.
    niveis_adicionados = []
    def rec_hierarquizar(conjunto, itens_do_conjunto):
        adicionados = []
        output = []
        output.append(conjunto)
        for i in itens_do_conjunto:
            if str(i["SAP"]).startswith("520-"):
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
    
    for index, linha in enumerate(conjuntos):
        if linha not in adicionados:
            itens_no_conjunto = [item for item in lista if item["Nível"].startswith(linha["Nível"] + ".") and item != linha]
            conjuntos[index], b = rec_hierarquizar(linha, itens_no_conjunto)
            adicionados.extend(b)
        else:
            conjuntos[index] = None
        
    conjuntos = [i for i in conjuntos if i != None]
    avulsos = []
    tolerated_SAPs = ["110-", "120-", "140-"]
    for j in tolerated_SAPs:
        k = [i for i in lista if i not in adicionados and str(i['SAP']).startswith(j)]
        avulsos.extend(k)
        
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
                except: #Se o arquivo já existir no destino, pular.
                    print(f"did not copy {file}")
                    item.update({"COPIADO" : "NÃO"})
    return lista_hierarquizada


def copiar_arquivos_solda_avulsos(acervo, destino, lista_avulsos):
    arquivos_acervo = listar_desenhos(acervo)
    # Primeiro, criar o caminho à pasta destino.
    # Em seguida, coletar o que precisa ser copiado.
    for file in arquivos_acervo:
        for item in lista_avulsos:
            if item['NOME_ARQUIVO'] in file:
                try:
                    shutil.copy(file, destino)
                    item.update({"COPIADO" : "SIM"})
                except: #Se o arquivo já existir no destino, pular.
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

def separate_weld_kit_items(lista_hierarquizada):
    weld_kit = [item for item in lista_hierarquizada if type(item) != list]
    filtered_lista = [item for item in lista_hierarquizada if item not in weld_kit]
    return filtered_lista, weld_kit