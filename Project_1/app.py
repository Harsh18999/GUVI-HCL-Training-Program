import streamlit as st
import pandas as pd
import random
import plotly.express as px


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Inventory Management System",
    page_icon=":package:",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CONSTANTS AND SAMPLE DATA

CATEGORIES = ['Electronics', 'Clothing', 'Grocery', 'Stationery', 'Sports']
PRODUCT_NAMES = [
    'Phone', 'T-Shirt', 'Bread', 'Notebook', 'Football',
    'Laptop', 'Jeans', 'Milk', 'Pen', 'Tennis Ball',
    'Tablet', 'Jacket', 'Eggs', 'Marker', 'Cricket Bat',
    'Headphones', 'Shoes', 'Butter', 'Stapler', 'Basketball'
]


# DATA MANAGEMENT FUNCTIONS

def generate_sample_data(num_items=20):
    """Generate sample inventory data"""
    data = []
    for i in range(1, num_items + 1):
        category = random.choice(CATEGORIES)
        name = f"{random.choice(PRODUCT_NAMES)}-{random.randint(100, 999)}"
        quantity = random.randint(0, 100)
        reorder_level = random.randint(5, 30)
        
        data.append({
            'ProductID': f"P{i:03d}",
            'Name': name,
            'Category': category,
            'QuantityAvailable': quantity,
            'ReorderLevel': reorder_level,
            'Status': 'Low Stock' if quantity <= reorder_level else 'In Stock'
        })
    return data

def initialize_data():
    """Initialize or load inventory data"""
    if 'data' not in st.session_state:
        st.session_state.data = generate_sample_data()
    if 'next_id' not in st.session_state:
        st.session_state.next_id = len(st.session_state.data) + 1


# SIDEBAR - PRODUCT MANAGEMENT

def render_sidebar():
    """Render the sidebar for product management"""
    with st.sidebar:
        st.header("📦 Product Management")
        
        # Add new product form
        with st.expander("➕ Add New Product", expanded=True):
            with st.form("add_product_form"):
                # Auto-generate product ID
                product_id = st.text_input(
                    "Product ID",
                    value=f"P{st.session_state.next_id:03d}",
                    disabled=True
                )
                
                name = st.text_input("Product Name", placeholder="Enter product name")
                category = st.selectbox("Category", CATEGORIES)
                quantity_available = st.number_input(
                    "Quantity Available",
                    min_value=0,
                    value=10,
                    step=1
                )
                reorder_level = st.number_input(
                    "Reorder Level",
                    min_value=0,
                    value=5,
                    step=1,
                    help="Minimum quantity before reordering is needed"
                )
                
                submitted = st.form_submit_button("Add Product")
                if submitted:
                    add_product(product_id, name, category, quantity_available, reorder_level)

        # Data management options
        with st.expander("⚙️ Data Options"):
            if st.button("🔄 Generate Sample Data"):
                st.session_state.data = generate_sample_data()
                st.session_state.next_id = len(st.session_state.data) + 1
                st.rerun()
                
            if st.button("🗑️ Clear All Data"):
                st.session_state.data = []
                st.session_state.next_id = 1
                st.rerun()

def add_product(product_id, name, category, quantity, reorder_level):
    """Add a new product to inventory"""
    if not name:
        st.error("Please enter a product name")
        return
        
    new_product = {
        'ProductID': product_id,
        'Name': name,
        'Category': category,
        'QuantityAvailable': quantity,
        'ReorderLevel': reorder_level,
        'Status': 'Low Stock' if quantity <= reorder_level else 'In Stock'
    }
    
    st.session_state.data.append(new_product)
    st.session_state.next_id += 1
    st.success(f"Product '{name}' added successfully!")
    st.rerun()


# MAIN DASHBOARD

def render_dashboard():
    """Render the main dashboard"""
    st.title("📦 Inventory Management Dashboard")
    st.markdown("---")
    
    # Convert data to DataFrame
    df = pd.DataFrame(st.session_state.data)
    
    if df.empty:
        st.warning("No inventory data available. Please add products or generate sample data.")
        return
    
    # Summary cards
    render_summary_cards(df)
    
    # Main content columns
    col1, col2 = st.columns([2, 3])
    
    with col1:
        render_inventory_table(df)
        
    with col2:
        render_category_charts(df)
    


def render_summary_cards(df):
    """Render summary KPI cards"""
    total_items = len(df)
    total_quantity = df['QuantityAvailable'].sum()
    low_stock_count = len(df[df['QuantityAvailable'] <= df['ReorderLevel']])
    categories_count = df['Category'].nunique()
    
    cols = st.columns(4)
    cols[0].metric("Total Products", total_items)
    cols[1].metric("Total Quantity", total_quantity)
    cols[2].metric("Low Stock Items", low_stock_count, delta_color="inverse")
    cols[3].metric("Categories", categories_count)

def render_inventory_table(df):
    """Render the inventory table with filters"""
    with st.container():
        st.subheader("📋 Inventory Overview")
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                options=df['Category'].unique(),
                default=df['Category'].unique()
            )
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=['In Stock', 'Low Stock'],
                default=['In Stock', 'Low Stock']
            )
        
        # Apply filters
        filtered_df = df[
            (df['Category'].isin(category_filter)) & 
            (df['Status'].isin(status_filter))
        ]
        
        # Display table with conditional formatting
        st.dataframe(
            filtered_df.style.applymap(
                lambda x: 'color: red' if x == 'Low Stock' else 'color: green',
                subset=['Status']
            ),
            use_container_width=True,
            height=600
        )

def render_category_charts(df):
    """Render category distribution charts"""
    with st.container():
        tab1, tab2, tab3 = st.tabs(["📊 Stock Distribution", "📈 Quantity by Category", "🚨 Low Stock Alerts"])
        
        with tab1:
            st.subheader("Stock Proportion by Category")
            category_proportion = df.groupby('Category')['QuantityAvailable'].sum().reset_index()
            fig = px.pie(
                category_proportion,
                values='QuantityAvailable',
                names='Category',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.subheader("Total Quantity by Category")
            category_counts = df.groupby('Category')['QuantityAvailable'].sum().reset_index()
            fig = px.bar(
                category_counts,
                x='Category',
                y='QuantityAvailable',
                color='Category',
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            render_alerts_section(df)

def render_alerts_section(df):
    """Render low stock alerts section"""
    st.markdown("---")
    st.subheader("🚨 Low Stock Alerts")
    
    low_stock = df[df['Status'] == 'Low Stock']
    
    if not low_stock.empty:
        # Create columns for each low stock item
        cols = st.columns(3)
        for idx, (_, row) in enumerate(low_stock.iterrows()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{row['Name']}** ({row['ProductID']})")
                    st.progress(
                        row['QuantityAvailable'] / row['ReorderLevel'],
                        text=f"{row['QuantityAvailable']}/{row['ReorderLevel']} units remaining"
                    )
                    st.caption(f"Category: {row['Category']}")
    else:
        st.success("🎉 All products are sufficiently stocked!")

# MAIN APP EXECUTION

if __name__ == "__main__":
    initialize_data()
    render_sidebar()
    render_dashboard()
