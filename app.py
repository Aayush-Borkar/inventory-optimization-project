import streamlit as st
import pandas as pd
from forecasting import prepare_forecast_input, generate_forecast
from inventory import eoq, reorder_point, safety_stock
from utils import preprocess_data
from io import BytesIO
from fpdf import FPDF

st.set_page_config(layout="wide")
st.title("📊 Sales Forecast and Inventory Optimizer")

uploaded_file = st.file_uploader("Upload your sales dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Preview of Uploaded Data")
    st.dataframe(df.head(15))

    st.markdown("### 🏷️ Select Relevant Columns")
    date_col = st.selectbox("Select Date Column", df.columns)
    sales_col = st.selectbox("Select Sales Column (Units Sold)", df.columns)
    product_col = st.selectbox("Select Product Column (Optional)", ["None"] + list(df.columns))

    processed_df = preprocess_data(df, date_col, sales_col, product_col)
    selected_product = st.selectbox("Select Product for Forecasting", processed_df['Product'].unique())
    product_df = processed_df[processed_df['Product'] == selected_product]

    # Forecasting
    forecast_df = prepare_forecast_input(product_df)
    model, forecast = generate_forecast(forecast_df)
    future = forecast[-30:]

    st.subheader("📈 Sales Forecast (Next 60 Days)")
    st.line_chart(forecast[['ds', 'yhat']].set_index('ds'))

    # Inventory Inputs
    st.sidebar.subheader("📦 Inventory Settings")
    lead_time = st.sidebar.slider("Lead Time (days)", 1, 30, 7)
    ordering_cost = st.sidebar.number_input("Ordering Cost", value=100.0)
    holding_cost = st.sidebar.number_input("Holding Cost", value=5.0)

    # Inventory Calculation
    total_demand = future['yhat'].sum()
    avg_demand = future['yhat'].mean()
    std_demand = future['yhat'].std()

    st.subheader("⚖️ Inventory Recommendations")
    st.write(f"**EOQ:** {eoq(total_demand, ordering_cost, holding_cost)} units")
    st.write(f"**Reorder Level:** {reorder_point(avg_demand, lead_time)} units")
    st.write(f"**Safety Stock:** {safety_stock(std_demand, lead_time)} units")

    # Export forecast
    st.subheader("📤 Export Forecast Results")
    forecast_export = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
        'ds': 'Date', 'yhat': 'Predicted Sales', 'yhat_lower': 'Lower Bound', 'yhat_upper': 'Upper Bound'
    })

    # Excel
    excel_buffer = BytesIO()
    forecast_export.to_excel(excel_buffer, index=False, engine='openpyxl')
    st.download_button("Download Forecast as Excel", excel_buffer.getvalue(), "forecast_results.xlsx")

    # PDF
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Sales Forecast Report", ln=True, align="C")

    def generate_pdf(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width = pdf.w / 4.5
        row_height = 10

        pdf.cell(col_width, row_height, "Date", border=1)
        pdf.cell(col_width, row_height, "Predicted", border=1)
        pdf.cell(col_width, row_height, "Lower", border=1)
        pdf.cell(col_width, row_height, "Upper", border=1)
        pdf.ln(row_height)

        for i in range(min(30, len(data))):
            row = data.iloc[i]
            pdf.cell(col_width, row_height, str(row['Date']), border=1)
            pdf.cell(col_width, row_height, f"{row['Predicted Sales']:.2f}", border=1)
            pdf.cell(col_width, row_height, f"{row['Lower Bound']:.2f}", border=1)
            pdf.cell(col_width, row_height, f"{row['Upper Bound']:.2f}", border=1)
            pdf.ln(row_height)

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        return pdf_output.getvalue()

    pdf_data = generate_pdf(forecast_export)
    st.download_button("Download Forecast as PDF", pdf_data, "forecast_report.pdf", mime="application/pdf")
