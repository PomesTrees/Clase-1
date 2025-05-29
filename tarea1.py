import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Header
st.title("Sales Dashboard")

# Upload file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Main container
    with st.container():
        st.subheader("Data Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Total Sales", f"${df['VENTAS TOTALES'].sum():,.0f}" if 'VENTAS TOTALES' in df.columns else "N/A")
        with col3:
            st.metric("Total Units", f"{df['UNIDADES VENDIDAS'].sum():,.0f}" if 'UNIDADES VENDIDAS' in df.columns else "N/A")
        with col4:
            st.metric("Avg Sale", f"${df['VENTAS TOTALES'].mean():,.0f}" if 'VENTAS TOTALES' in df.columns else "N/A")
    
    # Region Filter Section
    st.divider()
    with st.container():
        st.subheader("Filter by Region")
        
        if 'REGION' in df.columns:
            regions = ['All Regions'] + df['REGION'].unique().tolist()
            selected_region = st.selectbox("Select Region:", regions)
            
            # Filter data based on region
            if selected_region == 'All Regions':
                filtered_df = df.copy()
            else:
                filtered_df = df[df['REGION'] == selected_region]
                
            st.info(f"Showing {len(filtered_df)} records for {selected_region}")
            
            # Display filtered table
            with st.expander("View Data Table", expanded=False):
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.error("REGION column not found in the data")
            filtered_df = df.copy()
    
    # Graphs Section
    st.divider()
    st.subheader("Sales Analytics")
    
    # Check required columns
    required_cols = ['UNIDADES VENDIDAS', 'VENTAS TOTALES', 'NOMBRE', 'APELLIDO']
    available_cols = [col for col in required_cols if col in filtered_df.columns]
    
    if len(available_cols) >= 4:
        # Create salesperson name column
        filtered_df['VENDEDOR'] = filtered_df['NOMBRE'] + ' ' + filtered_df['APELLIDO']
        
        # Create three columns for graphs
        graph_col1, graph_col2, graph_col3 = st.columns(3)
        
        with graph_col1:
            st.write("**Units Sold**")
            units_by_person = filtered_df.groupby('VENDEDOR')['UNIDADES VENDIDAS'].sum().reset_index()
            fig1 = px.bar(units_by_person, x='VENDEDOR', y='UNIDADES VENDIDAS', 
                         title="Units Sold by Salesperson")
            fig1.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with graph_col2:
            st.write("**Total Sales**")
            sales_by_person = filtered_df.groupby('VENDEDOR')['VENTAS TOTALES'].sum().reset_index()
            fig2 = px.bar(sales_by_person, x='VENDEDOR', y='VENTAS TOTALES',
                         title="Total Sales by Salesperson")
            fig2.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)
        
        with graph_col3:
            st.write("**Average Sales**")
            avg_sales_by_person = filtered_df.groupby('VENDEDOR')['VENTAS TOTALES'].mean().reset_index()
            fig3 = px.bar(avg_sales_by_person, x='VENDEDOR', y='VENTAS TOTALES',
                         title="Average Sales by Salesperson")
            fig3.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Required columns (UNIDADES VENDIDAS, VENTAS TOTALES, NOMBRE, APELLIDO) not found in the data")
        missing_cols = [col for col in required_cols if col not in filtered_df.columns]
        st.error(f"Missing columns: {missing_cols}")
    
    # Vendor-specific Data Section (now Salesperson-specific)
    st.divider()
    with st.container():
        st.subheader("Salesperson Analysis")
        
        # Create full name for selection
        if 'NOMBRE' in filtered_df.columns and 'APELLIDO' in filtered_df.columns:
            if 'VENDEDOR' not in filtered_df.columns:
                filtered_df['VENDEDOR'] = filtered_df['NOMBRE'] + ' ' + filtered_df['APELLIDO']
            
            salespersons = filtered_df['VENDEDOR'].unique().tolist()
            selected_person = st.selectbox("Select Salesperson for detailed analysis:", salespersons)
            
            person_data = filtered_df[filtered_df['VENDEDOR'] == selected_person]
            
            # Salesperson metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records", len(person_data))
            with col2:
                if 'VENTAS TOTALES' in person_data.columns:
                    st.metric("Total Sales", f"${person_data['VENTAS TOTALES'].sum():,.0f}")
            with col3:
                if 'UNIDADES VENDIDAS' in person_data.columns:
                    st.metric("Units Sold", f"{person_data['UNIDADES VENDIDAS'].sum():,.0f}")
            with col4:
                if 'SALARIO' in person_data.columns:
                    st.metric("Salary", f"${person_data['SALARIO'].iloc[0]:,.0f}")
            
            # Salesperson data table
            st.write(f"**Data for {selected_person}:**")
            st.dataframe(person_data, use_container_width=True)
            
            # Download button for salesperson data
            csv = person_data.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_person} data as CSV",
                data=csv,
                file_name=f"{selected_person.replace(' ', '_')}_data.csv",
                mime="text/csv"
            )
        else:
            st.error("NOMBRE and APELLIDO columns not found in the data")

else:
    # Welcome message when no file is uploaded
    st.info("Please upload an Excel file to get started")
    st.markdown("""
    **Expected columns in your Excel file:**
    - REGION
    - NOMBRE, APELLIDO (for salesperson names)
    - UNIDADES VENDIDAS
    - VENTAS TOTALES
    - SALARIO
    """)