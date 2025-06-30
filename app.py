import streamlit as st
import sqlite3
import os
import openai
from openai import OpenAI
import os

from database import add_item, get_all_items, get_item_by_id, edit_item, init_db, delete_item, authenticate, create_user



openai.api_key = os.getenv("OPENAI_API_KEY")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = ""

init_db()
st.title( "Inventory Mnagment Application")

tabs = st.tabs(["🔑 Login", "📝 Signup"])


with tabs[0]:
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = username
            st.session_state.page = "dashboard"  
            st.rerun()  
        else:
            st.error("Invalid credentials")

with tabs[1]:
    st.subheader("Create an Account")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    role = st.selectbox("Register as", ["User", "Admin"])

    if st.button("Signup"):
        try:
            create_user(new_username, new_password, role)
            st.success("User created successfully. You can log in now.")
        except sqlite3.IntegrityError:
            st.warning("Username already exists.")


if st.session_state.logged_in:
    role = st.session_state.role
    username = st.session_state.username

    st.write(f"Logged in as: **{username}** ({role})")

    if role == "Admin":
        


        action = st.radio("Choose action", ["Add New", "Edit Existing", "Delete Item", "Search" , " AI Suggestions"])

        if action == "Add New":
            name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0)
            category = st.text_input("Category")
            description = st.text_area("Description")
            status = st.selectbox("Status", ["In Stock", "Low Stock", "Ordered", "Discontinued"])

            if st.button("➕ Add Item"):
                if name:
                    add_item(name, quantity, category, description, status)
                    st.success(f"Added '{name}' successfully.")
                else:
                    st.warning("Item name is required.")


        elif action == "Edit Existing":
            items = get_all_items()
            if not items.empty:
                selected_id = st.selectbox("Select Item to Edit", items["id"])
                item = get_item_by_id(selected_id)

                if item:
                        name = st.text_input("Item Name", item[1])
                        quantity = st.number_input("Quantity", min_value=0, value=item[2])
                        category = st.text_input("Category", item[3])
                        description = st.text_area("Description", item[4])
                        status = st.text_input ("status", item[5])
                        if st.button("✅ Save Changes"):
                            edit_item(selected_id, name, quantity, category, description, status)
                            st.success("Item updated successfully.")

        elif action == "Delete Item":
            items = get_all_items()
            if not items.empty:
                delete_id = st.selectbox("Select Item to Delete", items["id"])
                item = get_item_by_id(delete_id)
                if item:
                    st.write(f"🗂️ **Item:** {item[1]} | Quantity: {item[2]} | Category: {item[3]} | Status: {item[5]}")
                    if st.button("❌ Confirm Delete"):
                        delete_item(delete_id)
                        st.success(f"Item with ID {delete_id} deleted successfully.")
            else:
                st.info("No items to delete.")


        elif action == "Search":
            st.subheader("🔍 Search Items")
            df = get_all_items()

            if df.empty:
                st.info("Inventory is empty.")
            else:
                name_filter = st.text_input("Search by Name")
                category_filter = st.text_input("Search by Category")
                status_filter = st.selectbox("Filter by Status", ["", "In Stock", "Low Stock", "Ordered", "Discontinued"])

                # Apply filters dynamically
                filtered_df = df.copy()

                if name_filter:
                    filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False)]

                if category_filter:
                    filtered_df = filtered_df[filtered_df['category'].str.contains(category_filter, case=False)]

                if status_filter:
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]

                st.write(f"Showing {len(filtered_df)} result(s):")
                st.dataframe(filtered_df, use_container_width=True)

        elif action == " AI Suggestions":
                
            st.subheader("🧠 AI Inventory Suggestions")

            df = get_all_items()
            if df.empty:
                st.info("No inventory data to analyze.")
            else:
                st.dataframe(df)

                if st.button("🤖 Get Suggestions"):
                    try:
                        from openai import OpenAI
                        import os
                        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                        inventory_text = df[['name', 'category', 'quantity', 'status']].to_string(index=False)
                        prompt = f"""You are an AI assistant helping an inventory manager.
        Here is the current inventory:\n{inventory_text}
        Suggest 3 new items to stock (name, category, and reason)."""

                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are an assistant for managing inventory."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=400
                        )

                        suggestions = response.choices[0].message.content
                        st.success("Here are the AI suggestions:")
                        st.write(suggestions)

                    except Exception as e:
                        st.error(f"Error getting suggestions:\n\n{e}")


    elif role=="User":
            st.subheader("🔍 Search Items")
            df = get_all_items()

            if df.empty:
                st.info("Inventory is empty.")
            else:
                name_filter = st.text_input("Search by Name")
                category_filter = st.text_input("Search by Category")
                status_filter = st.selectbox("Filter by Status", ["", "In Stock", "Low Stock", "Ordered", "Discontinued"])

                # Apply filters dynamically
                filtered_df = df.copy()

                if name_filter:
                    filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False)]

                if category_filter:
                    filtered_df = filtered_df[filtered_df['category'].str.contains(category_filter, case=False)]

                if status_filter:
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]

                st.write(f"Showing {len(filtered_df)} result(s):")
                st.dataframe(filtered_df, use_container_width=True)


