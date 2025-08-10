import numpy as np

def eoq(demand, ordering_cost, holding_cost):
    return round(np.sqrt((2 * demand * ordering_cost) / holding_cost), 2)

def reorder_point(avg_daily_demand, lead_time):
    return round(avg_daily_demand * lead_time, 2)

def safety_stock(std_dev, lead_time, z_score=1.65):
    return round(z_score * std_dev * np.sqrt(lead_time), 2)
