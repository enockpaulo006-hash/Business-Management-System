import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from database import get_connection


class SalesScreen(ctk.CTkFrame):

    def __init__(self, master, current_user=None):
        super().__init__(master)

        self.current_user = current_user
        self.product_map = {}

        self.build_ui()
        self.load_products()
        self.load_sales()

    # =========================
    # BUILD UI
    # =========================

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="SALES / RECORD SALE",
            font=("Arial", 28, "bold")
        )

        title.pack(
            pady=(20, 5)
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Record products sold and calculate profit automatically",
            font=("Arial", 15)
        )

        subtitle.pack(
            pady=(0, 15)
        )

        # =========================
        # FORM
        # =========================

        form = ctk.CTkFrame(self)

        form.pack(
            fill="x",
            padx=25,
            pady=10
        )

        # Product
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
            width=260,
            values=["Loading..."],
            command=self.product_selected
        )

        self.product_combo.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 12)
        )

        # Stock
        ctk.CTkLabel(
            form,
            text="Available Stock"
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.stock_label = ctk.CTkLabel(
            form,
            text="0",
            font=("Arial", 16, "bold")
        )

        self.stock_label.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 12)
        )

        # Quantity
        ctk.CTkLabel(
            form,
            text="Quantity Sold"
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.quantity_entry = ctk.CTkEntry(
            form,
            width=130,
            placeholder_text="e.g. 2"
        )

        self.quantity_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 12)
        )

        # Selling price
        ctk.CTkLabel(
            form,
            text="Selling Price / Unit (TSh)"
        ).grid(
            row=0,
            column=3,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.selling_price_entry = ctk.CTkEntry(
            form,
            width=180,
            placeholder_text="e.g. 280000"
        )

        self.selling_price_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=(0, 12)
        )

        # Date
        ctk.CTkLabel(
            form,
            text="Sale Date"
        ).grid(
            row=0,
            column=4,
            padx=10,
            pady=(12, 5),
            sticky="w"
        )

        self.date_entry = ctk.CTkEntry(
            form,
            width=140
        )

        self.date_entry.insert(
            0,
            str(date.today())
        )

        self.date_entry.grid(
            row=1,
            column=4,
            padx=10,
            pady=(0, 12)
        )

        # Add sale
        self.add_button = ctk.CTkButton(
            form,
            text="RECORD SALE",
            width=145,
            height=40,
            font=("Arial", 14, "bold"),
            command=self.add_sale
        )

        self.add_button.grid(
            row=1,
            column=5,
            padx=15,
            pady=(0, 12)
        )

        # =========================
        # SUMMARY
        # =========================

        summary = ctk.CTkFrame(self)

        summary.pack(
            fill="x",
            padx=25,
            pady=(10, 5)
        )

        self.revenue_label = ctk.CTkLabel(
            summary,
            text="Revenue: 0 TSh",
            font=("Arial", 15, "bold")
        )

        self.revenue_label.pack(
            side="left",
            padx=25,
            pady=12
        )

        self.cost_label = ctk.CTkLabel(
            summary,
            text="Cost: 0 TSh",
            font=("Arial", 15, "bold")
        )

        self.cost_label.pack(
            side="left",
            padx=25,
            pady=12
        )

        self.profit_label = ctk.CTkLabel(
            summary,
            text="Profit: 0 TSh",
            font=("Arial", 15, "bold")
        )

        self.profit_label.pack(
            side="left",
            padx=25,
            pady=12
        )

        # =========================
        # SALES HISTORY
        # =========================

        history_title = ctk.CTkLabel(
            self,
            text="RECENT SALES",
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
    # LOAD PRODUCTS
    # =========================

    def load_products(self):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                category,
                brand,
                name
            FROM products
            WHERE is_active = 1
            ORDER BY category, brand, name
        """)

        products = cursor.fetchall()

        connection.close()

        self.product_map = {}

        product_names = []

        for product in products:

            if product["brand"]:

                display_name = (
                    f"{product['category']} | "
                    f"{product['brand']} "
                    f"{product['name']}"
                )

            else:

                display_name = (
                    f"{product['category']} | "
                    f"{product['name']}"
                )

            self.product_map[
                display_name
            ] = product["id"]

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

            self.product_selected(
                product_names[0]
            )

        else:

            self.product_combo.configure(
                values=["No products available"]
            )

            self.product_combo.set(
                "No products available"
            )

    # =========================
    # PRODUCT SELECTED
    # =========================

    def product_selected(self, choice):

        if choice not in self.product_map:

            self.stock_label.configure(
                text="0"
            )

            return

        product_id = self.product_map[
            choice
        ]

        stock = self.get_current_stock(
            product_id
        )

        self.stock_label.configure(
            text=f"{stock:g}"
        )

    # =========================
    # CURRENT STOCK
    # =========================

    def get_current_stock(self, product_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM purchases
                        WHERE product_id = ?
                    ),
                    0
                )
                -
                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM sales
                        WHERE product_id = ?
                    ),
                    0
                ) AS stock
        """, (
            product_id,
            product_id
        ))

        result = cursor.fetchone()

        connection.close()

        return result["stock"] or 0

    # =========================
    # GET COST USING FIFO
    # =========================

    def calculate_fifo_cost(
        self,
        product_id,
        quantity
    ):

        connection = get_connection()
        cursor = connection.cursor()

        # Get purchases from oldest to newest
        cursor.execute("""
            SELECT
                id,
                quantity,
                buying_price
            FROM purchases

            WHERE product_id = ?

            ORDER BY purchase_date ASC, id ASC
        """, (
            product_id,
        ))

        purchases = cursor.fetchall()

        # Get previous sales
        cursor.execute("""
            SELECT
                quantity
            FROM sales

            WHERE product_id = ?

            ORDER BY sale_date ASC, id ASC
        """, (
            product_id,
        ))

        sales = cursor.fetchall()

        connection.close()

        # Calculate how many units from previous purchases
        # have already been sold.
        remaining_to_remove = sum(
            sale["quantity"]
            for sale in sales
        )

        total_cost = 0
        remaining_sale_quantity = quantity

        for purchase in purchases:

            purchase_quantity = (
                purchase["quantity"]
            )

            # Skip stock already consumed by previous sales
            if remaining_to_remove >= purchase_quantity:

                remaining_to_remove -= (
                    purchase_quantity
                )

                continue

            available_from_purchase = (
                purchase_quantity
                - remaining_to_remove
            )

            remaining_to_remove = 0

            units_used = min(
                available_from_purchase,
                remaining_sale_quantity
            )

            total_cost += (
                units_used
                * purchase["buying_price"]
            )

            remaining_sale_quantity -= units_used

            if remaining_sale_quantity <= 0:
                break

        return total_cost

    # =========================
    # ADD SALE
    # =========================

    def add_sale(self):

        product_display = (
            self.product_combo.get().strip()
        )

        quantity_text = (
            self.quantity_entry.get().strip()
        )

        selling_price_text = (
            self.selling_price_entry.get().strip()
        )

        sale_date = (
            self.date_entry.get().strip()
        )

        # Product
        if product_display not in self.product_map:

            messagebox.showwarning(
                "Product Required",
                "Please select a valid product."
            )

            return

        product_id = (
            self.product_map[
                product_display
            ]
        )

        # Quantity
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

        # Selling price
        try:

            selling_price = float(
                selling_price_text
            )

            if selling_price < 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Price",
                "Enter a valid selling price."
            )

            return

        # Date
        if not sale_date:

            messagebox.showwarning(
                "Date Required",
                "Please enter the sale date."
            )

            return

        # Stock check
        current_stock = self.get_current_stock(
            product_id
        )

        if quantity > current_stock:

            messagebox.showerror(
                "Insufficient Stock",
                (
                    f"Available stock: "
                    f"{current_stock:g}\n\n"
                    f"You cannot sell "
                    f"{quantity:g} units."
                )
            )

            return

        # Calculate cost before inserting sale
        cost = self.calculate_fifo_cost(
            product_id,
            quantity
        )

        revenue = (
            quantity
            * selling_price
        )

        profit = (
            revenue
            - cost
        )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO sales
                (
                    product_id,
                    quantity,
                    selling_price,
                    cost_price,
                    profit,
                    sale_date,
                    user_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                quantity,
                selling_price,
                cost,
                profit,
                sale_date,
                self.current_user["id"]
                if self.current_user
                else None
            ))

            connection.commit()

            messagebox.showinfo(
                "Sale Recorded",
                (
                    f"Sale recorded successfully.\n\n"
                    f"Revenue: {revenue:,.0f} TSh\n"
                    f"Product Cost: {cost:,.0f} TSh\n"
                    f"Profit: {profit:,.0f} TSh"
                )
            )

            self.quantity_entry.delete(
                0,
                "end"
            )

            self.selling_price_entry.delete(
                0,
                "end"
            )

            self.load_products()
            self.load_sales()

        except Exception as error:

            connection.rollback()

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:

            connection.close()

    # =========================
    # LOAD SALES HISTORY
    # =========================

    def load_sales(self):

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                sales.id,

                products.category,
                products.brand,
                products.name AS product_name,

                sales.quantity,
                sales.selling_price,
                sales.cost_price,
                sales.profit,
                sales.sale_date,

                users.full_name AS worker

            FROM sales

            INNER JOIN products
                ON sales.product_id = products.id

            LEFT JOIN users
                ON sales.user_id = users.id

            ORDER BY sales.id DESC

            LIMIT 100
        """)

        sales = cursor.fetchall()

        connection.close()

        headers = [
            "Category",
            "Product / Model",
            "Qty",
            "Selling Price",
            "Revenue",
            "Cost",
            "Profit",
            "Date",
            "Worker",
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

        for row_index, sale in enumerate(
            sales,
            start=1
        ):

            revenue = (
                sale["quantity"]
                * sale["selling_price"]
            )

            if sale["brand"]:

                product_name = (
                    f"{sale['brand']} "
                    f"{sale['product_name']}"
                )

            else:

                product_name = (
                    sale["product_name"]
                )

            values = [
                sale["category"],
                product_name,
                f"{sale['quantity']:g}",
                f"{sale['selling_price']:,.0f} TSh",
                f"{revenue:,.0f} TSh",
                f"{sale['cost_price']:,.0f} TSh",
                f"{sale['profit']:,.0f} TSh",
                sale["sale_date"],
                sale["worker"] or "Unknown"
            ]

            for column, value in enumerate(values):

                label = ctk.CTkLabel(
                    self.list_frame,
                    text=value
                )

                label.grid(
                    row=row_index,
                    column=column,
                    padx=8,
                    pady=7,
                    sticky="w"
                )

            # =========================
            # UPDATE BUTTON
            # =========================

            update_button = ctk.CTkButton(
                self.list_frame,
                text="UPDATE",
                width=65,
                height=28,
                command=lambda sale_id=sale["id"]:
                    self.update_sale(sale_id)
            )

            update_button.grid(
                row=row_index,
                column=9,
                padx=5,
                pady=7
            )

            # =========================
            # DELETE BUTTON
            # =========================

            delete_button = ctk.CTkButton(
                self.list_frame,
                text="DELETE",
                width=75,
                height=28,
                fg_color="#8B1E1E",
                hover_color="#B22222",
                command=lambda sale_id=sale["id"]:
                    self.delete_sale(sale_id)
            )

            delete_button.grid(
                row=row_index,
                column=10,
                padx=5,
                pady=7
            )
            
    # ==================================================
    # UPDATE SALE
    # ==================================================

    def update_sale(self, sale_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                sales.id,
                sales.product_id,
                sales.quantity,
                sales.selling_price,
                sales.sale_date,
                products.category,
                products.brand,
                products.name AS product_name

            FROM sales

            INNER JOIN products
                ON sales.product_id = products.id

            WHERE sales.id = ?
        """, (sale_id,))

        sale = cursor.fetchone()

        connection.close()

        if not sale:

            messagebox.showerror(
                "Not Found",
                "This sale could not be found."
            )

            return

        # ==================================================
        # CURRENT PRODUCT
        # ==================================================

        if sale["brand"]:

            current_product = (
                f"{sale['category']} | "
                f"{sale['brand']} "
                f"{sale['product_name']}"
            )

        else:

            current_product = (
                f"{sale['category']} | "
                f"{sale['product_name']}"
            )

        # ==================================================
        # UPDATE WINDOW
        # ==================================================

        window = ctk.CTkToplevel(self)

        window.title("Update Sale")
        window.geometry("550x520")

        window.transient(self)
        window.grab_set()

        title = ctk.CTkLabel(
            window,
            text="UPDATE SALE",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(25, 20)
        )

        # ==================================================
        # PRODUCT / MODEL
        # ==================================================

        ctk.CTkLabel(
            window,
            text="Product / Model",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(5, 5)
        )

        product_combo = ctk.CTkComboBox(
            window,
            width=350,
            values=list(self.product_map.keys())
        )

        product_combo.pack(
            pady=5
        )

        product_combo.set(
            current_product
        )

        # ==================================================
        # QUANTITY
        # ==================================================

        ctk.CTkLabel(
            window,
            text="Quantity Sold",
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
            str(sale["quantity"])
        )

        quantity_entry.pack(
            pady=5
        )

        # ==================================================
        # SELLING PRICE
        # ==================================================

        ctk.CTkLabel(
            window,
            text="Selling Price / Unit (TSh)",
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
            str(sale["selling_price"])
        )

        price_entry.pack(
            pady=5
        )

        # ==================================================
        # SALE DATE
        # ==================================================

        ctk.CTkLabel(
            window,
            text="Sale Date",
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
            sale["sale_date"]
        )

        date_entry.pack(
            pady=5
        )

        # ==================================================
        # SAVE UPDATE
        # ==================================================

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

            # ----------------------------------------------
            # QUANTITY
            # ----------------------------------------------

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

            # ----------------------------------------------
            # SELLING PRICE
            # ----------------------------------------------

            try:

                new_selling_price = float(
                    price_entry.get().strip()
                )

                if new_selling_price < 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Invalid Selling Price",
                    "Enter a valid selling price.",
                    parent=window
                )

                return

            # ----------------------------------------------
            # DATE
            # ----------------------------------------------

            new_sale_date = (
                date_entry.get().strip()
            )

            if not new_sale_date:

                messagebox.showerror(
                    "Date Required",
                    "Please enter the sale date.",
                    parent=window
                )

                return

            # ==================================================
            # DATABASE CHECK
            # ==================================================

            connection = get_connection()
            cursor = connection.cursor()

            try:

                # ==============================================
                # AVAILABLE STOCK FOR NEW PRODUCT
                # ==============================================

                cursor.execute("""
                    SELECT
                        COALESCE(
                            (
                                SELECT SUM(quantity)
                                FROM purchases
                                WHERE product_id = ?
                            ),
                            0
                        )
                        -
                        COALESCE(
                            (
                                SELECT SUM(quantity)
                                FROM sales
                                WHERE product_id = ?
                                AND id != ?
                            ),
                            0
                        ) AS stock
                """, (
                    new_product_id,
                    new_product_id,
                    sale_id
                ))

                available_stock = (
                    cursor.fetchone()["stock"]
                    or 0
                )

                # ==============================================
                # CHECK STOCK
                # ==============================================

                if new_quantity > available_stock:

                    connection.close()

                    messagebox.showerror(
                        "Insufficient Stock",
                        (
                            f"Available stock: "
                            f"{available_stock:g}\n\n"
                            f"You cannot sell "
                            f"{new_quantity:g} units."
                        ),
                        parent=window
                    )

                    return

                # ==============================================
                # UPDATE SALE
                # ==============================================

                cursor.execute("""
                    UPDATE sales

                    SET
                        product_id = ?,
                        quantity = ?,
                        selling_price = ?,
                        sale_date = ?

                    WHERE id = ?
                """, (
                    new_product_id,
                    new_quantity,
                    new_selling_price,
                    new_sale_date,
                    sale_id
                ))

                connection.commit()

            except Exception as error:

                connection.rollback()
                connection.close()

                messagebox.showerror(
                    "Update Error",
                    f"Could not update sale.\n\n{error}",
                    parent=window
                )

                return

            connection.close()

            # ==================================================
            # RECALCULATE COST AND PROFIT
            # ==================================================

            new_cost = self.calculate_fifo_cost_for_edit(
                new_product_id,
                new_quantity,
                sale_id
            )

            new_revenue = (
                new_quantity
                * new_selling_price
            )

            new_profit = (
                new_revenue
                - new_cost
            )

            # ==================================================
            # SAVE COST AND PROFIT
            # ==================================================

            connection = get_connection()
            cursor = connection.cursor()

            try:

                cursor.execute("""
                    UPDATE sales

                    SET
                        cost_price = ?,
                        profit = ?

                    WHERE id = ?
                """, (
                    new_cost,
                    new_profit,
                    sale_id
                ))

                connection.commit()

            except Exception as error:

                connection.rollback()
                connection.close()

                messagebox.showerror(
                    "Update Error",
                    f"Could not update profit.\n\n{error}",
                    parent=window
                )

                return

            finally:

                connection.close()

            # ==================================================
            # FINISH
            
            window.destroy()

            messagebox.showinfo(
                "Sale Updated",
                (
                    "Sale updated successfully.\n\n"
                    f"Product: {selected_product}\n"
                    f"Quantity: {new_quantity:g}\n"
                    f"Selling Price: "
                    f"{new_selling_price:,.0f} TSh\n"
                    f"Revenue: "
                    f"{new_revenue:,.0f} TSh\n"
                    f"Cost: "
                    f"{new_cost:,.0f} TSh\n"
                    f"Profit: "
                    f"{new_profit:,.0f} TSh"
                )
            )

            self.load_products()
            self.load_sales()

        # ==================================================
        # UPDATE BUTTON

        update_button = ctk.CTkButton(
            window,
            text="UPDATE SALE",
            width=250,
            height=45,
            command=save_update
        )

        update_button.pack(
            pady=25
        )
        
    # ==================================================
    # FIFO COST FOR EDITED SALE

    def calculate_fifo_cost_for_edit(
        self,
        product_id,
        quantity,
        excluded_sale_id
    ):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                quantity,
                buying_price

            FROM purchases

            WHERE product_id = ?

            ORDER BY purchase_date ASC, id ASC
        """, (
            product_id,
        ))

        purchases = cursor.fetchall()

        cursor.execute("""
            SELECT
                quantity

            FROM sales

            WHERE product_id = ?

            AND id != ?

            ORDER BY sale_date ASC, id ASC
        """, (
            product_id,
            excluded_sale_id
        ))

        previous_sales = cursor.fetchall()

        connection.close()

        remaining_to_remove = sum(
            sale["quantity"]
            for sale in previous_sales
        )

        total_cost = 0

        remaining_quantity = quantity

        for purchase in purchases:

            purchase_quantity = (
                purchase["quantity"]
            )

            if remaining_to_remove >= purchase_quantity:

                remaining_to_remove -= (
                    purchase_quantity
                )

                continue

            available = (
                purchase_quantity
                - remaining_to_remove
            )

            remaining_to_remove = 0

            units_used = min(
                available,
                remaining_quantity
            )

            total_cost += (
                units_used
                * purchase["buying_price"]
            )

            remaining_quantity -= units_used

            if remaining_quantity <= 0:

                break

        return total_cost