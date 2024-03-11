import pandas as pd
import csv, os, glob, shutil, PyPDF2, re, random
from pathlib import Path
from datetime import datetime



def listar_desenhos(Acerv, types = ('\*.pdf', '\*.dxf', '\*.step')):
    # Lista todos os arquivos na pasta escolhida dos tipos escolhidos.
    files_grabbed = []
    for files in types:
         files_grabbed.extend(glob.glob(Acerv + files, recursive=True))
    return files_grabbed



def exportar_para_excel(nome_arquivo, lista, nomes_abas = None):
    #Código padrão para exportar listas de dicionários para excel.

    # Verificar uso apropriado
    if not isinstance(nomes_abas, list):
        print("Lista de nomes de abas não é lista. Substituindo por numeros sequenciais.")
        nomes_abas = [str(num) for num in range(len(lista))]

    if (isinstance(nomes_abas, list) and len(lista) != len(nomes_abas)):
        print("Lista de nomes de abas incompatível com lista de dados (comprimentos diferentes). Substituindo por numeros sequenciais.")
        nomes_abas = [str(num) for num in range(len(lista))]
    
    # Exportar os dados.
    with pd.ExcelWriter(nome_arquivo) as writer:
            for index, data in enumerate(lista):
                j = pd.DataFrame(data=data)
                j.to_excel(writer, sheet_name=nomes_abas[index])
    
    return 0



def extrairdados(arquivo):
    csv_mapping_list = []
    if os.path.isfile(arquivo):
         with open(arquivo, encoding='utf-8-sig') as my_data:
            try:
                csv_reader = csv.reader(my_data, delimiter='|')
                line_count = 0

                for line in csv_reader:
                    if line_count == 0:
                        header = line
                    else:
                        row_dict = {key: value for key, value in zip(header, line)}
                        csv_mapping_list.append(row_dict)
                    line_count += 1
            except:
                raise Exception("""Arquivo inválido para extração de dados.""")
    else:
        raise Exception("""Arquivo inválido para extração de dados.""")
    return csv_mapping_list



def remove_and_replace_delimiters(input_file, output_file, old_delimiter, new_delimiter):
    if os.path.isfile(str(input_file)):
        with open(input_file, 'r', encoding='utf-8-sig') as my_data:
            # Read the entire file and remove double-quote characters
            file_content = my_data.read().replace('"', '')

        # Write the content with the double-quotes removed to a temporary file
        temp_file_path = "temp.csv"
        with open(temp_file_path, 'w', encoding='utf-8-sig') as temp_file:
            temp_file.write(file_content)

        # Process the temporary file and replace delimiters
        with open(temp_file_path, 'r', newline='', encoding='utf-8-sig') as temp_data:
            csv_reader = csv.reader(temp_data, delimiter=old_delimiter)
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                csv_writer = csv.writer(outfile, delimiter=new_delimiter)
                for line in csv_reader:
                    csv_writer.writerow(line)

        # Delete the temporary file
        os.remove(temp_file_path)

    else:
        print('Invalid file path.')



def filtrar_por_padroes_sap(SAPs):
    patterns = [r"^\d{3}-\d{5}$",
            r"^\d{3}-\d{6}$",
            r"^\d{3}-\d{2}-\d{3}$"
            r"^\d{3}-\d{2}-\d{2}$"
            r"^\d{3}-\d{3}-\d{2}$"
            r"^\d{3}-\d{3}-\d{3}$",
            r"^\d{3}-\d{3}-\d{4}$",
            r"^\d{3}-\d{5}-[A-Z]\d$",
            r"^\d{3}-\d{6}-[A-Z]\d$",
            r"^\d{3}-\d{2}-\d{3}-[A-Z]\d$"
            r"^\d{3}-\d{2}-\d{2}-[A-Z]\d$"
            r"^\d{3}-\d{3}-\d{2}-[A-Z]\d$"
            r"^\d{3}-\d{3}-\d{3}-[A-Z]\d$",
            r"^\d{3}-\d{3}-\d{4}-[A-Z]\d$",]
    filtered_values = [value for value in SAPs 
                        if any(re.match(pattern, value) 
                        for pattern in patterns)]
    return filtered_values



