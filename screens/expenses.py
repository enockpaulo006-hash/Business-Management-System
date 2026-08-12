import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from database import get_connection


class ExpensesScreen(ctk.CTkFrame):

    def __init__(self, master, current_user=None):
        super().__init__(master)

        self.current_user = current_user

        self.build_ui()
        self.load_expenses()

    # =========================
    # BUILD UI
    # =========================

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="EXPENSES / MONEY USED",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Record money spent by the shop",
            font=("Arial", 15)
        )
        subtitle.pack(pady=(0, 15))

        # =========================
        # FORM
        # =========================

        form = ctk.CTkFrame(self)
        form.pack(
            fill="x",
            padx=25,
            pady=10
        )

        # Category
        ctk.CTkLabel(
            form,
            text="Category"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.category_entry = ctk.CTkEntry(
            form,
            width=180,
            placeholder_text="e.g. Food"
        )
        self.category_entry.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 12)
        )

        # Description
        ctk.CTkLabel(
            form,
            text="Description"
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.description_entry = ctk.CTkEntry(
            form,
            width=280,
            placeholder_text="e.g. Lunch for workers"
        )
        self.description_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 12)
        )

        # Amount
        ctk.CTkLabel(
            form,
            text="Amount (TSh)"
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.amount_entry = ctk.CTkEntry(
            form,
            width=170,
            placeholder_text="e.g. 10000"
        )
        self.amount_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 12)
        )

        # Date
        ctk.CTkLabel(
            form,
            text="Expense Date"
        ).grid(
            row=0,
            column=3,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.date_entry = ctk.CTkEntry(
            form,
            width=150
        )

        self.date_entry.insert(
            0,
            str(date.today())
        )

        self.date_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=(0, 12)
        )

        # Add expense
        self.add_button = ctk.CTkButton(
            form,
            text="ADD EXPENSE",
            width=145,
            height=40,
            font=("Arial", 14, "bold"),
            command=self.add_expense
        )

        self.add_button.grid(
            row=1,
            column=4,
            padx=15,
            pady=(0, 12)
        )

        # =========================
        # TOTAL
        # =========================

        summary = ctk.CTkFrame(self)
        summary.pack(
            fill="x",
            padx=25,
            pady=(10, 5)
        )

        self.total_label = ctk.CTkLabel(
            summary,
            text="Total Expenses: 0 TSh",
            font=("Arial", 17, "bold")
        )

        self.total_label.pack(
            pady=12
        )

        # =========================
        # HISTORY
        # =========================

        history_title = ctk.CTkLabel(
            self,
            text="EXPENSE HISTORY",
            font=("Arial", 20, "bold")
        )

        history_title.pack(
            anchor="w",
            padx=25,
            pady=(15, 8)
        )

        self.list_frame = ctk.CTkScrollableFrame(
            self
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

    # =========================
    # ADD EXPENSE
    # =========================

    def add_expense(self):

        category = self.category_entry.get().strip()
        description = self.description_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        expense_date = self.date_entry.get().strip()

        if not category:

            messagebox.showwarning(
                "Category Required",
                "Please enter an expense category."
            )
            return

        try:

            amount = float(amount_text)

            if amount <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter an amount greater than zero."
            )
            return

        if not expense_date:

            messagebox.showwarning(
                "Date Required",
                "Please enter the expense date."
            )
            return

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO expenses
                (
                    category,
                    description,
                    amount,
                    expense_date,
                    user_id
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                category,
                description or None,
                amount,
                expense_date,
                self.current_user["id"]
                if self.current_user
                else None
            ))

            connection.commit()

            messagebox.showinfo(
                "Expense Recorded",
                f"{amount:,.0f} TSh expense recorded successfully."
            )

            self.category_entry.delete(
                0,
                "end"
            )

            self.description_entry.delete(
                0,
                "end"
            )

            self.amount_entry.delete(
                0,
                "end"
            )

            self.load_expenses()

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:

            connection.close()

    # =========================
    # LOAD EXPENSES
    # =========================

    def load_expenses(self):

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                expenses.id,
                expenses.category,
                expenses.description,
                expenses.amount,
                expenses.expense_date,
                users.full_name AS worker

            FROM expenses

            LEFT JOIN users
                ON expenses.user_id = users.id

            ORDER BY expenses.id DESC

            LIMIT 100
        """)

        expenses = cursor.fetchall()

        # Total expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM expenses
        """)

        total = cursor.fetchone()["total"]

        connection.close()

        self.total_label.configure(
            text=f"Total Expenses: {total:,.0f} TSh"
        )

        headers = [
            "Category",
            "Description",
            "Amount",
            "Date",
            "Entered By"
        ]

        for column, header in enumerate(headers):

            label = ctk.CTkLabel(
                self.list_frame,
                text=header,
                font=("Arial", 14, "bold")
            )

            label.grid(
                row=0,
                column=column,
                padx=12,
                pady=10,
                sticky="w"
            )

        for row_index, expense in enumerate(
            expenses,
            start=1
        ):

            values = [
                expense["category"],
                expense["description"] or "-",
                f"{expense['amount']:,.0f} TSh",
                expense["expense_date"],
                expense["worker"] or "Unknown"
            ]

            for column, value in enumerate(values):

                label = ctk.CTkLabel(
                    self.list_frame,
                    text=value
                )

                label.grid(
                    row=row_index,
                    column=column,
                    padx=12,
                    pady=7,
                    sticky="w"
                )