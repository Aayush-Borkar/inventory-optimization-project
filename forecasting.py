from prophet import Prophet

def prepare_forecast_input(df):
    return df[['Date', 'Units Sold']].rename(columns={'Date': 'ds', 'Units Sold': 'y'})

def generate_forecast(df, periods=60):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return model, forecast
