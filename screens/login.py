import customtkinter as ctk
from tkinter import messagebox

from database import get_connection


class LoginScreen(ctk.CTkFrame):

    def __init__(self, master, on_login_success):
        super().__init__(master)

        self.master = master
        self.on_login_success = on_login_success

        self.build_ui()

    def build_ui(self):

        # Main container
        self.container = ctk.CTkFrame(
            self,
            width=450,
            height=500,
            corner_radius=20
        )

        self.container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # System title
        self.title_label = ctk.CTkLabel(
            self.container,
            text="GIDEON MANAGEMENT SYSTEM",
            font=("Arial", 25, "bold")
        )

        self.title_label.pack(
            pady=(45, 10)
        )

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.container,
            text="Login to continue",
            font=("Arial", 16)
        )

        self.subtitle_label.pack(
            pady=(0, 35)
        )

        # Username
        self.username_label = ctk.CTkLabel(
            self.container,
            text="Username",
            font=("Arial", 15)
        )

        self.username_label.pack(
            anchor="w",
            padx=50
        )

        self.username_entry = ctk.CTkEntry(
            self.container,
            width=350,
            height=45,
            placeholder_text="Enter username"
        )

        self.username_entry.pack(
            pady=(5, 20)
        )

        # Password
        self.password_label = ctk.CTkLabel(
            self.container,
            text="Password",
            font=("Arial", 15)
        )

        self.password_label.pack(
            anchor="w",
            padx=50
        )

        self.password_entry = ctk.CTkEntry(
            self.container,
            width=350,
            height=45,
            placeholder_text="Enter password",
            show="*"
        )

        self.password_entry.pack(
            pady=(5, 25)
        )

        # Login button
        self.login_button = ctk.CTkButton(
            self.container,
            text="LOGIN",
            width=350,
            height=45,
            font=("Arial", 16, "bold"),
            command=self.login
        )

        self.login_button.pack(
            pady=10
        )

        # Status
        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 13)
        )

        self.status_label.pack(
            pady=10
        )

        # Enter key
        self.username_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        # Focus username
        self.username_entry.focus()

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(
                text="Please enter username and password."
            )
            return

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, full_name, username, role
            FROM users
            WHERE username = ?
            AND password = ?
            AND is_active = 1
        """, (username, password))

        user = cursor.fetchone()

        connection.close()

        if user:

            self.status_label.configure(
                text="Login successful."
            )

            self.on_login_success(dict(user))

        else:

            self.status_label.configure(
                text="Invalid username or password."
            )

            self.password_entry.delete(
                0,
                "end"
            )