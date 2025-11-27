import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="💰 Personal Finance Dashboard", layout="wide")

st.title("💰 Personal Finance Dashboard")
st.caption("Upload your bank statements and analyze your expenses visually.")

# -----------------------------
# Helper: Categorize Expenses
# -----------------------------
def auto_categorize(description):
    description = description.lower()

    food_keywords = ["food", "restaurant", "swiggy", "zomato", "meal", "pizza", "burger"]
    travel_keywords = ["uber", "ola", "fuel", "petrol", "train", "bus", "flight"]
    shopping_keywords = ["amazon", "flipkart", "shopping", "mall"]
    bills_keywords = ["electricity", "wifi", "internet", "recharge", "bill", "rent"]
    entertainment_keywords = ["movie", "netflix", "hotstar", "spotify"]

    if any(k in description for k in food_keywords):
        return "Food & Dining"
    elif any(k in description for k in travel_keywords):
        return "Travel"
    elif any(k in description for k in shopping_keywords):
        return "Shopping"
    elif any(k in description for k in bills_keywords):
        return "Bills & Utilities"
    elif any(k in description for k in entertainment_keywords):
        return "Entertainment"
    else:
        return "Others"

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload your bank statement (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully!")

    # Standardize columns
    df.columns = [col.lower() for col in df.columns]

    # Expected column names
    expected_cols = ["date", "description", "amount"]

    # Rename automatically if needed
    for col in df.columns:
        if "desc" in col:
            df.rename(columns={col: "description"}, inplace=True)
        if "amt" in col or "amount" in col:
            df.rename(columns={col: "amount"}, inplace=True)
        if "date" in col:
            df.rename(columns={col: "date"}, inplace=True)

    if not all(col in df.columns for col in expected_cols):
        st.error("Your file must contain Date, Description, and Amount columns.")
        st.stop()

    # Convert types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Auto categorize
    df["category"] = df["description"].apply(auto_categorize)

    # -----------------------------
    # Summary Metrics
    # -----------------------------
    total_expense = df["amount"].sum()
    monthly_expense = df.groupby(df["date"].dt.to_period("M"))["amount"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Expense", f"₹{total_expense:,.2f}")
    col2.metric("Average Monthly Expense", f"₹{monthly_expense.mean():,.2f}")

    # -----------------------------
    # Category-wise Pie Chart
    # -----------------------------
    st.subheader("📊 Category-wise Expense Distribution")

    cat_sum = df.groupby("category")["amount"].sum()

    fig1, ax1 = plt.subplots()
    ax1.pie(cat_sum, labels=cat_sum.index, autopct="%1.1f%%")
    ax1.axis("equal")
    st.pyplot(fig1)

    # -----------------------------
    # Monthly Trend Line Chart
    # -----------------------------
    st.subheader("📈 Monthly Expense Trend")

    fig2, ax2 = plt.subplots()
    monthly_expense.plot(ax=ax2)
    ax2.set_ylabel("Amount (₹)")
    ax2.set_xlabel("Month")
    st.pyplot(fig2)

    # -----------------------------
    # Show Data
    # -----------------------------
    st.subheader("📄 Expense Table")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Upload a CSV or Excel file to begin.")