def copiar_arquivos3(Destn, files_grabbed, lista):

    #Check input
    if files_grabbed == [] or lista == []:
        return 1

    #Separação de SAPs, a condicional é necessária para não bugar os processos abaixo.
    SAPs = [i['COD.MP'] for i in lista if i['COD.MP']] + [i['SAP'] for i in lista if i['SAP']]
    SAPs = list(dict.fromkeys(SAPs))

    #Etapa 1 - Filtrar a lista.
    filtered_values = filtrar_por_padroes_sap(SAPs)
    
    #Etapa 1.1 - Tentando eliminar acidentes.
    code_counts = {SAP: 0 for SAP in filtered_values}
    for i,value in enumerate(filtered_values):
        filtered_values[i] = value + ' -'

    #Etapa 2 - Localizar os arquivos a copiar.
    localizado = []
    for file in files_grabbed:
        for SAP in filtered_values:
            if SAP in file:
                localizado.append(file)
                code_counts[SAP[:-2]] += 1 #This is to remove the ' -' for the excel.

    #Etapa 3 - Copiar os arquivos.
    localizado = list(dict.fromkeys(localizado)) #Provavelmente redundante.
    for arquivo in localizado:
        try:
            shutil.copy(arquivo,Destn)
        except: #Se o arquivo já existir no destino, pular.
            pass

    #Etapa 4 - Gerar a lista com os SAPs e contagens.
    excelname = 'relacao_de_arquivos.xlsx'
    exportarexcel = pd.DataFrame(data=code_counts, index=[0])
    exportarexcel.T.to_excel(excelname, sheet_name='sheet1', index=True)

    return 0

def separar_grupos_desenhos(Pasta, Destino):

    #Verificação de segurança
    if Pasta == None or Destino == None:
        return 1

    #ETAPA 1: Definir grupos
    patterns = {
        "110-" : "CHFISU",
        "111-" : "CHFICU",
        "112-" : "CHFICU",
        "120-" : "CHGRSU",
        "121-" : "CHGRCU",
        "122-" : "CHGRCU",
        "140-" : "TUBOS",
        "200-" : "COMERCIAL",
        "210-" : "COMERCIAL",
        "220-" : "COMERCIAL",
        "300-" : "COMERCIAL",
        "310-" : "COMERCIAL",
        "320-" : "COMERCIAL",
        "400-" : "COMERCIAL",
        "510-" : "TEMP1",
        "511-" : "TEMP2",
        "520-" : "SOLDA",
        "800-" : "MONTAGEM"
        }
    
    pastas = {
        "CHFISU"    : [],
        "CHFICU"    : [],
        "CHGRSU"    : [],
        "CHGRCU"    : [],
        "TUBOS"     : [],
        "COMERCIAL" : [],
        "USINAGEM"  : [],
        "SOLDA"     : [],
        "TEMP1"     : [],
        "TEMP2"     : [],
        "MONTAGEM"  : [],
        "ERRO"      : []
        }
    
    #ETAPA 2: Coletar arquivos.
    files_grabbed = listar_desenhos(Pasta)

    #ETAPA 3: Identificar e classificar os desenhos:
    for file in files_grabbed:
        current_file = Path(file).stem
        prefix = current_file[:4]
        try:
            grupo = patterns[prefix]
        except KeyError:
            grupo = "ERRO"
        pastas[grupo].append(file)

    #ETAPA 4: Processar os usinados.
    TEMP1_temp    = [desenho for desenho in pastas['TEMP1']]
    TEMP2_temp    = [desenho for desenho in pastas['TEMP2']]
    CHFICU_filtro = [[Path(desenho).stem[4:]] for desenho in pastas['CHFICU']]
    CHGRCU_filtro = [[Path(desenho).stem[4:]] for desenho in pastas['CHGRCU']]
    #This procedure below is used to match codes such as 112-123456 with the corresponding 510-123456.
    #Filter values from TEMP1_temp into CHFICU_add1, CHGRCU_add1 and USINAGEM_add1
    CHFICU_add1 =   [desenho for desenho in TEMP1_temp if [Path(desenho).stem[4:]] in CHFICU_filtro]
    CHGRCU_add1 =   [desenho for desenho in TEMP1_temp if [Path(desenho).stem[4:]] in CHGRCU_filtro]
    USINAGEM_add1 = [desenho for desenho in TEMP1_temp if [Path(desenho).stem[4:]] not in CHFICU_filtro and file not in CHGRCU_filtro]
    #Filter values from TEMP2_temp into CHFICU_add2, CHGRCU_add2 and USINAGEM_add2
    CHFICU_add2 =   [desenho for desenho in TEMP2_temp if [Path(desenho).stem[4:]] in CHFICU_filtro]
    CHGRCU_add2 =   [desenho for desenho in TEMP2_temp if [Path(desenho).stem[4:]] in CHGRCU_filtro]
    USINAGEM_add2 = [desenho for desenho in TEMP2_temp if [Path(desenho).stem[4:]] not in CHFICU_filtro and file not in CHGRCU_filtro]
    #Add the filtered values into the existing lists.
    pastas['CHFICU']    += CHFICU_add1   + CHFICU_add2
    pastas['CHGRCU']    += CHGRCU_add1   + CHGRCU_add2
    pastas['USINAGEM']  += USINAGEM_add1 + USINAGEM_add2

    #ETAPA 5: Criar as pastas e copiar os arquivos.
    folder_list = list(pastas.keys())
    values_to_remove = ["TEMP1", "TEMP2"]
    folder_list = [key for key in folder_list if key not in values_to_remove]
    #Contadores de arquivos.
    totalcounter = 0
    failedcounter = 0
    for folder_name in folder_list:
        folder_path = os.path.join(Destino, folder_name)
        counter = 0
        if pastas[folder_name]:
            #Check if folder exists. Create one if it doesn't.
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
                print(f"Created folder: {folder_name} in {Destino}")
            else:
                print(f"Folder {folder_name} already exists in {Destino}")
            
            #Copy files into the new folder.
            for file in pastas[folder_name]:
                try:
                    shutil.move(file, folder_path)
                    counter += 1
                    totalcounter += 1
                except:
                    print(f"Could not copy {file}")
                    failedcounter += 1
            print(f"{counter} out of {len(pastas[folder_name])} files copied into {folder_name} successfully.")

        else:
            print(f"No files to copy into {folder_name}. Folder not created.")

    print(f"{totalcounter} files copied successfully.")
    print(f"{failedcounter} files failed to copy.")
    return 0



