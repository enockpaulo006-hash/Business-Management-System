import customtkinter as ctk
from datetime import date

from database import get_connection
from screens.reports import ReportsScreen
from screens.analysis import AnalysisScreen

from screens.login import LoginScreen
from screens.products import ProductsScreen
from screens.purchases import PurchasesScreen
from screens.sales import SalesScreen
from screens.expenses import ExpensesScreen

class ShopManagementSystem(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Gideon Management System")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.current_user = None

        self.show_login()

    # ==================================================
    # LOGIN
    # ==================================================

    def show_login(self):

        for widget in self.winfo_children():
            widget.destroy()

        login_screen = LoginScreen(
            self,
            self.login_successful
        )

        login_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # LOGIN SUCCESSFUL
    # ==================================================

    def login_successful(self, user):

        self.current_user = user

        self.build_main_layout()

        self.show_dashboard()

    # ==================================================
    # MAIN LAYOUT
    # ==================================================

    def build_main_layout(self):

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # =========================
        # SIDEBAR
        # =========================

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Logo
        logo = ctk.CTkLabel(
            self.sidebar,
            text="GIDEON\nMANAGEMENT",
            font=("Arial", 22, "bold")
        )

        logo.pack(
            pady=(30, 40)
        )

        # =========================
        # NAVIGATION
        # =========================

        self.dashboard_button = ctk.CTkButton(
            self.sidebar,
            text="🏠  Dashboard",
            height=45,
            command=self.show_dashboard
        )

        self.dashboard_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.products_button = ctk.CTkButton(
            self.sidebar,
            text="📦  Products",
            height=45,
            command=self.show_products
        )

        self.products_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.purchases_button = ctk.CTkButton(
            self.sidebar,
            text="📥  Purchases",
            height=45,
            command=self.show_purchases
        )

        self.purchases_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.sales_button = ctk.CTkButton(
            self.sidebar,
            text="💰  Sales",
            height=45,
            command=self.show_sales
        )

        self.sales_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.expenses_button = ctk.CTkButton(
            self.sidebar,
            text="💸  Expenses",
            height=45,
            command=self.show_expenses
        )

        self.expenses_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.reports_button = ctk.CTkButton(
            self.sidebar,
            text="📊  Reports",
            height=45,
            command=self.show_reports
        )

        self.reports_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.analysis_button = ctk.CTkButton(
            self.sidebar,
            text="📈  Analysis",
            height=45,
            command=self.show_analysis
        )

        self.analysis_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        # =========================
        # SPACER
        # =========================

        spacer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        spacer.pack(
            fill="both",
            expand=True
        )

        # =========================
        # LOGOUT
        # =========================

        logout_button = ctk.CTkButton(
            self.sidebar,
            text="🚪  Logout",
            height=45,
            command=self.logout
        )

        logout_button.pack(
            fill="x",
            padx=20,
            pady=(5, 25)
        )

        # =========================
        # CONTENT AREA
        # =========================

        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )

        self.content_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

    # ==================================================
    # CLEAR CONTENT
    # ==================================================

    def clear_content(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ==================================================
    # DASHBOARD
    # ==================================================

    def show_dashboard(self):

        self.clear_content()

        today = date.today().isoformat()

        connection = get_connection()
        cursor = connection.cursor()

        # =========================
        # TODAY'S SALES
        # =========================

        cursor.execute("""
            SELECT COALESCE(
                SUM(quantity * selling_price),
                0
            ) AS total
            FROM sales
            WHERE sale_date = ?
        """, (today,))

        today_sales = cursor.fetchone()["total"]

        # =========================
        # TODAY'S GROSS PROFIT
        # =========================

        cursor.execute("""
            SELECT COALESCE(
                SUM(profit),
                0
            ) AS total
            FROM sales
            WHERE sale_date = ?
        """, (today,))

        today_profit = cursor.fetchone()["total"]

        # =========================
        # TODAY'S EXPENSES
        # =========================

        cursor.execute("""
            SELECT COALESCE(
                SUM(amount),
                0
            ) AS total
            FROM expenses
            WHERE expense_date = ?
        """, (today,))

        today_expenses = cursor.fetchone()["total"]

        # =========================
        # NET PROFIT
        # =========================

        today_net_profit = (
            today_profit - today_expenses
        )

        # =========================
        # LOW STOCK PRODUCTS
        # =========================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM products p

            WHERE p.is_active = 1

            AND (
                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM purchases
                        WHERE product_id = p.id
                    ),
                    0
                )

                -

                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM sales
                        WHERE product_id = p.id
                    ),
                    0
                )
            )

            <=

            (
                COALESCE(
                    (
                        SELECT SUM(quantity)
                        FROM purchases
                        WHERE product_id = p.id
                    ),
                    0
                )

                *

                p.reorder_percentage

                / 100
            )

            AND COALESCE(
                (
                    SELECT SUM(quantity)
                    FROM purchases
                    WHERE product_id = p.id
                ),
                0
            ) > 0
        """)

        low_stock = cursor.fetchone()["total"]

        connection.close()

        # =========================
        # TITLE
        # =========================

        title = ctk.CTkLabel(
            self.content_frame,
            text="Dashboard",
            font=("Arial", 32, "bold")
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        welcome = ctk.CTkLabel(
            self.content_frame,
            text=(
                f"Welcome, "
                f"{self.current_user['full_name']}"
            ),
            font=("Arial", 16)
        )

        welcome.pack(
            anchor="w",
            padx=30,
            pady=(0, 25)
        )

        # =========================
        # SUMMARY CARDS
        # =========================

        cards = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        cards.pack(
            fill="x",
            padx=25
        )

        self.create_card(
            cards,
            "TODAY'S SALES",
            f"{today_sales:,.0f} TSh",
            0
        )

        self.create_card(
            cards,
            "GROSS PROFIT",
            f"{today_profit:,.0f} TSh",
            1
        )

        self.create_card(
            cards,
            "EXPENSES",
            f"{today_expenses:,.0f} TSh",
            2
        )

        self.create_card(
            cards,
            "NET PROFIT",
            f"{today_net_profit:,.0f} TSh",
            3
        )

        # =========================
        # LOW STOCK CARD
        # =========================

        second_row = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        second_row.pack(
            fill="x",
            padx=25,
            pady=20
        )

        self.create_card(
            second_row,
            "LOW STOCK PRODUCTS",
            str(low_stock),
            0
        )

        # =========================
        # SUMMARY
        # =========================

        info = ctk.CTkFrame(
            self.content_frame
        )

        info.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 25)
        )

        info_title = ctk.CTkLabel(
            info,
            text="Today's Business Summary",
            font=("Arial", 22, "bold")
        )

        info_title.pack(
            pady=(25, 15)
        )

        summary_text = (
            f"Sales Revenue: {today_sales:,.0f} TSh\n\n"
            f"Gross Profit: {today_profit:,.0f} TSh\n\n"
            f"Expenses: {today_expenses:,.0f} TSh\n\n"
            f"Net Profit: {today_net_profit:,.0f} TSh\n\n"
            f"Low Stock Products: {low_stock}"
        )

        summary = ctk.CTkLabel(
            info,
            text=summary_text,
            font=("Arial", 16),
            justify="left"
        )

        summary.pack(
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
            height=130
        )

        card.grid(
            row=0,
            column=column,
            padx=7,
            sticky="nsew"
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        card.pack_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 13)
        )

        title_label.pack(
            pady=(25, 5)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 24, "bold")
        )

        value_label.pack()

    # ==================================================
    # PRODUCTS
    # ==================================================

    def show_products(self):

        self.clear_content()

        products_screen = ProductsScreen(
            self.content_frame
        )

        products_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # PURCHASES
    # ==================================================

    def show_purchases(self):

        self.clear_content()

        purchases_screen = PurchasesScreen(
            self.content_frame,
            self.current_user
        )

        purchases_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # SALES
    # ==================================================

    def show_sales(self):

        self.clear_content()

        sales_screen = SalesScreen(
            self.content_frame,
            self.current_user
        )

        sales_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # EXPENSES
    # ==================================================

    def show_expenses(self):

        self.clear_content()

        expenses_screen = ExpensesScreen(
            self.content_frame,
            self.current_user
        )

        expenses_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # REPORTS
    # ==================================================

    def show_reports(self):

        self.clear_content()

        reports_screen = ReportsScreen(
            self.content_frame
        )

        reports_screen.pack(
            fill="both",
            expand=True
        ) 

    # ==================================================
    # ANALYSIS
    # ==================================================

    def show_analysis(self):

        self.clear_content()

        analysis_screen = AnalysisScreen(
            self.content_frame,
            self.current_user
        )

        analysis_screen.pack(
            fill="both",
            expand=True
        )

    # ==================================================
    # LOGOUT
    # ==================================================

    def logout(self):

        self.current_user = None

        self.show_login()


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ShopManagementSystem()

    app.mainloop()