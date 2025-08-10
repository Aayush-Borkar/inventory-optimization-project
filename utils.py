import pandas as pd

def preprocess_data(df, date_col, sales_col, product_col=None):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col, sales_col])
    df = df.sort_values(by=date_col)

    if product_col and product_col != "None":
        grouped = df.groupby([date_col, product_col]).agg({sales_col: 'sum'}).reset_index()
    else:
        grouped = df.groupby(date_col).agg({sales_col: 'sum'}).reset_index()
        grouped[product_col] = "All Products"

    grouped.columns = ['Date', 'Units Sold', 'Product']
    return grouped
