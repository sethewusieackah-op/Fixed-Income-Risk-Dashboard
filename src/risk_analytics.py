import pandas as pd
import numpy as np

df = pd.read_csv('financial_raw.csv')

print("--- DATA LOADED SUCCESSFULLY ---")
print(df.head())

print("\nAvailable Columns:")
print(df.columns.tolist())


# 2. Define the quantitative bond metrics function
def calculate_bond_metrics(row):
    F = row['face_value']
    c = row['coupon_rate']
    T = row['years_to_maturity']
    y = row['ytm']
    m = row.get('frequency', 2)  # Default to semi-annual (2) if frequency isn't specified

    periods = int(T * m)
    coupon_payment = (F * c) / m
    period_ytm = y / m

    if periods <= 0 or period_ytm <= 0:
        return pd.Series({
            'Bond_Price': np.nan,
            'Macaulay_Duration': np.nan,
            'Modified_Duration': np.nan,
            'Convexity': np.nan,
            'DV01': np.nan
        })

    # Bond Price (DCF Formula)
    t = np.arange(1, periods + 1)
    discount_factors = (1 + period_ytm) ** t
    pv_coupons = np.sum(coupon_payment / discount_factors)
    pv_face = F / ((1 + period_ytm) ** periods)
    bond_price = pv_coupons + pv_face

    # Macaulay Duration (in years)
    mac_dur_periods = np.sum((t * coupon_payment) / discount_factors) + (
        periods * pv_face / ((1 + period_ytm) ** periods)
    )
    macaulay_duration = (mac_dur_periods / bond_price) / m

    # Convexity
    convexity_sum = np.sum(
        (t * (t + 1) * coupon_payment) / ((1 + period_ytm) ** (t + 2))
    ) + (periods * (periods + 1) * pv_face / ((1 + period_ytm) ** (periods + 2)))
    convexity = convexity_sum / (bond_price * (m ** 2))

    # Modified Duration & DV01 (Dollar Value of 1 basis point)
    modified_duration = macaulay_duration / (1 + period_ytm)
    dv01 = bond_price * modified_duration * 0.0001

    return pd.Series({
        'Bond_Price': round(bond_price, 4),
        'Macaulay_Duration': round(macaulay_duration, 4),
        'Modified_Duration': round(modified_duration, 4),
        'Convexity': round(convexity, 4),
        'DV01': round(dv01, 4),
    })


# 3. Apply the calculations across all rows
df[['Bond_Price', 'Macaulay_Duration', 'Modified_Duration', 'Convexity', 'DV01']] = df.apply(
    calculate_bond_metrics, axis=1
)

# 4. Display the resulting financial metrics
print('\n--- QUANTITATIVE BOND METRICS ---')
print(
    df[[
        'face_value',
        'coupon_rate',
        'years_to_maturity',
        'ytm',
        'Bond_Price',
        'Macaulay_Duration',
        'Modified_Duration',
        'Convexity',
        'DV01',
    ]].head()
)


# --- ADD THE STRESS-TEST CALCULATIONS HERE ---
shocks = {
    'Price_Shock_Plus_200bps': 0.02,
    'Price_Shock_Plus_100bps': 0.01,
    'Price_Shock_Minus_100bps': -0.01,
    'Price_Shock_Minus_200bps': -0.02
}

for col_name, dy in shocks.items():
    # Using the computed Modified_Duration and Convexity for accurate second-order Taylor series approximation
    pct_change = (-df['Modified_Duration'] * dy) + (0.5 * df['Convexity'] * (dy ** 2))
    df[col_name] = df['Bond_Price'] * (1 + pct_change)

# Export the complete results to a new CSV file
df.to_csv('financial_calculated_results.csv', index=False)
print("\n--- RESULTS SUCCESSFULLY SAVED TO CSV ---")
