import tkinter as tk
from tkinter import filedialog
import tools_ferramentas as ferr
import pandas as pd
import os

#Classe para criar interface grafica.
class GUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Processamento de listas")

        global path_var1
        global path_var2
        global path_var3
        global toggle_var1
        global toggle_var2
        global toggle_var3
        global toggle_var4

        path_var1 = tk.StringVar()
        path_var2 = tk.StringVar()
        path_var3 = tk.StringVar()

        toggle_var1 = tk.BooleanVar()
        toggle_var2 = tk.BooleanVar()
        toggle_var3 = tk.BooleanVar()
        toggle_var4 = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        description1 = tk.Label(self.root, text="Lista:")
        description1.pack()

        self.path_entry1 = tk.Entry(self.root, textvariable=path_var1)
        self.path_entry1.pack(fill=tk.X, padx=10)

        browse_button1 = tk.Button(self.root, text="Buscar", command=self.browse_path1)
        browse_button1.pack()

        description2 = tk.Label(self.root, text="Destino:")
        description2.pack()

        self.path_entry2 = tk.Entry(self.root, textvariable=path_var2)
        self.path_entry2.pack(fill=tk.X, padx=10)

        browse_button2 = tk.Button(self.root, text="Buscar", command=self.browse_path2)
        browse_button2.pack()

        description3 = tk.Label(self.root, text="Acervo:")
        description3.pack()

        self.path_entry3 = tk.Entry(self.root, textvariable=path_var3)
        self.path_entry3.pack(fill=tk.X, padx=10)

        browse_button3 = tk.Button(self.root, text="Buscar", command=self.browse_path3)
        browse_button3.pack()

        #toggle_button1 = tk.Checkbutton(self.root, text="Lista SAP", variable=toggle_var1)
        #toggle_button1.pack()

        #toggle_button2 = tk.Checkbutton(self.root, text="Orçamento", variable=toggle_var2)
        #toggle_button2.pack()

        toggle_button3 = tk.Checkbutton(self.root, text="Copiar Desenhos", variable=toggle_var3)
        toggle_button3.pack()

        toggle_button4 = tk.Checkbutton(self.root, text="Pasta de Solda", variable=toggle_var4)
        toggle_button4.pack()

        run_button = tk.Button(self.root, text="Rodar", command=self.run_program)
        run_button.pack()

    def browse_path1(self):
        path = filedialog.askopenfilename()
        path_var1.set(path)

    def browse_path2(self):
        path = filedialog.askdirectory()
        path_var2.set(path)

    def browse_path3(self):
        path = filedialog.askdirectory()
        path_var3.set(path)

    def run_program(self):
        print("Running the program...")
        print("Path 1:", path_var1.get())
        print("Path 2:", path_var2.get())
        print("Path 3:", path_var3.get())
        print("Toggle 1:", toggle_var1.get())
        print("Toggle 2:", toggle_var2.get())
        print("Toggle 3:", toggle_var3.get())
        print("Toggle 4:", toggle_var4.get())
        root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.title("Automatização de tarefas")
    root.geometry("500x300")
    root.mainloop()

#Converter variaveis de widgets para string e bool.
path_var1 = path_var1.get()
path_var2 = path_var2.get()
path_var3 = path_var3.get()
toggle_var1 = toggle_var1.get()
toggle_var2 = toggle_var2.get()
toggle_var3 = toggle_var3.get()
toggle_var4 = toggle_var4.get()

#Esse trecho serve para trocar os separadores do arquivo csv por algo que funcione.
input_file_path = path_var1
output_file_path = "output.csv"
old_delimiter = ';'
new_delimiter = '|'
ferr.remove_and_replace_delimiters(input_file_path, output_file_path, old_delimiter, new_delimiter)
lista = ferr.extrairdados(output_file_path)
files_grabbed = ferr.listar_desenhos(path_var3)

#Separacao para inserir no SAP a estrutura da maquina em questao.
if toggle_var1 == True:
    Lista_para_SAP = ferr.sepSAP(lista)
    with pd.ExcelWriter('resultados.xlsx') as writer:
        k = 0
        for i in Lista_para_SAP:
            j = pd.DataFrame(data=i)
            j.to_excel(writer, sheet_name=str(k))
            k += 1

#Separacao para criar lista de orcamento para fornecedor teimoso.
if toggle_var2 == True:
    Orcamento_tera = ferr.orcamentacao(lista)
    with pd.ExcelWriter('orcamento.xlsx') as writer:
        k = 0
        for i in Lista_para_SAP:
            j = pd.DataFrame(data=i)
            j.to_excel(writer, sheet_name=str(k))
            k += 1

#Procedimento de copia de desenhos para pasta destino.
if toggle_var3 == True:
    SAPs = [lista[x]['SAP'] for x in range(len(lista))]
    ferr.copiar_arquivos3(path_var2, files_grabbed, lista)
    ferr.separar_grupos_desenhos(path_var2,path_var2)

if toggle_var4 == True:
    ferr.pasta_de_solda(path_var2, files_grabbed, lista, nome_projeto="padrao")

if os.path.isfile(output_file_path):
    os.remove(output_file_path)