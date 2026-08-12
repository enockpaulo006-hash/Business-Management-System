import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta

from database import get_connection


class ReportsScreen(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.build_ui()

        # Always open with today's report
        self.generate_report()

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="BUSINESS REPORTS",
            font=("Arial", 28, "bold")
        )

        title.pack(
            pady=(20, 5)
        )

        # ==================================================
        # SUBTITLE
        # ==================================================

        self.subtitle = ctk.CTkLabel(
            self,
            text="Today's business report",
            font=("Arial", 15)
        )

        self.subtitle.pack(
            pady=(0, 15)
        )

        # ==================================================
        # FILTER
        # ==================================================

        filter_frame = ctk.CTkFrame(
            self
        )

        filter_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        ctk.CTkLabel(
            filter_frame,
            text="Report Period",
            font=("Arial", 13, "bold")
        ).pack(
            side="left",
            padx=(15, 8),
            pady=15
        )

        # ==================================================
        # PERIOD SELECTOR
        # ==================================================

        self.period_combo = ctk.CTkComboBox(
            filter_frame,
            width=200,
            values=[
                "Today",
                "Yesterday",
                "Specific Date",
                "Last 7 Days",
                "Last 30 Days",
                "This Month",
                "All Time"
            ],
            command=self.period_changed
        )

        self.period_combo.set(
            "Today"
        )

        self.period_combo.pack(
            side="left",
            padx=8,
            pady=15
        )

        # ==================================================
        # SPECIFIC DATE
        # ==================================================

        self.specific_date_entry = ctk.CTkEntry(
            filter_frame,
            width=130,
            placeholder_text="YYYY-MM-DD"
        )

        self.specific_date_entry.pack(
            side="left",
            padx=8,
            pady=15
        )

        # Hide until Specific Date is selected
        self.specific_date_entry.pack_forget()

        # ==================================================
        # GENERATE BUTTON
        # ==================================================

        generate_button = ctk.CTkButton(
            filter_frame,
            text="GENERATE REPORT",
            width=160,
            command=self.generate_report
        )

        generate_button.pack(
            side="left",
            padx=10,
            pady=15
        )

        # ==================================================
        # REPORT CONTENT
        # ==================================================

        self.report_frame = ctk.CTkScrollableFrame(
            self
        )

        self.report_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )
            # ==================================================
    # PERIOD CHANGED
    # ==================================================

    def period_changed(self, value):

        if value == "Specific Date":

            self.specific_date_entry.pack(
                side="left",
                padx=8,
                pady=15
            )

        else:

            self.specific_date_entry.pack_forget()

    # ==================================================
    # GET DATE RANGE
    # ==================================================

    def get_date_range(self):

        today = date.today()

        period = self.period_combo.get()

        # ==================================================
        # TODAY
        # ==================================================

        if period == "Today":

            start_date = today
            end_date = today

        # ==================================================
        # YESTERDAY
        # ==================================================

        elif period == "Yesterday":

            yesterday = (
                today - timedelta(days=1)
            )

            start_date = yesterday
            end_date = yesterday

        # ==================================================
        # SPECIFIC DATE
        # ==================================================

        elif period == "Specific Date":

            selected_date = (
                self.specific_date_entry
                .get()
                .strip()
            )

            if not selected_date:

                messagebox.showwarning(
                    "Date Required",
                    "Please enter a date in YYYY-MM-DD format."
                )

                return None, None

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

                return None, None

            start_date = selected
            end_date = selected

        # ==================================================
        # LAST 7 DAYS
        # ==================================================

        elif period == "Last 7 Days":

            start_date = (
                today - timedelta(days=6)
            )

            end_date = today

        # ==================================================
        # LAST 30 DAYS
        # ==================================================

        elif period == "Last 30 Days":

            start_date = (
                today - timedelta(days=29)
            )

            end_date = today

        # ==================================================
        # THIS MONTH
        # ==================================================

        elif period == "This Month":

            start_date = today.replace(
                day=1
            )

            end_date = today

        # ==================================================
        # ALL TIME
        # ==================================================

        elif period == "All Time":

            return None, None

        # ==================================================
        # DEFAULT
        # ==================================================

        else:

            start_date = today
            end_date = today

        return (
            start_date.isoformat(),
            end_date.isoformat()
        )
        
            # ==================================================
    # GENERATE REPORT
    # ==================================================

    def generate_report(self):

        # ==================================================
        # CLEAR PREVIOUS REPORT
        # ==================================================

        for widget in (
            self.report_frame.winfo_children()
        ):

            widget.destroy()

        # ==================================================
        # GET DATE RANGE
        # ==================================================

        start_date, end_date = (
            self.get_date_range()
        )

        # Invalid specific date
        if start_date is None and end_date is None:

            if self.period_combo.get() != "All Time":

                return

            all_time = True

        else:

            all_time = False

        # ==================================================
        # DATABASE
        # ==================================================

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
                        SUM(profit),
                        0
                    ) AS gross_profit,

                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS units_sold

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
                        SUM(profit),
                        0
                    ) AS gross_profit,

                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS units_sold

                FROM sales

                WHERE date(sale_date)
                BETWEEN date(?) AND date(?)

            """, (
                start_date,
                end_date
            ))

        sales_summary = cursor.fetchone()

        revenue = (
            sales_summary["revenue"]
            or 0
        )

        gross_profit = (
            sales_summary["gross_profit"]
            or 0
        )

        units_sold = (
            sales_summary["units_sold"]
            or 0
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
                    ) AS total

                FROM expenses
            """)

        else:

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS total

                FROM expenses

                WHERE date(expense_date)
                BETWEEN date(?) AND date(?)

            """, (
                start_date,
                end_date
            ))

        expenses = (
            cursor.fetchone()["total"]
            or 0
        )

        # ==================================================
        # NET PROFIT
        # ==================================================

        net_profit = (
            gross_profit
            - expenses
        )

        # ==================================================
        # TRANSACTION COUNT
        # ==================================================

        if all_time:

            cursor.execute("""
                SELECT
                    COUNT(*) AS total

                FROM sales
            """)

        else:

            cursor.execute("""
                SELECT
                    COUNT(*) AS total

                FROM sales

                WHERE date(sale_date)
                BETWEEN date(?) AND date(?)

            """, (
                start_date,
                end_date
            ))

        transactions = (
            cursor.fetchone()["total"]
        )
        
                # ==================================================
        # PRODUCT PROFITABILITY
        # ==================================================

        if all_time:

            cursor.execute("""
                SELECT

                    products.category,
                    products.brand,
                    products.name,

                    SUM(
                        sales.quantity
                    ) AS quantity_sold,

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
                    ) AS quantity_sold,

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

        product_rows = cursor.fetchall()

        # ==================================================
        # EXPENSE BREAKDOWN
        # ==================================================

        if all_time:

            cursor.execute("""
                SELECT

                    category,
                    SUM(amount) AS total

                FROM expenses

                GROUP BY category

                ORDER BY total DESC
            """)

        else:

            cursor.execute("""
                SELECT

                    category,
                    SUM(amount) AS total

                FROM expenses

                WHERE date(expense_date)
                BETWEEN date(?) AND date(?)

                GROUP BY category

                ORDER BY total DESC

            """, (
                start_date,
                end_date
            ))

        expense_rows = cursor.fetchall()

        connection.close()

        # ==================================================
        # REPORT TITLE
        # ==================================================

        if all_time:

            report_title_text = (
                "REPORT: ALL TIME"
            )

            subtitle_text = (
                "Complete business history"
            )

        elif start_date == end_date:

            report_title_text = (
                f"REPORT: {start_date}"
            )

            subtitle_text = (
                f"Business report for {start_date}"
            )

        else:

            report_title_text = (
                f"REPORT: "
                f"{start_date} → {end_date}"
            )

            subtitle_text = (
                f"Business report from "
                f"{start_date} to {end_date}"
            )

        self.subtitle.configure(
            text=subtitle_text
        )

        report_title = ctk.CTkLabel(
            self.report_frame,
            text=report_title_text,
            font=("Arial", 22, "bold")
        )

        report_title.pack(
            anchor="w",
            pady=(10, 20)
        )
        
                # ==================================================
        # SUMMARY CARDS
        # ==================================================

        cards = ctk.CTkFrame(
            self.report_frame,
            fg_color="transparent"
        )

        cards.pack(
            fill="x",
            pady=5
        )

        self.create_card(
            cards,
            "SALES",
            f"{revenue:,.0f} TSh",
            0
        )

        self.create_card(
            cards,
            "GROSS PROFIT",
            f"{gross_profit:,.0f} TSh",
            1
        )

        self.create_card(
            cards,
            "EXPENSES",
            f"{expenses:,.0f} TSh",
            2
        )

        self.create_card(
            cards,
            "NET PROFIT",
            f"{net_profit:,.0f} TSh",
            3
        )

        # ==================================================
        # ADDITIONAL INFORMATION
        # ==================================================

        info = ctk.CTkLabel(
            self.report_frame,
            text=(
                f"Units Sold: {units_sold:g}    |    "
                f"Sales Transactions: {transactions}"
            ),
            font=("Arial", 15)
        )

        info.pack(
            anchor="w",
            pady=20
        )

        # ==================================================
        # PRODUCT PERFORMANCE
        # ==================================================

        product_title = ctk.CTkLabel(
            self.report_frame,
            text="PRODUCT PROFITABILITY",
            font=("Arial", 20, "bold")
        )

        product_title.pack(
            anchor="w",
            pady=(15, 10)
        )

        if product_rows:

            headers = [
                "Product",
                "Category",
                "Units Sold",
                "Revenue",
                "Profit"
            ]

            table = ctk.CTkFrame(
                self.report_frame
            )

            table.pack(
                fill="x"
            )

            # ==================================================
            # TABLE HEADERS
            # ==================================================

            for column, header in enumerate(
                headers
            ):

                ctk.CTkLabel(
                    table,
                    text=header,
                    font=("Arial", 13, "bold")
                ).grid(
                    row=0,
                    column=column,
                    padx=10,
                    pady=10,
                    sticky="w"
                )

            # ==================================================
            # TABLE ROWS
            # ==================================================

            for row_index, product in enumerate(
                product_rows,
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

                values = [
                    product_name,
                    product["category"],
                    f"{product['quantity_sold']:g}",
                    f"{product['revenue']:,.0f} TSh",
                    f"{product['profit']:,.0f} TSh"
                ]

                for column, value in enumerate(
                    values
                ):

                    ctk.CTkLabel(
                        table,
                        text=value
                    ).grid(
                        row=row_index,
                        column=column,
                        padx=10,
                        pady=7,
                        sticky="w"
                    )

        else:

            ctk.CTkLabel(
                self.report_frame,
                text="No sales recorded for this period."
            ).pack(
                anchor="w",
                pady=10
            )
            
                    # ==================================================
        # EXPENSE BREAKDOWN
        # ==================================================

        expense_title = ctk.CTkLabel(
            self.report_frame,
            text="EXPENSE BREAKDOWN",
            font=("Arial", 20, "bold")
        )

        expense_title.pack(
            anchor="w",
            pady=(30, 10)
        )

        if expense_rows:

            for expense in expense_rows:

                row = ctk.CTkFrame(
                    self.report_frame
                )

                row.pack(
                    fill="x",
                    pady=3
                )

                ctk.CTkLabel(
                    row,
                    text=expense["category"],
                    font=("Arial", 14, "bold")
                ).pack(
                    side="left",
                    padx=15,
                    pady=8
                )

                ctk.CTkLabel(
                    row,
                    text=(
                        f"{expense['total']:,.0f} TSh"
                    )
                ).pack(
                    side="right",
                    padx=15,
                    pady=8
                )

        else:

            ctk.CTkLabel(
                self.report_frame,
                text="No expenses recorded for this period."
            ).pack(
                anchor="w",
                pady=10
            )

    # ==================================================
    # CARD
    # ==================================================

    def create_card(
        self,
        parent,
        title,
        value,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            height=110
        )

        card.grid(
            row=0,
            column=column,
            padx=5,
            sticky="nsew"
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12)
        ).pack(
            pady=(20, 5)
        )

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 19, "bold")
        ).pack()