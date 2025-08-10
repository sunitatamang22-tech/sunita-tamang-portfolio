import streamlit as st
import requests
import datetime
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.title("Expense Tracker System")

menu = st.radio("Menu", ["Register", "Login", "Add Expense", "View & Manage Expenses"], horizontal=True)

if menu == "Register":
    st.subheader("Create a New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        response = requests.post(f"{BASE_URL}/users/", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(response.json()["detail"])

elif menu == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simulated login
        st.session_state["user_id"] = 1
        st.success("Logged in successfully")

elif menu == "Add Expense":
    st.subheader("Add a New Expense")
    if "user_id" in st.session_state:
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0)
        category = st.text_input("Category")
        date = st.date_input("Date")
        time = st.time_input("Time")
        if st.button("Add Expense"):
            date_time = datetime.datetime.combine(date, time)
            response = requests.post(
                f"{BASE_URL}/expenses/",
                json={
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "date_time": date_time.isoformat(),
                },
                params={"user_id": st.session_state["user_id"]},
            )
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json()["detail"])
    else:
        st.warning("Please log in first")

elif menu == "View & Manage Expenses":
    st.subheader("Your Expenses")
    if "user_id" in st.session_state:
        response = requests.get(f"{BASE_URL}/expenses/", params={"user_id": st.session_state["user_id"]})
        if response.status_code == 200:
            expenses = response.json()
            if expenses:
                df = pd.DataFrame(expenses)
                st.dataframe(df)
                st.download_button(
                    label="Download as CSV",
                    data=df.to_csv(index=False),
                    file_name="expenses.csv",
                    mime="text/csv",
                )
                
                selected_expense = st.selectbox("Select Expense to Modify or Delete", options=df.index)
                
                if st.button("Delete Expense"):
                    expense_id = df.iloc[selected_expense]["id"]
                    response = requests.delete(f"{BASE_URL}/expenses/{expense_id}")
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error(response.json()["detail"])

                if st.button("Update Expense"):
                    expense_id = df.iloc[selected_expense]["id"]
                    new_description = st.text_input("New Description", df.iloc[selected_expense]["description"])
                    new_amount = st.number_input("New Amount", value=df.iloc[selected_expense]["amount"])
                    new_category = st.text_input("New Category", df.iloc[selected_expense]["category"])
                    if st.button("Confirm Update"):
                        response = requests.put(
                            f"{BASE_URL}/expenses/{expense_id}",
                            json={
                                "description": new_description,
                                "amount": new_amount,
                                "category": new_category,
                                "date_time": df.iloc[selected_expense]["date_time"],
                            },
                        )
                        if response.status_code == 200:
                            st.experimental_rerun()
                            st.success(response.json()["message"])
                        else:
                            st.error(response.json()["detail"])
            else:
                st.info("No expenses found")
        else:
            st.error(response.json()["detail"])
    else:
        st.warning("Please log in first")
