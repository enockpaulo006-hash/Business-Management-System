import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from database import get_connection


class PurchasesScreen(ctk.CTkFrame):

    def __init__(self, master, current_user=None):
        super().__init__(master)

        self.current_user = current_user
        self.product_map = {}

        self.build_ui()
        self.load_products()
        self.load_purchases()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="PURCHASES / NEW STOCK",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Record new stock purchased by the shop",
            font=("Arial", 15)
        )
        subtitle.pack(pady=(0, 15))

        form = ctk.CTkFrame(self)
        form.pack(
            fill="x",
            padx=25,
            pady=10
        )

        ctk.CTkLabel(
            form,
            text="Product / Model"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.product_combo = ctk.CTkComboBox(
            form,
            width=250,
            values=["Loading..."],
            command=self.product_selection_changed
        )

        self.product_combo.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            form,
            text="Quantity"
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.quantity_entry = ctk.CTkEntry(
            form,
            width=140,
            placeholder_text="e.g. 8"
        )

        self.quantity_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            form,
            text="Buying Price / Unit (TSh)"
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.buying_price_entry = ctk.CTkEntry(
            form,
            width=190,
            placeholder_text="e.g. 250000"
        )

        self.buying_price_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            form,
            text="Purchase Date"
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

        self.add_button = ctk.CTkButton(
            form,
            text="ADD STOCK",
            width=140,
            height=40,
            font=("Arial", 14, "bold"),
            command=self.add_purchase
        )

        self.add_button.grid(
            row=1,
            column=4,
            padx=15,
            pady=(0, 12)
        )

        summary = ctk.CTkFrame(self)

        summary.pack(
            fill="x",
            padx=25,
            pady=(10, 5)
        )

        self.total_units_label = ctk.CTkLabel(
            summary,
            text="Total Units Purchased: 0",
            font=("Arial", 15, "bold")
        )

        self.total_units_label.pack(
            side="left",
            padx=20,
            pady=12
        )

        self.total_cost_label = ctk.CTkLabel(
            summary,
            text="Total Purchase Cost: 0 TSh",
            font=("Arial", 15, "bold")
        )

        self.total_cost_label.pack(
            side="left",
            padx=20,
            pady=12
        )

        self.transaction_count_label = ctk.CTkLabel(
            summary,
            text="Purchase Transactions: 0",
            font=("Arial", 15, "bold")
        )

        self.transaction_count_label.pack(
            side="left",
            padx=20,
            pady=12
        )

        recent_title = ctk.CTkLabel(
            self,
            text="RECENT PURCHASES",
            font=("Arial", 20, "bold")
        )

        recent_title.pack(
            anchor="w",
            padx=25,
            pady=(20, 10)
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

    def load_products(self):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                category,
                brand,
                name,
                unit
            FROM products
            WHERE is_active = 1
            ORDER BY category, brand, name
        """)

        products = cursor.fetchall()

        connection.close()

        self.product_map = {}

        product_names = []

        for product in products:

            brand = product["brand"]

            if brand:

                display_name = (
                    f"{product['category']} | "
                    f"{brand} {product['name']}"
                )

            else:

                display_name = (
                    f"{product['category']} | "
                    f"{product['name']}"
                )

            self.product_map[display_name] = product["id"]

            product_names.append(
                display_name
            )

        if product_names:

            self.product_combo.configure(
                values=product_names
            )

            self.product_combo.set(
                product_names[0]
            )

            self.product_selection_changed(
                product_names[0]
            )

        else:

            self.product_combo.configure(
                values=["No products available"]
            )

            self.product_combo.set(
                "No products available"
            )

            self.add_button.configure(
                state="disabled",
                text="ADD STOCK"
            )

    def product_selection_changed(
        self,
        selected_product
    ):

        if selected_product not in self.product_map:

            self.add_button.configure(
                state="disabled",
                text="ADD STOCK"
            )

            return

        product_id = (
            self.product_map[selected_product]
        )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT id
                FROM purchases
                WHERE product_id = ?
                LIMIT 1
            """, (
                product_id,
            ))

            existing_purchase = (
                cursor.fetchone()
            )

        finally:

            connection.close()

        if existing_purchase:

            self.add_button.configure(
                state="disabled",
                text="USE UPDATE"
            )

        else:

            self.add_button.configure(
                state="normal",
                text="ADD STOCK"
            )

    def add_purchase(self):

        product_display = (
            self.product_combo.get().strip()
        )

        quantity_text = (
            self.quantity_entry.get().strip()
        )

        price_text = (
            self.buying_price_entry.get().strip()
        )

        purchase_date = (
            self.date_entry.get().strip()
        )

        if product_display not in self.product_map:

            messagebox.showwarning(
                "Product Required",
                "Please select a valid product."
            )

            return

        product_id = (
            self.product_map[product_display]
        )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT id
                FROM purchases
                WHERE product_id = ?
                LIMIT 1
            """, (
                product_id,
            ))

            existing_purchase = (
                cursor.fetchone()
            )

            if existing_purchase:

                messagebox.showwarning(
                    "Product Already Exists",
                    (
                        f"{product_display} already exists "
                        "in purchases.\n\n"
                        "You cannot add it again as new stock.\n\n"
                        "Please use UPDATE on the existing "
                        "purchase record."
                    )
                )

                return

            try:

                quantity = float(
                    quantity_text
                )

                if quantity <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Quantity",
                    "Enter a quantity greater than zero."
                )

                return

            try:

                buying_price = float(
                    price_text
                )

                if buying_price < 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Price",
                    "Enter a valid buying price."
                )

                return

            if not purchase_date:

                messagebox.showwarning(
                    "Date Required",
                    "Please enter the purchase date."
                )

                return

            cursor.execute("""
                INSERT INTO purchases
                (
                    product_id,
                    quantity,
                    buying_price,
                    purchase_date,
                    user_id
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                quantity,
                buying_price,
                purchase_date,
                self.current_user["id"]
                if self.current_user
                else None
            ))

            connection.commit()

            messagebox.showinfo(
                "Stock Added",
                (
                    f"{quantity:g} unit(s) of "
                    f"{product_display} added successfully."
                )
            )

            self.quantity_entry.delete(
                0,
                "end"
            )

            self.buying_price_entry.delete(
                0,
                "end"
            )

            self.load_purchases()

            self.product_selection_changed(
                product_display
            )

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:

            connection.close()

    def load_purchases(self):

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        connection = get_connection()
        cursor = connection.cursor()

        # ==================================================
        # TOTALS
        # ==================================================

        cursor.execute("""
            SELECT
                COALESCE(SUM(quantity), 0) AS total_units,
                COALESCE(
                    SUM(quantity * buying_price),
                    0
                ) AS total_cost,
                COUNT(*) AS transaction_count
            FROM purchases
        """)

        totals = cursor.fetchone()

        total_units = totals["total_units"] or 0
        total_cost = totals["total_cost"] or 0
        transaction_count = totals["transaction_count"] or 0

        self.total_units_label.configure(
            text=f"Total Units Purchased: {total_units:g}"
        )

        self.total_cost_label.configure(
            text=f"Total Purchase Cost: {total_cost:,.0f} TSh"
        )

        self.transaction_count_label.configure(
            text=f"Purchase Transactions: {transaction_count}"
        )

        # ==================================================
        # PURCHASES
        # ==================================================

        cursor.execute("""
            SELECT
                purchases.id,
                products.category,
                products.brand,
                products.name AS product_name,
                purchases.quantity,
                purchases.buying_price,
                purchases.purchase_date,
                users.full_name AS worker

            FROM purchases

            INNER JOIN products
                ON purchases.product_id = products.id

            LEFT JOIN users
                ON purchases.user_id = users.id

            ORDER BY
                purchases.purchase_date DESC,
                purchases.id DESC

            LIMIT 100
        """)

        purchases = cursor.fetchall()

        connection.close()

        # ==================================================
        # TABLE
        # ==================================================

        table = ctk.CTkFrame(
            self.list_frame
        )

        table.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # ==================================================
        # FIXED COLUMN WIDTHS
        # ==================================================

        column_widths = [
            90,    # Category
            210,   # Product
            85,    # Quantity
            130,   # Buying Price
            135,   # Total Cost
            115,   # Date
            165,   # Entered By
            175    # Action
        ]

        for column, width in enumerate(column_widths):

            table.grid_columnconfigure(
                column,
                minsize=width,
                weight=0
            )

        # ==================================================
        # HEADER
        # ==================================================

        headers = [
            "CATEGORY",
            "PRODUCT / MODEL",
            "QUANTITY",
            "BUYING PRICE",
            "TOTAL COST",
            "DATE",
            "ENTERED BY",
            "ACTION"
        ]

        for column, header_text in enumerate(headers):

            header = ctk.CTkLabel(
                table,
                text=header_text,
                font=("Arial", 12, "bold"),
                anchor="w",
                width=column_widths[column]
            )

            header.grid(
                row=0,
                column=column,
                padx=5,
                pady=(8, 10),
                sticky="w"
            )

        # ==================================================
        # NO PURCHASES
        # ==================================================

        if not purchases:

            ctk.CTkLabel(
                table,
                text="No purchases recorded.",
                font=("Arial", 14)
            ).grid(
                row=1,
                column=0,
                columnspan=8,
                pady=30
            )

            return

        # ==================================================
        # PURCHASE ROWS
        # ==================================================

        for row_index, purchase in enumerate(
            purchases,
            start=1
        ):

            # --------------------------------------------------
            # PRODUCT NAME
            # --------------------------------------------------

            if purchase["brand"]:

                product_name = (
                    f"{purchase['brand']} "
                    f"{purchase['product_name']}"
                )

            else:

                product_name = (
                    purchase["product_name"]
                )

            # --------------------------------------------------
            # TOTAL COST
            # --------------------------------------------------

            purchase_total = (
                purchase["quantity"]
                * purchase["buying_price"]
            )

            # --------------------------------------------------
            # WORKER
            # --------------------------------------------------

            worker = (
                purchase["worker"]
                or "System Administrator"
            )

            # ==================================================
            # CATEGORY
            # ==================================================

            ctk.CTkLabel(
                table,
                text=purchase["category"],
                width=column_widths[0],
                anchor="w"
            ).grid(
                row=row_index,
                column=0,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # PRODUCT
            # ==================================================

            ctk.CTkLabel(
                table,
                text=product_name,
                width=column_widths[1],
                anchor="w"
            ).grid(
                row=row_index,
                column=1,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # QUANTITY
            # ==================================================

            ctk.CTkLabel(
                table,
                text=f"{purchase['quantity']:g}",
                width=column_widths[2],
                anchor="w"
            ).grid(
                row=row_index,
                column=2,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # BUYING PRICE
            # ==================================================

            ctk.CTkLabel(
                table,
                text=f"{purchase['buying_price']:,.0f} TSh",
                width=column_widths[3],
                anchor="w"
            ).grid(
                row=row_index,
                column=3,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # TOTAL COST
            # ==================================================

            ctk.CTkLabel(
                table,
                text=f"{purchase_total:,.0f} TSh",
                width=column_widths[4],
                anchor="w"
            ).grid(
                row=row_index,
                column=4,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # DATE
            # ==================================================

            ctk.CTkLabel(
                table,
                text=purchase["purchase_date"],
                width=column_widths[5],
                anchor="w"
            ).grid(
                row=row_index,
                column=5,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # ENTERED BY
            # ==================================================

            ctk.CTkLabel(
                table,
                text=worker,
                width=column_widths[6],
                anchor="w"
            ).grid(
                row=row_index,
                column=6,
                padx=5,
                pady=5,
                sticky="w"
            )

            # ==================================================
            # ACTION FRAME
            # ==================================================

            action_frame = ctk.CTkFrame(
                table,
                fg_color="transparent",
                width=column_widths[7]
            )

            action_frame.grid(
                row=row_index,
                column=7,
                padx=5,
                pady=5,
                sticky="w"
            )

            action_frame.grid_propagate(False)

            # ==================================================
            # UPDATE
            # ==================================================

            update_button = ctk.CTkButton(
                action_frame,
                text="UPDATE",
                width=75,
                height=30,
                command=lambda purchase_id=purchase["id"]:
                    self.update_purchase(
                        purchase_id
                    )
            )

            update_button.pack(
                side="left",
                padx=(0, 5)
            )

            # ==================================================
            # DELETE
            # ==================================================

            delete_button = ctk.CTkButton(
                action_frame,
                text="DELETE",
                width=75,
                height=30,
                fg_color="#B3261E",
                hover_color="#8C1D18",
                command=lambda purchase_id=purchase["id"]:
                    self.delete_purchase(
                        purchase_id
                    )
            )

            delete_button.pack(
                side="left"
            )

    def update_purchase(self, purchase_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                purchases.id,
                purchases.product_id,
                purchases.quantity,
                purchases.buying_price,
                purchases.purchase_date,
                products.category,
                products.brand,
                products.name AS product_name

            FROM purchases

            INNER JOIN products
                ON purchases.product_id = products.id

            WHERE purchases.id = ?
        """, (
            purchase_id,
        ))

        purchase = cursor.fetchone()

        connection.close()

        if not purchase:

            messagebox.showerror(
                "Not Found",
                "This purchase could not be found."
            )

            return

        window = ctk.CTkToplevel(
            self
        )

        window.title(
            "Update Purchase"
        )

        window.geometry(
            "550x650"
        )

        window.transient(
            self.winfo_toplevel()
        )

        window.grab_set()

        ctk.CTkLabel(
            window,
            text="UPDATE PURCHASE",
            font=("Arial", 24, "bold")
        ).pack(
            pady=(25, 15)
        )

        ctk.CTkLabel(
            window,
            text="Product / Model",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(10, 5)
        )

        product_combo = ctk.CTkComboBox(
            window,
            width=350,
            values=list(
                self.product_map.keys()
            )
        )

        product_combo.pack(
            pady=5
        )

        if purchase["brand"]:

            current_product = (
                f"{purchase['category']} | "
                f"{purchase['brand']} "
                f"{purchase['product_name']}"
            )

        else:

            current_product = (
                f"{purchase['category']} | "
                f"{purchase['product_name']}"
            )

        product_combo.set(
            current_product
        )

        ctk.CTkLabel(
            window,
            text="Quantity",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(15, 5)
        )

        quantity_entry = ctk.CTkEntry(
            window,
            width=350
        )

        quantity_entry.insert(
            0,
            str(purchase["quantity"])
        )

        quantity_entry.pack(
            pady=5
        )

        ctk.CTkLabel(
            window,
            text="Buying Price / Unit (TSh)",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(15, 5)
        )

        price_entry = ctk.CTkEntry(
            window,
            width=350
        )

        price_entry.insert(
            0,
            str(purchase["buying_price"])
        )

        price_entry.pack(
            pady=5
        )

        ctk.CTkLabel(
            window,
            text="Purchase Date",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(15, 5)
        )

        date_entry = ctk.CTkEntry(
            window,
            width=350
        )

        date_entry.insert(
            0,
            purchase["purchase_date"]
        )

        date_entry.pack(
            pady=5
        )

        def save_update():

            selected_product = (
                product_combo.get().strip()
            )

            if selected_product not in self.product_map:

                messagebox.showerror(
                    "Invalid Product",
                    "Please select a valid product.",
                    parent=window
                )

                return

            new_product_id = (
                self.product_map[selected_product]
            )

            try:

                new_quantity = float(
                    quantity_entry.get().strip()
                )

                if new_quantity <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Quantity",
                    "Enter a quantity greater than zero.",
                    parent=window
                )

                return

            try:

                new_buying_price = float(
                    price_entry.get().strip()
                )

                if new_buying_price < 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Buying Price",
                    "Enter a valid buying price.",
                    parent=window
                )

                return

            new_purchase_date = (
                date_entry.get().strip()
            )

            if not new_purchase_date:

                messagebox.showerror(
                    "Date Required",
                    "Please enter the purchase date.",
                    parent=window
                )

                return

            connection = get_connection()
            cursor = connection.cursor()

            try:

                cursor.execute("""
                    SELECT COALESCE(
                        SUM(quantity),
                        0
                    ) AS sold

                    FROM sales

                    WHERE product_id = ?
                """, (
                    purchase["product_id"],
                ))

                total_sold = (
                    cursor.fetchone()["sold"]
                    or 0
                )

                cursor.execute("""
                    SELECT COALESCE(
                        SUM(quantity),
                        0
                    ) AS other_purchases

                    FROM purchases

                    WHERE product_id = ?

                    AND id != ?
                """, (
                    purchase["product_id"],
                    purchase_id
                ))

                other_purchases = (
                    cursor.fetchone()["other_purchases"]
                    or 0
                )

                if (
                    new_product_id
                    != purchase["product_id"]
                ):

                    remaining_old_stock = (
                        other_purchases
                        - total_sold
                    )

                    if remaining_old_stock < 0:

                        connection.close()

                        messagebox.showerror(
                            "Cannot Update",
                            (
                                "This purchase cannot be moved "
                                "to another product because the "
                                "original product has already had "
                                "more sales than its remaining stock."
                            ),
                            parent=window
                        )

                        return

                    cursor.execute("""
                        SELECT id
                        FROM purchases
                        WHERE product_id = ?
                        AND id != ?
                        LIMIT 1
                    """, (
                        new_product_id,
                        purchase_id
                    ))

                    duplicate_target = (
                        cursor.fetchone()
                    )

                    if duplicate_target:

                        connection.close()

                        messagebox.showerror(
                            "Product Already Exists",
                            (
                                "The selected product already "
                                "has a purchase record.\n\n"
                                "A product can only have one "
                                "purchase record."
                            ),
                            parent=window
                        )

                        return

                else:

                    resulting_stock = (
                        other_purchases
                        + new_quantity
                        - total_sold
                    )

                    if resulting_stock < 0:

                        connection.close()

                        messagebox.showerror(
                            "Invalid Quantity",
                            (
                                "This quantity would create "
                                "negative stock.\n\n"
                                f"Other purchases: "
                                f"{other_purchases:g}\n"
                                f"Total sold: "
                                f"{total_sold:g}\n"
                                f"New quantity: "
                                f"{new_quantity:g}"
                            ),
                            parent=window
                        )

                        return

                cursor.execute("""
                    UPDATE purchases

                    SET
                        product_id = ?,
                        quantity = ?,
                        buying_price = ?,
                        purchase_date = ?

                    WHERE id = ?
                """, (
                    new_product_id,
                    new_quantity,
                    new_buying_price,
                    new_purchase_date,
                    purchase_id
                ))

                connection.commit()

            except Exception as error:

                connection.rollback()
                connection.close()

                messagebox.showerror(
                    "Update Error",
                    f"Could not update purchase.\n\n{error}",
                    parent=window
                )

                return

            connection.close()

            window.destroy()

            messagebox.showinfo(
                "Purchase Updated",
                (
                    "Purchase updated successfully.\n\n"
                    f"Product: {selected_product}\n"
                    f"Quantity: {new_quantity:g}\n"
                    f"Buying Price: "
                    f"{new_buying_price:,.0f} TSh\n"
                    f"Purchase Date: {new_purchase_date}"
                )
            )

            self.load_products()
            self.load_purchases()

        update_button = ctk.CTkButton(
            window,
            text="UPDATE PURCHASE",
            width=250,
            height=45,
            command=save_update
        )

        update_button.pack(
            pady=25
        )

    def delete_purchase(self, purchase_id):

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # ==================================================
            # GET THE PURCHASE
            # ==================================================

            cursor.execute("""
                SELECT
                    purchases.id,
                    purchases.product_id,
                    purchases.quantity,
                    purchases.buying_price,
                    purchases.purchase_date,
                    products.brand,
                    products.name AS product_name

                FROM purchases

                INNER JOIN products
                    ON purchases.product_id = products.id

                WHERE purchases.id = ?
            """, (
                purchase_id,
            ))

            purchase = cursor.fetchone()

            if not purchase:

                connection.close()

                messagebox.showerror(
                    "Not Found",
                    "This purchase could not be found."
                )

                return

            product_id = purchase["product_id"]

            # ==================================================
            # GET TOTAL PURCHASES EXCLUDING THIS RECORD
            # ==================================================

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS remaining_purchases

                FROM purchases

                WHERE product_id = ?

                AND id != ?
            """, (
                product_id,
                purchase_id
            ))

            result = cursor.fetchone()

            remaining_purchases = (
                result["remaining_purchases"]
                or 0
            )

            # ==================================================
            # GET TOTAL SOLD
            # ==================================================

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS total_sold

                FROM sales

                WHERE product_id = ?
            """, (
                product_id,
            ))

            result = cursor.fetchone()

            total_sold = (
                result["total_sold"]
                or 0
            )

            # ==================================================
            # CHECK STOCK AFTER DELETION
            # ==================================================

            stock_after_delete = (
                remaining_purchases
                - total_sold
            )

            if stock_after_delete < 0:

                connection.close()

                messagebox.showwarning(
                    "Cannot Delete Purchase",
                    (
                        "This purchase cannot be deleted "
                        "because it is required to support "
                        "the recorded sales.\n\n"
                        f"Purchases remaining after deletion: "
                        f"{remaining_purchases:g}\n"
                        f"Units already sold: "
                        f"{total_sold:g}\n\n"
                        "Deleting it would create negative stock."
                    )
                )

                return

            # ==================================================
            # PRODUCT NAME
            # ==================================================

            if purchase["brand"]:

                product_name = (
                    f"{purchase['brand']} "
                    f"{purchase['product_name']}"
                )

            else:

                product_name = (
                    purchase["product_name"]
                )

            total_cost = (
                purchase["quantity"]
                * purchase["buying_price"]
            )

            # ==================================================
            # CONFIRM DELETE
            # ==================================================

            confirm = messagebox.askyesno(
                "Confirm Delete",
                (
                    "Are you sure you want to delete "
                    "this purchase?\n\n"
                    f"Product: {product_name}\n"
                    f"Quantity: {purchase['quantity']:g}\n"
                    f"Buying Price: "
                    f"{purchase['buying_price']:,.0f} TSh\n"
                    f"Total Cost: "
                    f"{total_cost:,.0f} TSh\n"
                    f"Date: {purchase['purchase_date']}\n\n"
                    "This action cannot be undone."
                )
            )

            if not confirm:

                connection.close()

                return

            # ==================================================
            # DELETE

            cursor.execute("""
                DELETE FROM purchases
                WHERE id = ?
            """, (
                purchase_id,
            ))

            connection.commit()

            connection.close()

            messagebox.showinfo(
                "Purchase Deleted",
                (
                    f"{product_name} purchase deleted "
                    "successfully."
                )
            )

            # ==================================================
            # REFRESH

            self.load_products()
            self.load_purchases()

        except Exception as error:

            connection.rollback()
            connection.close()

            messagebox.showerror(
                "Delete Error",
                (
                    "Could not delete the purchase.\n\n"
                    f"{error}"
                )
            )