import streamlit as st
import pandas as pd
import numpy as np
import io

# Set page configuration
st.set_page_config(
    page_title="Missing Data Cleaner",
    page_icon="🧹",
    layout="wide"
)

# App title and description
st.title("🧹 Missing Data Cleaner")
st.markdown("""
This tool helps you clean datasets with missing values by identifying and filling them using statistical techniques.
Upload your CSV file, choose a filling method, and download the cleaned dataset.
""")

# Sidebar for file upload and settings
with st.sidebar:
    st.header("📁 Upload & Settings")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Read the dataset
        df = pd.read_csv(uploaded_file)
        
        # Show dataset info
        st.subheader("Dataset Info")
        st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Count missing values
        missing_values = df.isnull().sum()
        st.write("Missing values per column:")
        for col, count in missing_values.items():
            if count > 0:
                st.write(f"- {col}: {count} missing values")
    
    # Filling method selection
    st.subheader("Filling Method")
    fill_method = st.radio(
        "Choose a method to fill missing values:",
        ["Mean", "Median", "Mode"]
    )
    
    # Additional options
    st.subheader("Options")
    exclude_cols = st.checkbox("Exclude non-numeric columns from filling")
    save_option = st.checkbox("Show download option after cleaning", value=True)

# Main content area
if uploaded_file is not None:
    # Display original dataset
    st.header("Original Dataset")
    st.dataframe(df, use_container_width=True)
    
    # Show missing values heatmap
    st.subheader("Missing Values Visualization")
    try:
        import missingno as msno
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        msno.matrix(df, ax=ax)
        st.pyplot(fig)
    except ImportError:
        st.info("Install 'missingno' for missing data visualization: pip install missingno")
    
    # Clean data button
    if st.button("🪄 Clean Data", type="primary"):
        # Create a copy of the dataframe
        cleaned_df = df.copy()
        
        # Determine which columns to process
        if exclude_cols:
            # Only numeric columns
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            cols_to_process = numeric_cols
        else:
            # All columns
            cols_to_process = cleaned_df.columns
        
        # Fill missing values based on selected method
        for col in cols_to_process:
            if cleaned_df[col].isnull().sum() > 0:
                if fill_method == "Mean" and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    filled_value = cleaned_df[col].mean()
                elif fill_method == "Median" and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    filled_value = cleaned_df[col].median()
                elif fill_method == "Mode":
                    filled_value = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else None
                else:
                    filled_value = None
                
                if filled_value is not None:
                    cleaned_df[col].fillna(filled_value, inplace=True)
        
        # Display cleaned dataset
        st.header("Cleaned Dataset")
        st.dataframe(cleaned_df, use_container_width=True)
        
        # Show success message
        remaining_missing = cleaned_df.isnull().sum().sum()
        if remaining_missing == 0:
            st.success("All missing values have been filled!")
        else:
            st.warning(f"There are still {remaining_missing} missing values that couldn't be filled with the selected method.")
        
        # Download option
        if save_option:
            st.subheader("Download Cleaned Data")
            
            # Convert dataframe to CSV
            csv = cleaned_df.to_csv(index=False)
            
            # Create download button
            st.download_button(
                label="Download cleaned CSV",
                data=csv,
                file_name="cleaned_dataset.csv",
                mime="text/csv"
            )
else:
    # Show instructions when no file is uploaded
    st.info("👈 Please upload a CSV file to get started")
    
    # Example dataset
    st.subheader("Example Dataset")
    example_data = {
        'Name': ['Bav1', 'Moena', 'Kumar'],
        'Age': [28, np.nan, 30],
        'Salary': [np.nan, 45000, 50000]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df)
    
    st.markdown("""
    ### How to use this tool:
    1. Upload a CSV file using the sidebar
    2. Review the dataset information and missing values
    3. Select a filling method (mean, median, or mode)
    4. Click the 'Clean Data' button
    5. Download your cleaned dataset
    """)

# Footer
st.markdown("---")
st.markdown("### 📊 Missing Data Cleaner | Built with Streamlit")