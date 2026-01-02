import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
 

# Banco de Dados

def criar_tabelas():
    con = sqlite3.connect("avaliador_de_marcas.db")
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS marcas(
            id INTEGER NOT NULL PRIMARY KEY,
            nome TEXT NOT NULL,
            estilo TEXT NOT NULL,
            origem TEXT NOT NULL);
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS avaliacoes(
            id INTEGER NOT NULL PRIMARY KEY,
            marca_id INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            nota INTEGER CHECK (nota BETWEEN 1 AND 5),
            comentario TEXT,
            data_avaliacao DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (marca_id) REFERENCES marcas(id));
        """
    )

    con.commit()
    con.close()


def buscar_marcas():
    con = sqlite3.connect("avaliador_de_marcas.db")
    cur = con.cursor()

    cur.execute("SELECT id, nome, estilo, origem FROM marcas ORDER BY id")

    marcas = cur.fetchall()
    con.close()
    return marcas


def salvar_marca_bd(nome, estilo, origem):
    con = sqlite3.connect("avaliador_de_marcas.db")
    cur = con.cursor()

    cur.execute("INSERT INTO marcas (nome, estilo, origem) VALUES (?, ?, ?)", (nome, estilo, origem))

    con.commit()
    con.close()


def salvar_avaliacao_bd(marca_id, usuario, nota, comentario):
    con = sqlite3.connect("avaliador_de_marcas.db")
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO avaliacoes (marca_id, usuario, nota, comentario)
        VALUES (?, ?, ?, ?)
        """, (marca_id, usuario, nota, comentario))
    
    con.commit()
    con.close()


# Interface Tkinter

def abrir_cadastrar():
    cadastrar = tk.Toplevel()
    cadastrar.title("Avaliador de Marcas")
    cadastrar.geometry("700x500")
    tk.Label(cadastrar, text="Cadastre uma marca!", font=("Arial", 14)).pack(pady=50)

    tk.Label(cadastrar, text="Marca").pack()
    entrada_marca = tk.Entry(cadastrar, width=20)
    entrada_marca.pack(pady=10)

    tk.Label(cadastrar, text="Estilo").pack()
    estilos = ["Streetwear", "Esporte", "Casual", "Alta Costura", "Geral"]
    entrada_estilo = ttk.Combobox(cadastrar, values=estilos, state="reandoly", width=18)
    entrada_estilo.pack(pady=5)

    tk.Label(cadastrar, text="Origem").pack()
    entrada_origem = tk.Entry(cadastrar, width=20)
    entrada_origem.pack(pady=5)

    def salvar_marca():
        marca = entrada_marca.get()
        estilo = entrada_estilo.get()
        origem = entrada_origem.get()

        if not marca.strip() or not estilo.strip() or not origem.strip():
            messagebox.showwarning("Erro", "Preencha todos os campos antes de salvar!")
            cadastrar.lift()
            return

        salvar_marca_bd(marca, estilo, origem)

        messagebox.showinfo("Marca cadastrada",
                            f"{marca}\nEstilo: {estilo}\nOrigem: {origem}")
        
        cadastrar.lift()

        entrada_marca.delete(0, tk.END)
        entrada_estilo.delete(0, tk.END)
        entrada_origem.delete(0, tk.END)

    tk.Button(cadastrar, text="Salvar", command=salvar_marca).pack(pady=10)
    tk.Button(cadastrar, text="Cancelar", command=cadastrar.destroy).pack()


