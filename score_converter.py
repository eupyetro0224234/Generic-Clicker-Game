import os
import json
import base64
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class ScoreConverterGUI:
    def __init__(self, root):
        self.encryption_key = b'justanotherkey12'
        self.root = root
        self.root.title("Conversor de Score.dat")
        self.root.geometry("700x550")
        self.root.configure(bg="#e8f0fe")

        self.data = None
        self.raw_data = None
        self.is_binary = False

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Conversor de Score.dat entre versões", font=("Arial", 16, "bold"), bg="#e8f0fe").pack(pady=10)

        tk.Button(self.root, text="Selecionar score.dat antigo", command=self.load_old_file, bg="#4caf50", fg="white", font=("Arial", 12)).pack(pady=10)

        self.output_text = scrolledtext.ScrolledText(self.root, width=80, height=15, font=("Courier", 10))
        self.output_text.pack(pady=10)

        frame = tk.Frame(self.root, bg="#e8f0fe")
        frame.pack(pady=10)

        self.save_mode = tk.StringVar(value="base64")
        tk.Radiobutton(frame, text="Salvar como texto (base64)", variable=self.save_mode, value="base64", bg="#e8f0fe").pack(side="left", padx=10)
        tk.Radiobutton(frame, text="Salvar como binário", variable=self.save_mode, value="binary", bg="#e8f0fe").pack(side="left", padx=10)

        tk.Button(self.root, text="Salvar score.dat convertido", command=self.save_new_file, bg="#2196f3", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_old_file(self):
        path = filedialog.askopenfilename(title="Selecionar score.dat antigo", filetypes=[("score.dat", "*.dat")])
        if not path:
            return

        try:
            with open(path, "rb") as file:
                self.raw_data = file.read()

            # Detecta se é texto ou binário
            try:
                decoded = self.raw_data.decode("utf-8")
                self.data = self.decrypt_base64(decoded)
                self.is_binary = False
            except:
                self.data = self.decrypt_binary(self.raw_data)
                self.is_binary = True

            if not self.data:
                raise Exception("Não foi possível descriptografar os dados.")

            self.show_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo:\n{e}")

    def show_data(self):
        self.output_text.delete(1.0, tk.END)
        pretty = json.dumps(self.data, indent=4, ensure_ascii=False)
        self.output_text.insert(tk.END, pretty)

    def save_new_file(self):
        if not self.data:
            messagebox.showwarning("Aviso", "Você precisa carregar um score.dat primeiro.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("Arquivos DAT", "*.dat")], title="Salvar novo score.dat")
        if not path:
            return

        try:
            if self.save_mode.get() == "base64":
                enc = self.encrypt_base64(self.data)
                with open(path, "w") as f:
                    f.write(enc)
            else:
                enc = self.encrypt_binary(self.data)
                with open(path, "wb") as f:
                    f.write(enc)

            messagebox.showinfo("Sucesso", "Novo score.dat salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar novo arquivo:\n{e}")

    def decrypt_base64(self, encoded):
        try:
            data = base64.b64decode(encoded)
            iv = data[:AES.block_size]
            ct = data[AES.block_size:]
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            return None

    def decrypt_binary(self, data):
        try:
            iv = data[:AES.block_size]
            ct = data[AES.block_size:]
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            return None

    def encrypt_base64(self, data):
        json_data = json.dumps(data).encode('utf-8')
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(json_data, AES.block_size))
        return base64.b64encode(iv + ct).decode('utf-8')

    def encrypt_binary(self, data):
        json_data = json.dumps(data).encode('utf-8')
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(json_data, AES.block_size))
        return iv + ct

# Execução principal
if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreConverterGUI(root)
    root.mainloop()