def pasta_de_solda(Destn, files_grabbed, lista, nome_projeto="padrao"):
    #Check input
    if lista == []:
        return 1
    
    #Variables
    Dateformat = re.compile(r'\d\d/\d\d/\d\d\d\d')
    csv_output = []
    Destn = Destn + r"\solda_interna"
    
    #ETAPA 1: Obter os SAPs e descrições dos conjuntos de solda interna.
    List_filtered = [i for i in lista if (i['TIPO DO ITEM'] == "Soldado Internamente")]
    List_filtered = [i for i in List_filtered if i['SAP']]

    #ETAPA 2: Obter os PDFs dos SAPs obtidos.
    pdfFiles = files_grabbed
    for entry in List_filtered:
        sap_value = entry['SAP']
        matching_files = [file for file in pdfFiles if (str(sap_value) + ' -') in Path(file).stem]
        if matching_files:
            # If a matching file is found, add the 'filepath' key to the dictionary
            entry['filepath'] = matching_files[0]  # Assuming there's only one matching file
    
    #ETAPA 3: Obter, dos PDFs, a quantidade de páginas de cada PDF e data.
    pdf_unificado = PyPDF2.PdfMerger()

    for num, current_file in enumerate(List_filtered):
        if current_file['filepath']:
            with open(current_file['filepath'], 'rb') as pdfFileObj:
                pdfReader = PyPDF2.PdfReader(pdfFileObj)
                pageObj = pdfReader.pages[0]
                
                text = pageObj.extract_text()

                #Get all the dates.
                all_dates = re.findall(Dateformat, text)
                date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in all_dates]
                Date = max(date_objects)

                #Old Method - Does not work because only gets first date.
                #Date = Dateformat.search(text).group()

                for i, data in enumerate(pdfReader.pages):
                    Pages = (str(num+1) + '.' + str(i+1))
                    #Dados para Etapa 5.
                    file = {
                        'Pages'       : Pages,
                        'Date'        : Date,
                        'Description' : current_file['DESCRIÇÃO'],
                        'SAP'         : current_file['SAP']
                    }
                    csv_output.append(file)
                pdf_unificado.append(pdfFileObj)
        else:
            file = {
                'Pages'       : 'Arquivo não encontrado',
                'Date'        : '0',
                'Description' : current_file['DESCRIÇÃO'],
                'SAP'         : current_file['SAP']
            }
            csv_output.append(file)

    #ETAPA 4: Unir todos os PDFs num único arquivo de saída.
    with open(Destn + nome_projeto + '.pdf', 'wb') as output:
        pdf_unificado.write(output)

    #ETAPA 5: Preparar a planilha com a relação de desenhos. Incluir:
    #	Nome do projeto (pedir ao usuário), data de hoje.
    #	SAP do desenho, revisão, descrição, data do desenho.
    if len(csv_output) > 0:
        with open(Destn + nome_projeto + ".csv", 'w', newline='') as csv_file:
            # Create a CSV writer object
            csv_writer = csv.DictWriter(csv_file, fieldnames=csv_output[0].keys())

            # Write the header to the CSV file
            csv_writer.writeheader()

            #ETAPA 6: Salvar a planilha.
            # Write each dictionary as a row in the CSV file
            csv_writer.writerows(csv_output)



