import sqlite3
import csv
import os
from pathlib import Path
import shutil
from datetime import datetime

DB_PATH = Path("livraria.db")
BACKUP_DIR = Path("backups")
CSV_DIR = Path("csv")

def create_directories():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"livraria_backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_file)
    clean_old_backups()

def clean_old_backups():
    backups = sorted(BACKUP_DIR.glob("*.db"), key=os.path.getmtime)
    for old_backup in backups[:-5]:
        old_backup.unlink()

def initialize_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                ano_publicacao INTEGER,
                preco REAL
            )
        ''')
        conn.commit()

def add_book(titulo, autor, ano_publicacao, preco):
    backup_database()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO livros (titulo, autor, ano_publicacao, preco)
            VALUES (?, ?, ?, ?)
        ''', (titulo, autor, ano_publicacao, preco))
        conn.commit()

def view_books():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livros')
        return cursor.fetchall()

def update_book_price(book_id, new_price):
    backup_database()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE livros SET preco = ? WHERE id = ?
        ''', (new_price, book_id))
        conn.commit()

def remove_book(book_id):
    backup_database()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM livros WHERE id = ?', (book_id,))
        conn.commit()

def search_books_by_author(author):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livros WHERE autor = ?', (author,))
        return cursor.fetchall()

def export_to_csv(file_name):
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM livros')
            rows = cursor.fetchall()

            with open(CSV_DIR / file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['id', 'titulo', 'autor', 'ano_publicacao', 'preco'])
                writer.writerows(rows)

        print(f"Dados exportados para {CSV_DIR / file_name} com sucesso.")

    except sqlite3.Error as se:
        print(f"Erro ao acessar o banco de dados: {se}")
    except IOError as io_error:
        print(f"Erro ao escrever o arquivo CSV: {io_error}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


def import_from_csv(file_name):
    backup_database()

    try:
        with open(CSV_DIR / file_name, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                for row in reader:
                    if len(row) != 5:
                        print(f"Linha inválida: {row}. Esperado 5 colunas.")
                        continue

                    try:
                        cursor.execute('''
                            INSERT INTO livros (titulo, autor, ano_publicacao, preco)
                            VALUES (?, ?, ?, ?)
                        ''', (row[1], row[2], int(row[3]), float(row[4])))
                    except ValueError as ve:
                        print(f"Erro ao converter dados da linha {row}: {ve}")
                        continue
                    except sqlite3.Error as se:
                        print(f"Erro ao inserir dados no banco de dados: {se}")
                        continue  

                conn.commit()
        print(f"Importação de {file_name} concluída com sucesso.")

    except FileNotFoundError:
        print(f"Arquivo {file_name} não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


def main_menu():
    while True:
        print("\nMenu:")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")

        choice = input("Escolha uma opção: ")
        if choice == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de Publicação: "))
            preco = float(input("Preço: "))
            add_book(titulo, autor, ano_publicacao, preco)
        elif choice == "2":
            books = view_books()
            for book in books:
                print(book)
        elif choice == "3":
            book_id = int(input("ID do livro: "))
            new_price = float(input("Novo preço: "))
            update_book_price(book_id, new_price)
        elif choice == "4":
            book_id = int(input("ID do livro: "))
            remove_book(book_id)
        elif choice == "5":
            autor = input("Autor: ")
            books = search_books_by_author(autor)
            for book in books:
                print(book)
        elif choice == "6":
            file_name = input("Nome do arquivo CSV (ex: livros.csv): ")
            export_to_csv(file_name)
        elif choice == "7":
            file_name = input("Nome do arquivo CSV para importar (ex: livros.csv): ")
            import_from_csv(file_name)
        elif choice == "8":
            backup_database()
            print("Backup realizado com sucesso!")
        elif choice == "9":
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    create_directories()
    initialize_db()
    main_menu()
