import customtkinter as ctk
from tkinter import messagebox
from database import get_connection


class ProductsScreen(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.selected_product_id = None

        self.build_ui()

        self.archive_button.configure(
            state="disabled"
        )

        self.load_products()

    def build_ui(self):

        # =========================
        # TITLE
        # =========================

        title = ctk.CTkLabel(
            self,
            text="PRODUCT MANAGEMENT",
            font=("Arial", 28, "bold")
        )

        title.pack(
            pady=(25, 10)
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Add, edit, search and manage shop products",
            font=("Arial", 15)
        )

        subtitle.pack(
            pady=(0, 20)
        )

        # =========================
        # FORM
        # =========================

        form = ctk.CTkFrame(
            self
        )

        form.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # =========================
        # PRODUCT NAME
        # =========================

        ctk.CTkLabel(
            form,
            text="Product Name"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        self.name_entry = ctk.CTkEntry(
            form,
            width=220,
            placeholder_text="e.g. Phone"
        )

        self.name_entry.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # UNIT
        # =========================

        ctk.CTkLabel(
            form,
            text="Unit"
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        self.unit_entry = ctk.CTkEntry(
            form,
            width=180,
            placeholder_text="e.g. piece"
        )

        self.unit_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # REORDER PERCENTAGE
        # =========================

        ctk.CTkLabel(
            form,
            text="Low Stock %"
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        self.reorder_entry = ctk.CTkEntry(
            form,
            width=150,
            placeholder_text="25"
        )

        self.reorder_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # ADD PRODUCT
        # =========================

        self.add_button = ctk.CTkButton(
            form,
            text="ADD PRODUCT",
            width=150,
            command=self.add_product
        )

        self.add_button.grid(
            row=1,
            column=3,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # UPDATE
        # =========================

        self.update_button = ctk.CTkButton(
            form,
            text="UPDATE",
            width=120,
            command=self.update_product
        )

        self.update_button.grid(
            row=1,
            column=4,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # CLEAR
        # =========================

        self.clear_button = ctk.CTkButton(
            form,
            text="CLEAR",
            width=100,
            command=self.clear_form
        )

        self.clear_button.grid(
            row=1,
            column=5,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # ARCHIVE
        # =========================

        self.archive_button = ctk.CTkButton(
            form,
            text="ARCHIVE",
            width=120,
            fg_color="#C62828",
            hover_color="#8E0000",
            command=self.archive_product
        )

        self.archive_button.grid(
            row=1,
            column=6,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # SEARCH
        # =========================

        search_frame = ctk.CTkFrame(
            self
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search:"
        ).pack(
            side="left",
            padx=(15, 5),
            pady=10
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search product..."
        )

        self.search_entry.pack(
            side="left",
            padx=5,
            pady=10
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.load_products()
        )

        # =========================
        # PRODUCTS LIST
        # =========================

        self.list_frame = ctk.CTkScrollableFrame(
            self
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )
            # ==================================================
    # LOAD PRODUCTS
    # ==================================================

    def load_products(self):

        for widget in self.list_frame.winfo_children():

            widget.destroy()

        search_text = (
            self.search_entry.get().strip()
        )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                p.id,
                p.name,
                p.unit,
                p.reorder_percentage,

                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM purchases
                        WHERE product_id = p.id
                    ),
                    0
                ) AS purchased,

                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM sales
                        WHERE product_id = p.id
                    ),
                    0
                ) AS sold

            FROM products p

            WHERE p.is_active = 1

            AND p.name LIKE ?

            ORDER BY p.name
        """, (
            f"%{search_text}%",
        ))

        products = cursor.fetchall()

        connection.close()

        # =========================
        # TABLE HEADERS
        # =========================

        headers = [
            "Product",
            "Unit",
            "Purchased",
            "Sold",
            "Current Stock",
            "Low Stock",
            "Action"
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
                padx=10,
                pady=10,
                sticky="w"
            )

        # =========================
        # PRODUCT ROWS
        # =========================

        for row_index, product in enumerate(
            products,
            start=1
        ):

            purchased = (
                product["purchased"]
            )

            sold = (
                product["sold"]
            )

            current_stock = (
                purchased - sold
            )

            threshold = (
                purchased
                * (
                    product["reorder_percentage"]
                    / 100
                )
            )

            values = [
                product["name"],
                product["unit"],
                f"{purchased:g}",
                f"{sold:g}",
                f"{current_stock:g}",
                f"{threshold:g}"
            ]

            for column, value in enumerate(
                values
            ):

                label = ctk.CTkLabel(
                    self.list_frame,
                    text=value
                )

                label.grid(
                    row=row_index,
                    column=column,
                    padx=10,
                    pady=8,
                    sticky="w"
                )

            # =========================
            # SELECT BUTTON
            # =========================

            select_button = ctk.CTkButton(
                self.list_frame,
                text="SELECT",
                width=80,
                command=lambda p=product:
                self.select_product(p)
            )

            select_button.grid(
                row=row_index,
                column=6,
                padx=10,
                pady=8
            )

    # ==================================================
    # ADD PRODUCT
    # ==================================================

    def add_product(self):

        name = (
            self.name_entry.get().strip()
        )

        unit = (
            self.unit_entry.get().strip()
        )

        reorder = (
            self.reorder_entry.get().strip()
        )

        # =========================
        # PRODUCT NAME
        # =========================

        if not name:

            messagebox.showwarning(
                "Missing Information",
                "Please enter the product name."
            )

            return

        # =========================
        # DEFAULT UNIT
        # =========================

        if not unit:

            unit = "piece"

        # =========================
        # REORDER PERCENTAGE
        # =========================

        try:

            reorder = (
                float(reorder)
                if reorder
                else 25
            )

            if (
                reorder <= 0
                or reorder > 100
            ):

                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Value",
                "Low Stock % must be between 1 and 100."
            )

            return

        connection = get_connection()
        cursor = connection.cursor()

        # =========================
        # CHECK EXISTING PRODUCT
        # =========================

        cursor.execute("""
            SELECT id
            FROM products

            WHERE LOWER(
                TRIM(name)
            ) = LOWER(
                TRIM(?)
            )

            AND is_active = 1
        """, (
            name,
        ))

        existing_product = (
            cursor.fetchone()
        )

        if existing_product:

            connection.close()

            messagebox.showwarning(
                "Product Already Exists",
                (
                    f'"{name}" is already registered '
                    "in the system.\n\n"
                    "Please use the Purchases menu "
                    "to update its stock."
                )
            )

            return

        # =========================
        # INSERT PRODUCT
        # =========================

        try:

            cursor.execute("""
                INSERT INTO products
                (
                    name,
                    unit,
                    reorder_percentage
                )

                VALUES (?, ?, ?)
            """, (
                name,
                unit,
                reorder
            ))

            connection.commit()

            messagebox.showinfo(
                "Success",
                f"{name} has been added successfully."
            )

            self.clear_form()

            self.load_products()

        except Exception as error:

            connection.rollback()

            if "UNIQUE" in str(error):

                messagebox.showerror(
                    "Product Exists",
                    "A product with this name already exists."
                )

            else:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        finally:

            connection.close()
            
                # ==================================================
    # SELECT PRODUCT
    # ==================================================

    def select_product(self, product):

        self.selected_product_id = (
            product["id"]
        )

        self.name_entry.delete(
            0,
            "end"
        )

        self.name_entry.insert(
            0,
            product["name"]
        )

        self.unit_entry.delete(
            0,
            "end"
        )

        self.unit_entry.insert(
            0,
            product["unit"]
        )

        self.reorder_entry.delete(
            0,
            "end"
        )

        self.reorder_entry.insert(
            0,
            product["reorder_percentage"]
        )

        self.archive_button.configure(
            state="normal"
        )

    # ==================================================
    # UPDATE PRODUCT
    # ==================================================

    def update_product(self):

        if not self.selected_product_id:

            messagebox.showwarning(
                "No Product Selected",
                "Please select a product first."
            )

            return

        name = (
            self.name_entry.get().strip()
        )

        unit = (
            self.unit_entry.get().strip()
        )

        # =========================
        # REORDER PERCENTAGE
        # =========================

        try:

            reorder = float(
                self.reorder_entry.get()
            )

            if (
                reorder <= 0
                or reorder > 100
            ):

                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Value",
                "Low Stock % must be between 1 and 100."
            )

            return

        # =========================
        # NAME
        # =========================

        if not name:

            messagebox.showwarning(
                "Missing Information",
                "Product name is required."
            )

            return

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # =========================
            # CHECK DUPLICATE NAME
            # =========================

            cursor.execute("""
                SELECT id
                FROM products

                WHERE LOWER(
                    TRIM(name)
                ) = LOWER(
                    TRIM(?)
                )

                AND id != ?

                AND is_active = 1
            """, (
                name,
                self.selected_product_id
            ))

            duplicate = (
                cursor.fetchone()
            )

            if duplicate:

                messagebox.showwarning(
                    "Product Already Exists",
                    (
                        f'"{name}" is already used '
                        "by another product."
                    )
                )

                return

            # =========================
            # UPDATE
            # =========================

            cursor.execute("""
                UPDATE products

                SET
                    name = ?,
                    unit = ?,
                    reorder_percentage = ?

                WHERE id = ?
            """, (
                name,
                unit,
                reorder,
                self.selected_product_id
            ))

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Product updated successfully."
            )

            self.clear_form()

            self.load_products()

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:

            connection.close()
            
                
    # ARCHIVE PRODUCT
    # ==================================================

    def archive_product(self):

        if not self.selected_product_id:

            messagebox.showwarning(
                "No Product Selected",
                "Please select a product first."
            )

            return

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # =========================
            # GET PRODUCT
            # =========================

            cursor.execute("""
                SELECT
                    id,
                    name

                FROM products

                WHERE id = ?

                AND is_active = 1
            """, (
                self.selected_product_id,
            ))

            product = cursor.fetchone()

            if not product:

                messagebox.showerror(
                    "Product Not Found",
                    "The selected product could not be found."
                )

                return

            product_name = (
                product["name"]
            )

            # =========================
            # CONFIRM ARCHIVE
            # =========================

            confirm = messagebox.askyesno(
                "Archive Product",
                (
                    f'Are you sure you want to archive '
                    f'"{product_name}"?\n\n'

                    "The product will no longer appear "
                    "in the active Products list or "
                    "Purchases.\n\n"

                    "Its purchase, sales, stock, report "
                    "and analysis history will remain "
                    "preserved."
                )
            )

            if not confirm:

                return

            # =========================
            # ARCHIVE
            # =========================

            cursor.execute("""
                UPDATE products

                SET is_active = 0

                WHERE id = ?
            """, (
                self.selected_product_id,
            ))

            connection.commit()

            messagebox.showinfo(
                "Product Archived",
                (
                    f'"{product_name}" has been '
                    "archived successfully.\n\n"

                    "Its historical records have "
                    "been preserved."
                )
            )

            # =========================
            # CLEAR FORM
            # =========================

            self.clear_form()

            # =========================
            # REFRESH
            # =========================

            self.load_products()

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Archive Error",
                (
                    "The product could not be archived.\n\n"
                    f"{error}"
                )
            )

        finally:

            connection.close()

    # ==================================================
    # CLEAR FORM
    # ==================================================

    def clear_form(self):

        self.selected_product_id = None

        self.name_entry.delete(
            0,
            "end"
        )

        self.unit_entry.delete(
            0,
            "end"
        )

        self.reorder_entry.delete(        pyinstaller --onefile --windowed --icon=app_icon.ico --name="Gideon Management System" main.py        pyinstaller --onefile --windowed --icon=app_icon.ico --name="Gideon Management System" main.py        dist/Gideon Management System.exe
            0,
            "end"
        )

        self.reorder_entry.insert(
            0,
            "25"
        )

        self.archive_button.configure(
            state="disabled"
        )