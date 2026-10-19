import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta

from database import get_connection


class AnalysisScreen(ctk.CTkFrame):

    def __init__(self, master, current_user=None):

        super().__init__(master)

        self.current_user = current_user

        self.configure(
            fg_color="transparent"
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = ctk.CTkLabel(
            self,
            text="Business Analysis",
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        # ==================================================
        # SUBTITLE
        # ==================================================

        self.subtitle = ctk.CTkLabel(
            self,
            text="Today's business performance and product analysis",
            font=("Arial", 14)
        )

        self.subtitle.pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        # ==================================================
        # ANALYSIS PERIOD
        # ==================================================

        period_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        period_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            period_frame,
            text="Analysis Period:",
            font=("Arial", 13, "bold")
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.period_combo = ctk.CTkComboBox(
            period_frame,
            width=190,
            values=[
                "Today",
                "Yesterday",
                "Specific Date",
                "Last 7 Days",
                "Last 30 Days",
                "Overall / All Time"
            ],
            command=self.period_changed
        )

        self.period_combo.pack(
            side="left",
            padx=(0, 15)
        )

        self.period_combo.set(
            "Today"
        )

        # ==================================================
        # SPECIFIC DATE
        # ==================================================

        self.date_label = ctk.CTkLabel(
            period_frame,
            text="Date:"
        )

        self.date_entry = ctk.CTkEntry(
            period_frame,
            width=130,
            placeholder_text="YYYY-MM-DD"
        )

        self.date_entry.insert(
            0,
            date.today().isoformat()
        )

        self.apply_button = ctk.CTkButton(
            period_frame,
            text="APPLY",
            width=90,
            command=self.load_analysis
        )

        # Hide specific date controls initially
        self.date_label.pack_forget()
        self.date_entry.pack_forget()
        self.apply_button.pack_forget()

        # ==================================================
        # SUMMARY CARDS
        # ==================================================

        self.summary_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.summary_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        for i in range(5):

            self.summary_frame.grid_columnconfigure(
                i,
                weight=1
            )

        self.revenue_card = self.create_card(
            self.summary_frame,
            "SALES REVENUE",
            "0 TSh"
        )

        self.revenue_card.grid(
            row=0,
            column=0,
            padx=5,
            sticky="ew"
        )

        self.profit_card = self.create_card(
            self.summary_frame,
            "GROSS PROFIT",
            "0 TSh"
        )

        self.profit_card.grid(
            row=0,
            column=1,
            padx=5,
            sticky="ew"
        )

        self.expense_card = self.create_card(
            self.summary_frame,
            "EXPENSES",
            "0 TSh"
        )

        self.expense_card.grid(
            row=0,
            column=2,
            padx=5,
            sticky="ew"
        )

        self.net_profit_card = self.create_card(
            self.summary_frame,
            "NET PROFIT",
            "0 TSh"
        )

        self.net_profit_card.grid(
            row=0,
            column=3,
            padx=5,
            sticky="ew"
        )

        self.units_card = self.create_card(
            self.summary_frame,
            "UNITS SOLD",
            "0"
        )

        self.units_card.grid(
            row=0,
            column=4,
            padx=5,
            sticky="ew"
        )
                # ==================================================
        # MAIN CONTENT
        # ==================================================

        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        content_frame.grid_columnconfigure(
            0,
            weight=3
        )

        content_frame.grid_columnconfigure(
            1,
            weight=2
        )

        content_frame.grid_rowconfigure(
            0,
            weight=1
        )

        # ==================================================
        # PRODUCT PERFORMANCE
        # ==================================================

        performance_frame = ctk.CTkFrame(
            content_frame
        )

        performance_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        ctk.CTkLabel(
            performance_frame,
            text="PRODUCT PERFORMANCE",
            font=("Arial", 18, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.products_frame = ctk.CTkScrollableFrame(
            performance_frame
        )

        self.products_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ==================================================
        # STOCK / RECOMMENDATIONS
        # ==================================================

        right_frame = ctk.CTkFrame(
            content_frame
        )

        right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        ctk.CTkLabel(
            right_frame,
            text="CURRENT STOCK & RECOMMENDATIONS",
            font=("Arial", 18, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.recommendations_frame = ctk.CTkScrollableFrame(
            right_frame
        )

        self.recommendations_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ==================================================
        # LOAD DATA
        # ==================================================

        self.load_analysis()
        
            # ==================================================
    # SUMMARY CARD
    # ==================================================

    def create_card(
        self,
        parent,
        title,
        value
    ):

        card = ctk.CTkFrame(
            parent,
            height=110
        )

        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12, "bold")
        ).pack(
            pady=(18, 5)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 20, "bold")
        )

        value_label.pack()

        card.value_label = value_label

        return card

    # ==================================================
    # PERIOD CHANGED
    # ==================================================

    def period_changed(self, value):

        if value == "Specific Date":

            self.date_label.pack(
                side="left",
                padx=(0, 5)
            )

            self.date_entry.pack(
                side="left",
                padx=(0, 10)
            )

            self.apply_button.pack(
                side="left"
            )

        else:

            self.date_label.pack_forget()
            self.date_entry.pack_forget()
            self.apply_button.pack_forget()

            self.load_analysis()

    # ==================================================
    # DATE RANGE
    # ==================================================

    def get_date_range(self):

        today = date.today()

        period = self.period_combo.get()

        # ==================================================
        # TODAY
        # ==================================================

        if period == "Today":

            return (
                today.isoformat(),
                today.isoformat(),
                False
            )

        # ==================================================
        # YESTERDAY
        # ==================================================

        elif period == "Yesterday":

            yesterday = (
                today - timedelta(days=1)
            )

            return (
                yesterday.isoformat(),
                yesterday.isoformat(),
                False
            )

        # ==================================================
        # SPECIFIC DATE
        # ==================================================

        elif period == "Specific Date":

            selected_date = (
                self.date_entry
                .get()
                .strip()
            )

            if not selected_date:

                messagebox.showwarning(
                    "Date Required",
                    "Please enter a date in YYYY-MM-DD format."
                )

                return None, None, False

            try:

                selected = date.fromisoformat(
                    selected_date
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid Date",
                    (
                        "Please enter a valid date.\n\n"
                        "Required format:\n"
                        "YYYY-MM-DD\n\n"
                        "Example:\n"
                        "2026-08-12"
                    )
                )

                return None, None, False

            return (
                selected.isoformat(),
                selected.isoformat(),
                False
            )

        # ==================================================
        # LAST 7 DAYS
        # ==================================================

        elif period == "Last 7 Days":

            start_date = (
                today - timedelta(days=6)
            )

            return (
                start_date.isoformat(),
                today.isoformat(),
                False
            )

        # ==================================================
        # LAST 30 DAYS
        # ==================================================

        elif period == "Last 30 Days":

            start_date = (
                today - timedelta(days=29)
            )

            return (
                start_date.isoformat(),
                today.isoformat(),
                False
            )

        # ==================================================
        # OVERALL / ALL TIME
        # ==================================================

        elif period == "Overall / All Time":

            return (
                None,
                None,
                True
            )

        # ==================================================
        # DEFAULT
        # ==================================================

        return (
            today.isoformat(),
            today.isoformat(),
            False
        )
            # ==================================================
    # LOAD ANALYSIS
    # ==================================================

    def load_analysis(self):

        start_date, end_date, all_time = (
            self.get_date_range()
        )

        # Invalid date
        if (
            start_date is None
            and end_date is None
            and not all_time
        ):

            return

        # ==================================================
        # DISPLAY SELECTED PERIOD
        # ==================================================

        if all_time:

            self.subtitle.configure(
                text="Overall business performance — All Time"
            )

        elif start_date == end_date:

            self.subtitle.configure(
                text=f"Analysis for {start_date}"
            )

        else:

            self.subtitle.configure(
                text=(
                    f"Analysis from {start_date} "
                    f"to {end_date}"
                )
            )

        connection = get_connection()
        cursor = connection.cursor()

        # ==================================================
        # SALES SUMMARY
        # ==================================================

        if all_time:

            cursor.execute("""
                SELECT

                    COALESCE(
                        SUM(
                            quantity * selling_price
                        ),
                        0
                    ) AS revenue,

                    COALESCE(
                        SUM(cost_price),
                        0
                    ) AS cost,

                    COALESCE(
                        SUM(profit),
                        0
                    ) AS profit,

                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS units,

                    COUNT(*) AS transactions

                FROM sales
            """)

        else:

            cursor.execute("""
                SELECT

                    COALESCE(
                        SUM(
                            quantity * selling_price
                        ),
                        0
                    ) AS revenue,

                    COALESCE(
                        SUM(cost_price),
                        0
                    ) AS cost,

                    COALESCE(
                        SUM(profit),
                        0
                    ) AS profit,

                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS units,

                    COUNT(*) AS transactions

                FROM sales

                WHERE date(sale_date)
                BETWEEN date(?) AND date(?)

            """, (
                start_date,
                end_date
            ))

        sales = cursor.fetchone()

        revenue = (
            sales["revenue"] or 0
        )

        gross_profit = (
            sales["profit"] or 0
        )

        units = (
            sales["units"] or 0
        )

        # ==================================================
        # EXPENSES
        # ==================================================

        if all_time:

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS expenses

                FROM expenses
            """)

        else:

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS expenses

                FROM expenses

                WHERE date(expense_date)
                BETWEEN date(?) AND date(?)

            """, (
                start_date,
                end_date
            ))

        expenses = (
            cursor.fetchone()["expenses"]
            or 0
        )

        # ==================================================
        # NET PROFIT
        # ==================================================

        net_profit = (
            gross_profit
            - expenses
        )

        connection.close()

        # ==================================================
        # UPDATE SUMMARY CARDS
        # ==================================================

        self.revenue_card.value_label.configure(
            text=f"{revenue:,.0f} TSh"
        )

        self.profit_card.value_label.configure(
            text=f"{gross_profit:,.0f} TSh"
        )

        self.expense_card.value_label.configure(
            text=f"{expenses:,.0f} TSh"
        )

        self.net_profit_card.value_label.configure(
            text=f"{net_profit:,.0f} TSh"
        )

        self.units_card.value_label.configure(
            text=f"{units:g}"
        )

        # ==================================================
        # PRODUCT PERFORMANCE
        # ==================================================

        self.load_product_performance(
            start_date,
            end_date,
            all_time
        )

        # ==================================================
        # CURRENT STOCK
        # ==================================================

        self.load_recommendations()
        
            # ==================================================
    # PRODUCT PERFORMANCE
    # ==================================================

    def load_product_performance(
        self,
        start_date,
        end_date,
        all_time
    ):

        for widget in (
            self.products_frame.winfo_children()
        ):

            widget.destroy()

        connection = get_connection()
        cursor = connection.cursor()

        if all_time:

            cursor.execute("""
                SELECT

                    products.category,
                    products.brand,
                    products.name,

                    SUM(
                        sales.quantity
                    ) AS units,

                    SUM(
                        sales.quantity
                        * sales.selling_price
                    ) AS revenue,

                    SUM(
                        sales.profit
                    ) AS profit

                FROM sales

                INNER JOIN products
                    ON sales.product_id =
                       products.id

                GROUP BY sales.product_id

                ORDER BY profit DESC
            """)

        else:

            cursor.execute("""
                SELECT

                    products.category,
                    products.brand,
                    products.name,

                    SUM(
                        sales.quantity
                    ) AS units,

                    SUM(
                        sales.quantity
                        * sales.selling_price
                    ) AS revenue,

                    SUM(
                        sales.profit
                    ) AS profit

                FROM sales

                INNER JOIN products
                    ON sales.product_id =
                       products.id

                WHERE date(sales.sale_date)
                BETWEEN date(?) AND date(?)

                GROUP BY sales.product_id

                ORDER BY profit DESC

            """, (
                start_date,
                end_date
            ))

        products = cursor.fetchall()

        connection.close()

        # ==================================================
        # HEADERS
        # ==================================================

        headers = [
            "RANK",
            "PRODUCT",
            "UNITS",
            "REVENUE",
            "PROFIT"
        ]

        header_frame = ctk.CTkFrame(
            self.products_frame
        )

        header_frame.pack(
            fill="x",
            pady=(0, 5)
        )

        for column, header in enumerate(
            headers
        ):

            ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold")
            ).grid(
                row=0,
                column=column,
                padx=8,
                pady=8,
                sticky="w"
            )

        for column in range(5):

            header_frame.grid_columnconfigure(
                column,
                weight=1
            )

        # ==================================================
        # NO SALES
        # ==================================================

        if not products:

            ctk.CTkLabel(
                self.products_frame,
                text="No sales recorded for this period."
            ).pack(
                pady=30
            )

            return

        # ==================================================
        # PRODUCT ROWS
        # ==================================================

        for rank, product in enumerate(
            products,
            start=1
        ):

            if product["brand"]:

                product_name = (
                    f"{product['brand']} "
                    f"{product['name']}"
                )

            else:

                product_name = (
                    product["name"]
                )

            row = ctk.CTkFrame(
                self.products_frame
            )

            row.pack(
                fill="x",
                pady=2
            )

            values = [
                str(rank),
                product_name,
                f"{product['units']:g}",
                f"{product['revenue']:,.0f}",
                f"{product['profit']:,.0f}"
            ]

            for column, value in enumerate(
                values
            ):

                ctk.CTkLabel(
                    row,
                    text=value
                ).grid(
                    row=0,
                    column=column,
                    padx=8,
                    pady=8,
                    sticky="w"
                )

            for column in range(5):

                row.grid_columnconfigure(
                    column,
                    weight=1
                )
                
                    # ==================================================
    # CURRENT STOCK & RECOMMENDATIONS
    # ==================================================

    def load_recommendations(self):

        for widget in (
            self.recommendations_frame.winfo_children()
        ):

            widget.destroy()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT

                products.id,
                products.category,
                products.brand,
                products.name,
                products.reorder_percentage,

                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM purchases
                        WHERE product_id = products.id
                    ),
                    0
                ) AS purchased,

                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM sales
                        WHERE product_id = products.id
                    ),
                    0
                ) AS sold

            FROM products

            WHERE products.is_active = 1

            ORDER BY products.name
        """)

        products = cursor.fetchall()

        connection.close()

        if not products:

            ctk.CTkLabel(
                self.recommendations_frame,
                text="No products registered."
            ).pack(
                pady=30
            )

            return

        # ==================================================
        # PREPARE STOCK DATA
        # ==================================================

        stock_data = []

        for product in products:

            purchased = (
                product["purchased"] or 0
            )

            sold = (
                product["sold"] or 0
            )

            stock = (
                purchased - sold
            )

            if stock < 0:

                stock = 0

            # ==================================================
            # STOCK PERCENTAGE
            # ==================================================

            if purchased > 0:

                percentage = (
                    stock / purchased
                ) * 100

            else:

                percentage = 0

            # ==================================================
            # STATUS
            # ==================================================

            if stock <= 0:

                status = "OUT OF STOCK"
                priority = 1

                border_color = "#E53935"
                title_color = "#FF5252"
                status_color = "#C62828"

                recommendation = (
                    "URGENT: Purchase stock immediately."
                )

            elif percentage <= 25:

                status = "LOW STOCK"
                priority = 2

                border_color = "#FBC02D"
                title_color = "#FFD740"
                status_color = "#F9A825"

                recommendation = (
                    "Consider purchasing more stock soon."
                )

            else:

                status = "SUFFICIENT STOCK"
                priority = 3

                border_color = "#43A047"
                title_color = "#4CAF50"
                status_color = "#2E7D32"

                recommendation = (
                    "Stock level is currently sufficient."
                )

            # ==================================================
            # PRODUCT NAME
            # ==================================================

            if product["brand"]:

                product_name = (
                    f"{product['brand']} "
                    f"{product['name']}"
                )

            else:

                product_name = (
                    product["name"]
                )

            stock_data.append({
                "name": product_name,
                "purchased": purchased,
                "sold": sold,
                "stock": stock,
                "percentage": percentage,
                "status": status,
                "priority": priority,
                "border_color": border_color,
                "title_color": title_color,
                "status_color": status_color,
                "recommendation": recommendation
            })

        # ==================================================
        # MOST URGENT FIRST
        # ==================================================

        stock_data.sort(
            key=lambda item: (
                item["priority"],
                item["percentage"]
            )
        )

        # ==================================================
        # DISPLAY
        # ==================================================

        for item in stock_data:

            card = ctk.CTkFrame(
                self.recommendations_frame,
                border_width=2,
                border_color=item["border_color"]
            )

            card.pack(
                fill="x",
                pady=5,
                padx=3
            )

            # ==================================================
            # PRODUCT NAME
            # ==================================================

            ctk.CTkLabel(
                card,
                text=item["name"],
                font=("Arial", 15, "bold"),
                text_color=item["title_color"]
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 3)
            )

            # ==================================================
            # STOCK INFORMATION
            # ==================================================

            ctk.CTkLabel(
                card,
                text=(
                    f"Stock: {item['stock']:g}  |  "
                    f"Purchased: {item['purchased']:g}  |  "
                    f"Sold: {item['sold']:g}"
                )
            ).pack(
                anchor="w",
                padx=12,
                pady=2
            )

            # ==================================================
            # STOCK LEVEL
            # ==================================================

            ctk.CTkLabel(
                card,
                text=(
                    f"Stock level: "
                    f"{item['percentage']:.1f}%"
                )
            ).pack(
                anchor="w",
                padx=12,
                pady=2
            )

            # ==================================================
            # STATUS
            # ==================================================

            ctk.CTkLabel(
                card,
                text=item["status"],
                font=("Arial", 12, "bold"),
                text_color="white",
                fg_color=item["status_color"],
                corner_radius=8,
                padx=12,
                pady=5
            ).pack(
                anchor="w",
                padx=12,
                pady=(6, 3)
            )

            # ==================================================
            # RECOMMENDATION
          

            ctk.CTkLabel(
                card,
                text=item["recommendation"],
                font=("Arial", 12, "bold")
            ).pack(
                anchor="w",
                padx=12,
                pady=(3, 10)
            )