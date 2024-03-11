
import os, shutil, glob

def listar_desenhos(Acerv, types = ('\*.pdf', '\*.dxf', '\*.step')):
    # Lista todos os arquivos na pasta escolhida dos tipos escolhidos.
    files_grabbed = []
    for files in types:
         files_grabbed.extend(glob.glob(Acerv + files, recursive=True))
    return files_grabbed

def billing_folders(acervo, destino, lista):
    '''
    Input:
        Acervo - local onde os arquivos estão armazenados. Deve ser um string com endereço de pasta.
        Destino - local onde serão criadas as pastas de orçamento. Deve ser um string com endereço de pasta.
        Lista - lista de orçamento, gerada de acordo com as diretrizes da empresa. Deve ser um list de dicts.
            A lista de orçamento deve estar dividida em conjuntos, subconjuntos e avulsos, obrigatóriamente, e agrupada corretamente.
    
    Output esperado:
        Diversas pastas, cada uma com nome em formato SAP - SÉRIE, contendo os arquivos .PDF, .DXF e .STEP dos arquivos do projeto.
        Se aplicável, devem haver subpastas também.
        Criar uma cópia da lista de orçamento na pasta base do destino.
    '''
    
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
    
    # Copiar os arquivos às pastas de destino, recursivamente.
    def copiar_arquivos_solda_conjuntos(lista_hierarquizada, destino):
        # Primeiro, criar o caminho à pasta destino.
        # Em seguida, coletar o que precisa ser copiado.
        nome_pasta = lista_hierarquizada[0]['nome_arquivo'] + " - " + lista_hierarquizada[0]['TIPO DO ITEM']
        full_path = os.path.join(destino, nome_pasta)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Pasta '{lista_hierarquizada[0]['nome_arquivo']}' criada com sucesso em '{destino}'.")
        else:
            print(f"Pasta '{lista_hierarquizada[0]['nome_arquivo']}' já existe em '{destino}'.")
        # A recursão ali serve para tratar de subconjuntos correspondentemente.
        copiar = []
        for item in lista_hierarquizada:
            if isinstance(item, list):
                copiar_arquivos_solda_conjuntos(item, full_path)
            else:
                copiar.append(item)
            
        # Finalmente, copiar os arquivos à pasta de destino.
        for file in arquivos_acervo:
            for item in copiar:
                if item['nome_arquivo'] in file:
                    try:
                        shutil.copy(file, full_path)
                    except: #Se o arquivo já existir no destino, pular.
                        print(f"did not copy {file}")
                        pass
        return
    
    def copiar_arquivos_solda_avulsos(lista_avulsos, destino):
        # Primeiro, criar o caminho à pasta destino.
        # Em seguida, coletar o que precisa ser copiado.
        for file in arquivos_acervo:
            for item in lista_avulsos:
                if item['nome_arquivo'] in file:
                    try:
                        shutil.copy(file, destino)
                    except: #Se o arquivo já existir no destino, pular.
                        pass
        return
    
    # Obter arquivos do acervo.
    arquivos_acervo = listar_desenhos(acervo)
    
    # Gerar nomes.
    for item in lista:
        item.update({"nome_arquivo" : (item["SAP"] + " - " + item["DESENHO"])})
    
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
    tolerated_SAPs = ["110-", "140-"]
    for j in tolerated_SAPs:
        k = [i for i in lista if i not in adicionados and str(i['SAP']).startswith(j)]
        avulsos.extend(k)
    
    for conjunto in conjuntos:
        copiar_arquivos_solda_conjuntos(conjunto, destino)
        
    return conjuntos + avulsos