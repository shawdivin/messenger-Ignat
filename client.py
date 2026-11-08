import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.label = None
        self.username_entry = None
        self.save_btn = None

        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300,fg_color="#1a1d24")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='▶️',fg_color="black",border_color="#00FF00",border_width=2,hover_color="green", command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # main
        self.chat_field = CTkTextbox(self, font=('calibri', 14, 'bold'),fg_color="#222629", state='disable')
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:',font=("Calibri", 18), height=40, border_color="#00FF00",border_width=2, fg_color="black", text_color="white")
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', font=("Arial", 28,), fg_color="black",border_width=2,border_color="#00FF00", hover_color="green",width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.username = 'Artem2'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 1111))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()


            self.label = CTkLabel(self.menu_frame, text='Імʼя', font=("Calibri", 38), text_color="white")
            self.label.pack(pady=30)

            self.username_entry = CTkEntry(self.menu_frame, placeholder_text="Введіть ім'я",font=("Calibri", 18), border_color="#00FF00",border_width=2, fg_color="black", text_color="white")
            self.username_entry.pack(pady=5)
            self.username_entry.insert(0, self.username)

            self.save_btn = CTkButton(self.menu_frame, text="Зберегти",font=("Calibri", 15),border_color="#00FF00",hover_color="green",border_width=2,fg_color="black", command=self.save_username)
            self.save_btn.pack(pady=10)

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.username_entry:
                self.label.destroy()
                self.username_entry.destroy()
                if self.save_btn:
                    self.save_btn.destroy()
                    self.save_btn = None

    def save_username(self):
        new_name = self.username_entry.get().strip()
        if new_name and new_name != self.username:
            old_name = self.username
            self.username = new_name
            self.add_message(f"[SYSTEM] Ім'я змінено на: {self.username}")

            try:
                data = f"TEXT@{self.username}@[SYSTEM] {old_name} змінив(ла) ім'я на {self.username}\n"
                self.sock.sendall(data.encode())
            except:
                pass

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, '' + text + '\n')
        self.chat_field.configure(state='disable')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]

                self.add_message(f"{author} надіслав(ла) зображення: {filename}")

        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()