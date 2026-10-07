import customtkinter as ctk
import os
import sqlite3
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


#conectar banco
def conectar():
    caminho = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sistema.db2"
    )

    conexao = sqlite3.connect(caminho)
    cursor = conexao.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS produtos(
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )""")

    conexao.commit()

    return conexao, cursor


#consultar produtos
def consultar_produto():
    for widget in caixa_resultados.winfo_children():
        widget.destroy()

    conexao, cursor = conectar()

    cursor.execute("SELECT * FROM produtos")
    itens = cursor.fetchall()

    conexao.close()

    if not itens:
        ctk.CTkLabel(
            caixa_resultados,
            text="Nenhum produto cadastrado."
        ).pack(pady=10)

    for nome, preco, quantidade in itens:

        linha = ctk.CTkFrame(caixa_resultados)
        linha.pack(fill="x", pady=5, padx=5)

        if quantidade < 5:
            cor_estoque = "red"
        else:
            cor_estoque = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

        ctk.CTkLabel(
            linha,
            text=f"{nome} | R$ {preco:.2f} | Estoque: {quantidade}",
            text_color=cor_estoque
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            linha,
            text="Vender",
            width=70,
            fg_color="green",
            command=lambda n=nome: vender_produto(n)
        ).pack(side="right", padx=3)

        ctk.CTkButton(
            linha,
            text="Editar",
            width=70,
            command=lambda n=nome: editar_produto(n)
        ).pack(side="right", padx=3)

        ctk.CTkButton(
            linha,
            text="Deletar",
            width=70,
            command=lambda n=nome: deletar_produto(n)
        ).pack(side="right", padx=3)


#cadastrar produto
def cadastrar_produto():
    nome = entry_nome.get().strip()

    try:
        preco = float(entry_preco.get())
        quantidade = int(entry_quantidade.get())

        if not nome or preco < 0 or quantidade < 0:
            raise ValueError

        conexao, cursor = conectar()

        cursor.execute(
            "SELECT * FROM produtos WHERE nome = ?",
            (nome,)
        )

        if cursor.fetchone():
            messagebox.showwarning(
                "Aviso",
                "Este produto já está cadastrado!"
            )

        else:
            cursor.execute(
                "INSERT INTO produtos VALUES (?, ?, ?)",
                (nome, preco, quantidade)
            )

            conexao.commit()

            messagebox.showinfo(
                "Sucesso",
                "Produto cadastrado!"
            )

        conexao.close()

        entry_nome.delete(0, "end")
        entry_preco.delete(0, "end")
        entry_quantidade.delete(0, "end")

        consultar_produto()

    except ValueError:
        messagebox.showwarning(
            "Aviso",
            "Digite valores válidos!"
        )

        entry_preco.delete(0, "end")
        entry_quantidade.delete(0, "end")


#vender produto
def vender_produto(nome_produto):
    conexao, cursor = conectar()

    cursor.execute(
        "SELECT quantidade FROM produtos WHERE nome = ?",
        (nome_produto,)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        messagebox.showwarning(
            "Aviso",
            "Produto não encontrado!"
        )

        conexao.close()
        return

    qtd_atual = resultado[0]

    if qtd_atual > 0:
        nova_qtd = qtd_atual - 1

        cursor.execute(
            "UPDATE produtos SET quantidade = ? WHERE nome = ?",
            (nova_qtd, nome_produto)
        )

        conexao.commit()
        conexao.close()

        consultar_produto()

    else:
        conexao.close()

        messagebox.showwarning(
            "Aviso",
            "Produto Esgotado!"
        )


#editar produto
def editar_produto(nome):
    janela_editar = ctk.CTkToplevel(janela)
    janela_editar.title("Editar Produto")
    janela_editar.geometry("300x220")

    ctk.CTkLabel(
        janela_editar,
        text=f"Editando: {nome}"
    ).pack(pady=10)

    preco = ctk.CTkEntry(
        janela_editar,
        placeholder_text="Novo preço"
    )
    preco.pack(pady=5)

    quantidade = ctk.CTkEntry(
        janela_editar,
        placeholder_text="Nova quantidade"
    )
    quantidade.pack(pady=5)

    #salvar edição
    def salvar():
        try:
            novo_preco = float(preco.get())
            nova_quantidade = int(quantidade.get())

            if novo_preco < 0 or nova_quantidade < 0:
                raise ValueError

            conexao, cursor = conectar()

            cursor.execute(
                """UPDATE produtos
                   SET preco = ?, quantidade = ?
                   WHERE nome = ?""",
                (novo_preco, nova_quantidade, nome)
            )

            conexao.commit()
            conexao.close()

            janela_editar.destroy()

            consultar_produto()

        except ValueError:
            messagebox.showwarning(
                "Aviso",
                "Digite valores válidos!"
            )

    ctk.CTkButton(
        janela_editar,
        text="Salvar",
        command=salvar
    ).pack(pady=10)


#deletar produto
def deletar_produto(nome):
    conexao, cursor = conectar()

    cursor.execute(
        "DELETE FROM produtos WHERE nome = ?",
        (nome,)
    )

    conexao.commit()
    conexao.close()

    consultar_produto()


#abrir sistema
def abrir_sistema_principal():
    global janela
    global entry_nome
    global entry_preco
    global entry_quantidade
    global caixa_resultados

    janela_login.destroy()

    janela = ctk.CTk()
    janela.title("Lanchonete Ennius Muniz - Senac-DF")
    janela.geometry("600x650")

    ctk.CTkLabel(
        janela,
        text="=== SISTEMA DE CONTROLE (SQLite) ==="
    ).pack(pady=20)

    entry_nome = ctk.CTkEntry(
        janela,
        placeholder_text="1. Nome do Produto",
        width=350
    )
    entry_nome.pack(pady=10)

    entry_preco = ctk.CTkEntry(
        janela,
        placeholder_text="2. Preço (Ex: 5.00)",
        width=350
    )
    entry_preco.pack(pady=10)

    entry_quantidade = ctk.CTkEntry(
        janela,
        placeholder_text="3. Quantidade em Estoque",
        width=350
    )
    entry_quantidade.pack(pady=10)

    ctk.CTkButton(
        janela,
        text="Salvar Produtos",
        fg_color="green",
        command=cadastrar_produto
    ).pack(pady=15)

    ctk.CTkButton(
        janela,
        text="Consultar Produtos Salvos",
        command=consultar_produto
    ).pack(pady=5)

    caixa_resultados = ctk.CTkScrollableFrame(
        janela,
        width=520,
        height=250
    )
    caixa_resultados.pack(pady=20)

    janela.mainloop()


#validar login
def validar_login():
    usuario = entry_user.get()
    senha = entry_senha.get()

    if usuario == "admin" and senha == "1234":
        abrir_sistema_principal()

    else:
        messagebox.showerror(
            "Acesso Negado!",
            "Usuário ou senha incorretos"
        )


#iniciar programa
janela_login = ctk.CTk()
janela_login.geometry("500x300")
janela_login.title("Login")

ctk.CTkLabel(
    janela_login,
    text="LOGIN",
    font=("Arial", 24)
).pack(pady=20)

entry_user = ctk.CTkEntry(
    janela_login,
    placeholder_text="Usuário",
    width=250
)
entry_user.pack(pady=10)

entry_senha = ctk.CTkEntry(
    janela_login,
    placeholder_text="Senha",
    show="*",
    width=250
)
entry_senha.pack(pady=10)

ctk.CTkButton(
    janela_login,
    text="Entrar",
    command=validar_login,
    width=250
).pack(pady=15)

janela_login.mainloop()