def abrir_editar():
    editar = tk.Toplevel()
    editar.title("Avaliador de Marcas")
    editar.geometry("700x500")

    tk.Label(editar, text="Deseja editar ou remover algum cadastro?",
             font=("Arial", 14)).pack(pady=50)

    marcas = buscar_marcas()

    if not marcas:
        tk.Label(editar, text="Nenhuma marca cadastrada.").pack()
        editar.lift()
        return

    lista = tk.Listbox(editar, width=60)
    lista.pack()

    for id, nome, estilo, origem in marcas:
        lista.insert(tk.END, f"{id} - {nome} ({estilo}, {origem})")

    def editar_marca():
        selecao = lista.curselection()
        if not selecao:
            messagebox.showwarning("Erro", "Selecione uma marca!")
            editar.lift()
            return

        item = lista.get(selecao[0])
        marca_id = int(item.split(" - ")[0])

        con = sqlite3.connect("avaliador_de_marcas.db")
        cur = con.cursor()

        cur.execute("SELECT nome, estilo, origem FROM marcas WHERE id=?", (marca_id,))

        nome, estilo, origem = cur.fetchone()
        con.close()

        janela_edit = tk.Toplevel(editar)
        janela_edit.title("Editar Marca")
        janela_edit.geometry("400x300")

        tk.Label(janela_edit, text="Editar Marca", font=("Arial", 14)).pack(pady=20)

        tk.Label(janela_edit, text="Nome:").pack()
        campo_nome = tk.Entry(janela_edit, width=30)
        campo_nome.insert(0, nome)
        campo_nome.pack(pady=5)

        tk.Label(janela_edit, text="Estilo:").pack()
        estilos_edit = ["Streetwear", "Esporte", "Casual", "Alta Costura", "Geral"]
        campo_estilo = ttk.Combobox(janela_edit, values=estilos_edit, state="reandonly", width=30)
        campo_estilo.pack(pady=5)

        tk.Label(janela_edit, text="Origem:").pack()
        campo_origem = tk.Entry(janela_edit, width=30)
        campo_origem.insert(0, origem)
        campo_origem.pack(pady=5)

        def salvar_edicao():
            novo_nome = campo_nome.get()
            novo_estilo = campo_estilo.get()
            nova_origem = campo_origem.get()

            if not novo_nome.strip() or not novo_estilo.strip() or not nova_origem.strip():
                messagebox.showwarning("Erro", "Preencha todos os campos!")
                janela_edit.lift()
                return

            con = sqlite3.connect("avaliador_de_marcas.db")
            cur = con.cursor()

            cur.execute(
                """
                UPDATE marcas
                SET nome=?, estilo=?, origem=?
                WHERE id=?
                """, (novo_nome, novo_estilo, nova_origem, marca_id)
            )
            
            con.commit()
            con.close()
            lista.delete(selecao[0])
            lista.insert(selecao[0], f"{marca_id} - {novo_nome} ({novo_estilo}, {nova_origem})")

            messagebox.showinfo("OK", "Marca atualizada!")
            janela_edit.destroy()
            editar.lift()

        tk.Button(janela_edit, text="Confirmar", command=salvar_edicao).pack(pady=10)
        tk.Button(janela_edit, text="Cancelar", command=janela_edit.destroy).pack()


    def remover():
        selecao = lista.curselection()
        if not selecao:
            messagebox.showwarning("Erro", "Selecione uma marca!")
            editar.lift()
            return

        item = lista.get(selecao[0])
        marca_id = int(item.split(" - ")[0])

        con = sqlite3.connect("avaliador_de_marcas.db")
        cur = con.cursor()

        cur.execute("DELETE FROM avaliacoes WHERE marca_id=?", (marca_id,))
        cur.execute("DELETE FROM marcas WHERE id=?", (marca_id,))
        
        con.commit()
        con.close()

        messagebox.showinfo("Removido", "Marca removida com sucesso!")
        editar.lift()
        lista.delete(selecao[0])
        

    tk.Button(editar, text="Editar", command=editar_marca).pack(pady=10)
    tk.Button(editar, text="Remover", command=remover).pack(pady=10)
    tk.Button(editar, text="Cancelar", command=editar.destroy).pack()


def abrir_avaliar():
    avaliar = tk.Toplevel()
    avaliar.title("Avaliador de Marcas")
    avaliar.geometry("900x700")
    tk.Label(avaliar, text="Deseja avaliar alguma marca?", font=("Arial", 14)).pack(pady=50)

    marcas = buscar_marcas()

    if not marcas:
        tk.Label(avaliar, text="Nenhuma marca cadastrada.").pack()
        avaliar.lift()
        return

    lista = tk.Listbox(avaliar, width=60)
    lista.pack()

    for id, nome, estilo, origem in marcas:
        lista.insert(tk.END, f"{id} - {nome} ({estilo}, {origem})")


    tk.Label(avaliar, text="Digite seu nome:").pack()
    entrada_usuario = tk.Entry(avaliar, width=20)
    entrada_usuario.pack(pady=15)

    tk.Label(avaliar, text="Nota:").pack()
    entrada_nota = tk.Scale(avaliar, from_=1, to=5, orient="horizontal")
    entrada_nota.pack(pady=7)

    tk.Label(avaliar, text="Você recomendaria esta marca?").pack()
    entrada_recomenda = tk.IntVar(value=-1)
    check = tk.Radiobutton(avaliar, text="Sim", variable=entrada_recomenda, value=1)
    check2 = tk.Radiobutton(avaliar, text="Não", variable=entrada_recomenda, value=0)
    check.pack()
    check2.pack()

    tk.Label(avaliar, text="Comentário:").pack()
    entrada_coment = tk.Entry(avaliar, width=40)
    entrada_coment.pack(pady=15)

    def confirmar():
        selecao = lista.curselection()
        usuario = entrada_usuario.get()
        nota = entrada_nota.get()
        comentario = entrada_coment.get()

        if not selecao:
            messagebox.showwarning("Erro", "Selecione uma marca!")
            avaliar.lift()
            return

        if not usuario.strip():
            messagebox.showwarning("Erro", "Preencha todos os campos obrigatórios!")
            avaliar.lift()
            return

        try:
            nota = int(nota)
            if nota < 1 or nota > 5:
                raise ValueError
        except:
            messagebox.showwarning("Erro", "A nota deve ser um número entre 1 e 5.")
            avaliar.lift()
            return

        marca_id = int(lista.get(selecao[0]).split(" - ")[0])

        salvar_avaliacao_bd(marca_id, usuario, nota, comentario)

        messagebox.showinfo("Sucesso", "Avaliação registrada!")
        entrada_usuario.delete(0, tk.END)
        entrada_coment.delete(0, tk.END)
        avaliar.destroy()

    tk.Button(avaliar, text="Confirmar", command=confirmar).pack(pady=10)
    tk.Button(avaliar, text="Cancelar", command=avaliar.destroy).pack()


