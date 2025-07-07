import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, add_category, get_categories, add_expense, get_expenses

# --- Custom CSS for modern look ---
st.markdown('''
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .summary-card {
        background: #fff;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: #c3cfe2;
        color: #333;
        text-align: center;
        padding: 0.5rem 0;
        font-size: 1rem;
        border-top-left-radius: 1rem;
        border-top-right-radius: 1rem;
    }
    </style>
''', unsafe_allow_html=True)

# --- Initialize DB ---
init_db()

# --- Header ---
st.markdown("""
<div style='display: flex; align-items: center; justify-content: center;'>
    <h1 style='color: #2d3a4b; margin-bottom: 0;'>💸 Personal Expense Tracker</h1>
</div>
<p style='text-align:center; color: #4f6272; font-size: 1.2rem;'>Track your spending, analyze your habits, and reach your financial goals!</p>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.image("https://img.icons8.com/color/96/000000/money-bag.png", width=80)
menu = ["🏠 Dashboard", "➕ Add Expense", "📋 View Expenses", "📊 Reports", "🗂️ Manage Categories"]
choice = st.sidebar.radio("Navigation", menu)

# --- Dashboard (Summary) ---
def dashboard():
    st.subheader("Dashboard ✨")
    expenses = get_expenses()
    df = pd.DataFrame(expenses, columns=["ID", "Amount", "Category", "Date", "Description"])
    if not df.empty:
        total = df["Amount"].sum()
        month = pd.to_datetime(df["Date"]).dt.to_period('M').max()
        this_month = df[pd.to_datetime(df["Date"]).dt.to_period('M') == month]["Amount"].sum()
        top_cat = df.groupby("Category")["Amount"].sum().idxmax()
        top_cat_amt = df.groupby("Category")["Amount"].sum().max()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='summary-card'><span style='font-size:2rem;'>💰</span><br><b>Total Spend</b><br><span style='font-size:1.5rem;color:#2d3a4b;'>₹{total:,.2f}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='summary-card'><span style='font-size:2rem;'>📅</span><br><b>This Month</b><br><span style='font-size:1.5rem;color:#2d3a4b;'>₹{this_month:,.2f}</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='summary-card'><span style='font-size:2rem;'>🏆</span><br><b>Top Category</b><br><span style='font-size:1.2rem;color:#2d3a4b;'>{top_cat}</span><br><span style='font-size:1.1rem;'>₹{top_cat_amt:,.2f}</span></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Recent Expenses")
        st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)
    else:
        st.info("No expenses yet. Start by adding your first expense!")

# --- Add Expense ---
def add_expense_page():
    st.subheader("Add a New Expense ➕")
    categories = get_categories()
    if not categories:
        st.warning("Please add a category first in 'Manage Categories'.")
    else:
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", categories, format_func=lambda x: x[1])
        date = st.date_input("Date")
        description = st.text_input("Description")
        if st.button("Add Expense", use_container_width=True):
            add_expense(amount, category[0], str(date), description)
            st.success("Expense added!")

# --- View Expenses ---
def view_expenses_page():
    st.subheader("All Expenses 📋")
    categories = get_categories()
    category_filter = st.selectbox("Filter by Category", [(0, "All")] + categories, format_func=lambda x: x[1])
    if category_filter[0] == 0:
        expenses = get_expenses()
    else:
        expenses = get_expenses(category_filter[0])
    df = pd.DataFrame(expenses, columns=["ID", "Amount", "Category", "Date", "Description"])
    st.dataframe(df, use_container_width=True)

# --- Reports ---
def reports_page():
    st.subheader("Expense Reports 📊")
    expenses = get_expenses()
    df = pd.DataFrame(expenses, columns=["ID", "Amount", "Category", "Date", "Description"])
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        st.markdown("#### Monthly Spend")
        monthly = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().reset_index()
        monthly['Date'] = monthly['Date'].astype(str)
        fig1 = px.bar(monthly, x='Date', y='Amount', color='Amount', color_continuous_scale='Blues', title='Monthly Spend')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("#### Spend by Category")
        cat = df.groupby('Category')['Amount'].sum().reset_index()
        fig2 = px.pie(cat, names='Category', values='Amount', title='Spend by Category', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No expenses to report.")

# --- Manage Categories ---
def manage_categories_page():
    st.subheader("Manage Categories 🗂️")
    new_cat = st.text_input("New Category Name")
    if st.button("Add Category", use_container_width=True):
        if new_cat:
            add_category(new_cat)
            st.success(f"Category '{new_cat}' added!")
    st.markdown("#### Existing Categories")
    cats = get_categories()
    st.write(", ".join([f"<span style='background:#e3eafc;padding:0.3em 0.7em;border-radius:0.7em;margin:0.2em;display:inline-block;'>{c[1]}</span>" for c in cats]), unsafe_allow_html=True)

# --- Page Routing ---
if choice == "🏠 Dashboard":
    dashboard()
elif choice == "➕ Add Expense":
    add_expense_page()
elif choice == "📋 View Expenses":
    view_expenses_page()
elif choice == "📊 Reports":
    reports_page()
elif choice == "🗂️ Manage Categories":
    manage_categories_page()

# --- Footer ---
st.markdown("""
<div class='footer'>
    Made with ❤️ using <b>Streamlit</b> | <a href='https://github.com/' style='color:#2d3a4b;' target='_blank'>Your Name</a>
</div>
""", unsafe_allow_html=True) 