def descaracterizar_lista(lista):
    # Descaracteriza uma lista, dando valores aleatórios que não tem referência a projeto.
    # Dá para adicionar uma função que adiciona SAPs múltiplas vezes.
    tag_Cod_MP  = "COD.MP"
    tag_Cod_SAP = "SAP"
    tag_MP_ext  = "MP EXTENSO"
    tag_Desenho = "DESENHO"
    tag_Desc    = "DESCRIÇÃO"
    tag_Comp    = "COMP."
    tag_Larg    = "LARGURA"
    tag_Peso    = "PESO KG"

    # Número de elementos para substituir em MP e SAP.
    tamanho = range(1,len(lista)*2)
    elementos = random.sample(tamanho, len(tamanho))

    # Adiciona zeros conforme nosso padrao.
    elementos = [str(i).zfill(6) for i in elementos]

    # Loop principal. Substitui valores com outros gerados.
    for index, values in enumerate(lista):
        if values[tag_Cod_MP]:
            values[tag_Cod_MP] = values[tag_Cod_MP][0:4] + elementos[index]
        if values[tag_Cod_SAP]:
            values[tag_Cod_SAP] = values[tag_Cod_SAP][0:4] + elementos[index]
        if values[tag_MP_ext]:
            values[tag_MP_ext] = "MP GENÉRICA" + " " + str(index)

        # Não precisa checar esses. Melhor preencher tudo para descaracterizar.
        values[tag_Desenho] = "DESENHO GENÉRICO" + " " + str(index)
        values[tag_Desc] = "DESCRIÇÃO GENÉRICA" + " " + str(index)
        values[tag_Comp] = random.randint(1,2000)
        values[tag_Larg] = random.randint(1,2000)
        values[tag_Peso] = random.uniform(1,100)

        # Tipo do item, Acab. Superficial e QTD são mantidos.
    return lista


def comparar_listas(lista_velha, 
                    lista_nova, 
                    key_drawing_num  = 'DESENHO', 
                    key_SAP_code     = 'SAP', 
                    key_description  = 'DESCRIÇÃO',
                    key_quantities   = 'QTD'):
    
    # Comparar duas listas de PDM
    # Tem que comparar duas chaves ao mesmo tempo para garantir que estamos falando da mesma peça.
    diff_qtd = 'Diff. ' + key_quantities

    # Verificar itens que saíram do projeto.
    removidos = []
    for ele_1 in lista_velha:
        if not any(ele_1[key_drawing_num] == ele_2[key_drawing_num] for ele_2 in lista_nova) and not any(ele_1[key_SAP_code] == ele_2[key_SAP_code] for ele_2 in lista_nova):
            removidos.append(ele_1)
    # Verificar itens que entraram no projeto.
    adicionados = []
    for ele_2 in lista_nova:
        if not any(ele_2[key_drawing_num] == ele_1[key_drawing_num] for ele_1 in lista_velha) and not any(ele_2[key_SAP_code] == ele_1[key_SAP_code] for ele_1 in lista_velha):
            adicionados.append(ele_2)

    # Tags para o excel a ser exportado no final, referente aos revisados.
    old_SAP_tag_for_xl = 'SAP antigo'
    old_qty_tag_for_xl = 'QTD antiga'
    new_SAP_tag_for_xl = 'SAP novo'
    new_qty_tag_for_xl = 'QTD nova'
    description_for_xl = 'Descrição'
    
    # Verificar itens que sofreram revisão.
    revisados = [
        {
            old_SAP_tag_for_xl : velho[key_SAP_code],
            old_qty_tag_for_xl : velho[key_quantities],
            new_SAP_tag_for_xl : novo[key_SAP_code],
            new_qty_tag_for_xl : novo[key_quantities],
            description_for_xl : novo[key_description]
        }
        for velho in removidos
        for novo in adicionados
        if novo[key_SAP_code].startswith(velho[key_SAP_code]) and novo[key_SAP_code] != velho[key_SAP_code]
    ]

    # Remove matching elements from old lists
    removidos = [i for i in removidos if not any(i[key_SAP_code] == j[old_SAP_tag_for_xl] for j in revisados)]
    adicionados = [i for i in adicionados if not any(i[key_SAP_code] == j[new_SAP_tag_for_xl] for j in revisados)]

    # Verificar itens que mudaram de quantidade.
    mudou_qtd = [
        {
            key_drawing_num : ele_1[key_drawing_num],
            key_SAP_code    : ele_1[key_SAP_code],
            key_description : ele_1[key_description],
            diff_qtd        : - int(ele_1[key_quantities]) + next((int(ele_2[key_quantities]) for ele_2 in lista_nova if ele_1[key_drawing_num] == ele_2[key_drawing_num]), None)
        }
        for ele_1 in lista_velha
        if any(ele_1[key_drawing_num] == ele_2[key_drawing_num] for ele_2 in lista_nova)
    ]
    mudou_qtd = [i for i in mudou_qtd if i[diff_qtd] != 0]

    # Montar lista relatório.
    Lista_para_SAP = [removidos, adicionados, revisados, mudou_qtd]

    return Lista_para_SAP