def abrir_avaliacoes():
    avaliacoes = tk.Toplevel()
    avaliacoes.title("Avaliador de Marcas")
    avaliacoes.geometry("1000x800")
    tk.Label(avaliacoes, text="Avaliações das Marcas", font=("Arial", 14)).pack(pady=20)

    con = sqlite3.connect("avaliador_de_marcas.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT m.nome, a.usuario, a.nota, a.comentario, a.data_avaliacao
        FROM avaliacoes a
        JOIN marcas m ON m.id = a.marca_id
        ORDER BY a.id DESC
        """
    )
    dados = cur.fetchall()
    
    cur.execute(
        """
        SELECT m.nome, AVG(a.nota)
        FROM avaliacoes a
        JOIN marcas m ON m.id = a.marca_id
        GROUP BY m.nome
        """
    )
    medias = cur.fetchall()

    cur.execute(
        """
        SELECT estilo, COUNT(*) 
        FROM marcas
        GROUP BY estilo
        """
    )
    estilos = cur.fetchall()

    con.close()

    lista = tk.Listbox(avaliacoes, width=80)
    lista.pack()

    if not dados:
        lista.insert(tk.END, "Nenhuma avaliação registrada.")
    else:
        for nome, usuario, nota, comentario, data in dados:
            lista.insert(tk.END, f"{nome} - {usuario} ({nota}/5 em {data}): {comentario}")


    # Gráficos
    frame_gráficos = tk.Frame(avaliacoes)
    frame_gráficos.pack(pady=10)

    frame_esquerda = tk.Frame(frame_gráficos)
    frame_esquerda.pack(side="left", padx=10)

    frame_direita = tk.Frame(frame_gráficos)
    frame_direita.pack(side="left", padx=10)

    if medias:
        marcas = [m[0] for m in medias]
        notas = [m[1] for m in medias]

        fig, ax = plt.subplots(figsize=(3, 2))
        ax.bar(marcas, notas)
        ax.set_title("Média das Avaliações por Marca", fontsize=9)
        ax.set_xlabel("Marca", fontsize=7)
        ax.set_ylabel("Nota Média (0 a 5)", fontsize=8)
        plt.xticks(fontsize=7, rotation=0)
        plt.yticks(fontsize=7)
        
    canvas = FigureCanvasTkAgg(fig, master=frame_esquerda)
    canvas.draw()
    canvas.get_tk_widget().pack()

    if estilos:
        nomes_estilos = [e[0] for e in estilos]
        quantidades = [e[1] for e in estilos]

        fig2, ax2 = plt.subplots(figsize=(3, 2))
        ax2.pie(quantidades, labels=nomes_estilos, autopct="%1.1f%%", textprops={'fontsize' : 7})
        ax2.set_title("Distribuição de Estilos das Marcas", fontsize=10)

    canvas2 = FigureCanvasTkAgg(fig2, master=frame_direita)
    canvas2.draw()
    canvas2.get_tk_widget().pack()

    tk.Button(avaliacoes, text="Fechar", command=avaliacoes.destroy).pack(pady=10)


# Janela Principal

criar_tabelas()

janela = tk.Tk()
janela.title("Tela Inicial")
janela.geometry("1000x700")
janela.config(bg="#E0F7FA")

label = tk.Label(janela, text="Avaliador de Marcas!",
                 font=("Arial", 14, "bold"), bg="#E0F7FA")
label.pack(pady=20)

tk.Button(janela, text="Cadastrar", command=abrir_cadastrar,
          bg="#000000", fg="white", font=("Arial", 12)).pack(pady=25)

tk.Button(janela, text="Editar", command=abrir_editar,
          bg="#000000", fg="white", font=("Arial", 12)).pack(pady=25)

tk.Button(janela, text="Avaliar", command=abrir_avaliar,
          bg="#000000", fg="white", font=("Arial", 12)).pack(pady=25)

tk.Button(janela, text="Avaliações", command=abrir_avaliacoes,
          bg="#000000", fg="white", font=("Arial", 12)).pack(pady=25)

tk.Button(janela, text="Fechar", command=janela.destroy,
          bg="#000000", fg="white", font=("Arial", 12)).pack()

janela.mainloop()
