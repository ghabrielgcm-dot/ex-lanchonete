import customtkinter as ctk
import os
import sqlite3
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def conectar():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema.db2")
    conexao = sqlite3.connect(caminho)
    cursor = conexao.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS produtos(
        nome TEXT, preco REAL, quantidade INTEGER)""")
    conexao.commit()
    return conexao, cursor

def consultar_produto():
    for widget in caixa_resultados.winfo_children():
        widget.destroy()

    conexao, cursor = conectar()
    cursor.execute("SELECT * FROM produtos")
    itens = cursor.fetchall()
    conexao.close()

    if not itens:
        ctk.CTkLabel(caixa_resultados, text="Nenhum produto cadastrado.").pack(pady=10)

    for nome, preco, quantidade in itens:
        linha = ctk.CTkFrame(caixa_resultados)
        linha.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(linha, text=f"{nome} | R$ {preco:.2f} | Estoque: {quantidade}").pack(side="left", padx=5)
        ctk.CTkButton(linha, text="Editar", width=70,
                      command=lambda n=nome: editar_produto(n)).pack(side="right", padx=3)
        ctk.CTkButton(linha, text="Deletar", width=70,
                      command=lambda n=nome: deletar_produto(n)).pack(side="right", padx=3)

def cadastrar_produto():
    nome = entry_nome.get().strip()
    try:
        preco = float(entry_preco.get())
        quantidade = int(entry_quantidade.get())

        if not nome or preco < 0 or quantidade < 0:
            raise ValueError

        conexao, cursor = conectar()
        cursor.execute("SELECT * FROM produtos WHERE nome = ?", (nome,))
        if cursor.fetchone():
            messagebox.showwarning("Aviso", "Este produto já está cadastrado!")
        else:
            cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)", (nome, preco, quantidade))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado!")
        conexao.close()
        consultar_produto()

        
        entry_nome.delete(0, "end")
        entry_preco.delete(0, "end")
        entry_quantidade.delete(0, "end")

    except ValueError:
        messagebox.showwarning("Aviso", "Digite valores válidos!")

        
        entry_preco.delete(0, "end")
        entry_quantidade.delete(0, "end")
        
def editar_produto(nome):
    janela_editar = ctk.CTkToplevel(janela)
    janela_editar.title("Editar Produto")
    janela_editar.geometry("300x220")

    ctk.CTkLabel(janela_editar, text=f"Editando: {nome}").pack(pady=10)
    preco = ctk.CTkEntry(janela_editar, placeholder_text="Novo preço")
    preco.pack(pady=5)
    quantidade = ctk.CTkEntry(janela_editar, placeholder_text="Nova quantidade")
    quantidade.pack(pady=5)

    def salvar():
        try:
            conexao, cursor = conectar()
            cursor.execute("UPDATE produtos SET preco = ?, quantidade = ? WHERE nome = ?",
                           (float(preco.get()), int(quantidade.get()), nome))
            conexao.commit()
            conexao.close()
            janela_editar.destroy()
            consultar_produto()
        except ValueError:
            messagebox.showwarning("Aviso", "Digite valores válidos!")

    ctk.CTkButton(janela_editar, text="Salvar", command=salvar).pack(pady=10)

def deletar_produto(nome):
    conexao, cursor = conectar()
    cursor.execute("DELETE FROM produtos WHERE nome = ?", (nome,))
    conexao.commit()
    conexao.close()
    consultar_produto()

janela = ctk.CTk()
janela.title("Lanchonete Ennius Muniz - Senac-DF")
janela.geometry("600x650")

ctk.CTkLabel(janela, text="=== SISTEMA DE CONTROLE (SQLite) ===").pack(pady=20)

entry_nome = ctk.CTkEntry(janela, placeholder_text="1. Nome do Produto", width=350)
entry_nome.pack(pady=10)

entry_preco = ctk.CTkEntry(janela, placeholder_text="2. Preço (Ex: 5.00)", width=350)
entry_preco.pack(pady=10)

entry_quantidade = ctk.CTkEntry(janela, placeholder_text="3. Quantidade em Estoque", width=350)
entry_quantidade.pack(pady=10)

ctk.CTkButton(janela, text="Salvar Produtos", fg_color="green",
              command=cadastrar_produto).pack(pady=15)

ctk.CTkButton(janela, text="Consultar Produtos Salvos",
              command=consultar_produto).pack(pady=5)

caixa_resultados = ctk.CTkScrollableFrame(janela, width=520, height=250)
caixa_resultados.pack(pady=20)

janela.mainloop()