def orcamentacao(lista):
    lista = extrairdados(lista)
    SAP_key = 'SAP'
    lvl_key = 'Nível'
    qty_key = 'QTD'
    tipo_key = 'Tipo do Item'
    
    solda_interna_key = 'Soldado Internamente'
    solda_comprada_key = 'Comprar'
    
    carenagem  = []
    kit_solda  = []
    conj_solda = []
    soldas_int = []
    
    # 1 - Isolar somente os conjuntos de solda, descartar demais informações.
    soldas = [row for row in lista if row[SAP_key].startswith('520-')]
    lista_filt = [row for row in lista if any(row[lvl_key].startswith(solda[lvl_key]) for solda in soldas)]
    avulsos = [row for row in lista if row not in lista_filt]
    
    # EXTRA - Tratar avulsos.
    deletar = []
    prefixos_carenagem = ['110-', '120-', '130-', '140-']
    
    for index, row in enumerate(avulsos):
        montagem = any(item[lvl_key].startswith(row[lvl_key]) for item in avulsos)
        if montagem:
            componentes = [item for item in avulsos if item[lvl_key].startswith(row[lvl_key])]
            for item in componentes:
                item[qty_key] = item[qty_key] * row[qty_key]
            deletar.append(row)
    
    for index in deletar:
        lista_filt.pop(index)
        
    avulsos_carenagem = [row for row in avulsos if row[SAP_key][0:4] in prefixos_carenagem]
    carenagem.append(avulsos_carenagem)
        
    # 2 - Tratar as soldas internas primeiro:
    # 2.1 - Multiplicar componentes se aplicável.
    deletar = []
    for index, row in enumerate(lista_filt):
        if row in soldas:
            componentes = [item for item in lista_filt if item[lvl_key].startswith(row[lvl_key])]
            if row[tipo_key] == solda_interna_key:
                for item in componentes:
                    item[qty_key] = item[qty_key] * row[qty_key]
                deletar.append(index)
                soldas_int.append(row)
                soldas_int.append(componentes)
            elif row[tipo_key] == solda_comprada_key:
                carenagem.append(row)
                
            
    # 2.2 - Eliminar as linhas de solda interna.
    for index in deletar:
        lista_filt.pop(index)
        
    # 2.4 - Relocar soldas compradas para carenagem.
    for index, row in enumerate(lista_filt):
        pass
        
        
        
    return lista


def orcamentacao2(lista):
    # Procedimento: Repetir as etapas abaixo para todas a montagens do projeto:
    lista = extrairdados(lista)
    
    # Padroes de nomes. Alterar se necessario.
    SAP_key = 'SAP'
    lvl_key = 'Nível'
    qty_key = 'QTD'
    tipo_key = 'Tipo do Item'
    solda_interna_key = 'Soldado Internamente'
    solda_comprada_key = 'Comprar'
    format_key = 'FORMATO'
    
    # Listas vazias para processamento.
    carenagem  = []
    kit_solda  = []
    montagem   = []
    soldas_int = []
    erros      = []
    temp       = []
    
    # Etapa 1: Discriminar tudo que está dentro de uma montagem e o que não. Mover todas as montagens para um grupo separado.
    assemblies  = [row for row in lista if row[format_key] == 'sldasm']
    
    sub_assemblies = []
    groups = []
    
    for assembly in assemblies:
        temp_groups = []
        content = [row for row in lista if any(row[lvl_key].startswith(assembly[lvl_key]))]
        temp_groups.append(assembly)
        temp_groups.extend(content)
        sub_assemblies.append(assembly)
        sub_assemblies.extend(content)
        groups.append(temp_groups)

    avulsos = [row for row in lista if row not in sub_assemblies]

    # Montagem / Montagem Base: 
    # 110, 120, 130, 140 -> Carenagem.
    # Todo o restante -> Montagem.
    metodo_montagem  = {'110' : carenagem,
                        '120' : carenagem,
                        '130' : carenagem,
                        '140' : carenagem}

    # Solda Interna:
    # 110, 120, 130, 140 -> Carenagem.
    # Todo o restante -> Kit Solda.
    metodo_solda_int = {'110' : carenagem,
                        '120' : carenagem,
                        '130' : carenagem,
                        '140' : carenagem,
                        '520' : soldas_int}
    
    # Solda Comprada:
    # 510, 511 -> Kit Solda
    # Todo o restante -> Deletar.
    metodo_solda_com = {'510' : kit_solda,
                        '511' : kit_solda,
                        '520' : carenagem}
    
    # Etapa 3: Processar os itens que estão soltos.
    for item in avulsos:
        metodo_montagem[item[SAP_key][0:4]].append(item)
        

def pastas_de_orc(acervo, destino, lista):
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
    
    # Obter arquivos do acervo.
    arquivos_acervo = listar_desenhos(acervo)
    
    # Gerar nomes.
    for item in lista:
        item.update({"nome_arquivo" : (item["SAP"] + " - " + item["DESENHO"])})
    
    # Obter os conjuntos da lista (que interessam).
    conjuntos = [linha for linha in lista if linha["TIPO"] == "Conjunto"]
    avulsos = [linha for linha in lista if linha["TIPO"] == "Avulso"]
    
    # Output esperado: dicionário com níveis relativos ao nome das pastas.
    # Hierarquizar a lista.
    # Nessa etapa, o objetivo é transformar subconjuntos dentro da lista de dict de cada conjunto em sublistas de dict, recursivamente.
    def rec_hierarquizar(conjunto, itens_do_conjunto):
        adicionados = []
        output = []
        output.append(conjunto)
        for i in itens_do_conjunto:
            if i["TIPO"] == "Subconjunto":
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
        full_path = os.path.join(destino, lista_hierarquizada[0]['nome_arquivo'])
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
    
    for index, linha in enumerate(conjuntos):
        itens_no_conjunto = [item for item in lista if item["Nível"].startswith(linha["Nível"] + ".") and item != linha]
        conjuntos[index], b = rec_hierarquizar(linha, itens_no_conjunto)
        
    for conjunto in conjuntos:
        copiar_arquivos_solda_conjuntos(conjunto, destino)
        
    copiar_arquivos_solda_avulsos(avulsos, destino)

    return


def renomear_arquivos(data, acervo):
    # Corrige nome de arquivos exportados pelo SAP que puxaram códigos errados.
    
    # Input:
        # Data is a list of dictionaries with the data.
        # Acervo is a string of the location of files to be treated.
    # Output:
        # Files whose SAP codes were incorrect will be appropriately renamed according to the data provided.
    
    output = {}
    for item in data:
        key = item['SAP']
        value = str(item['DESENHO']).replace("  ", "")
        output[key] = value
    arquivos = listar_desenhos(acervo)
    
    for file_name in arquivos:
        file_name = os.path.basename(file_name) # Remove file path.
        base_name, extension = os.path.splitext(file_name) # Remove file extension.
    
        if " - " in base_name: # Necessario para funcionar o codigo.
            parts = base_name.split(" - ", 1) # Divide o nome do arquivo para extrair as informacoes.
            part1 = parts[0]
            part2 = parts[1]
        
            # Comparar o nome do arquivo com a correspondencia no dicionario extraido da lista.
            try:
                if part1 != output[part2]:
                # Criar o novo nome do arquivo.
                    correto = str(output[part2]) + " - " + str(part2) + extension
                    print(file_name, "RENOMEADO PARA", correto)
                
                # Processo de renomear o arquivo.
                    old_file_path = os.path.join(acervo, file_name)
                    new_file_path = os.path.join(acervo, correto)
                    os.rename(old_file_path, new_file_path)
            except KeyError:
                print(file_name, "NÃO EXISTE NA LISTA.")