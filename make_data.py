import numpy as np
import pandas as pd

rng = np.random.default_rng(42) # random seed

# products (price, buy probability )
products = {
    "Laptop": (5500, 0.1),
    "Smartphone": (3200, 0.25),
    "Ipad": (2400, 0.15),
    "Eyephones": (400, 0.30),
    "Smartwatches" :(1200, 0.20),
}

regions = ["East","North","South","Southwest","Northeast"]
region_p =[0.30,0.22,0.22,0.15,0.11]

n = 5000
dates = pd.date_range("2025-07-01", "2025-12-31")

df = pd.DataFrame({
    "date": rng.choice(dates, n),
    "products": rng.choice(list(products), n, p=[v[1] for v in products.values()]),
    "region":rng.choice(regions, n, p =region_p)
})

# remove : 35% data of East in Dec.2025, 20% data of South in Dec.2025
is_dec  = df["date"].dt.month ==12
drop_east = is_dec & (df["region"]=="East") & (rng.random(n)<0.35)
drop_south = is_dec & (df["region"]=="South") & (rng.random(n)<0.20)
df = df[~(drop_east| drop_south)].copy()


# quantity & sales revenue
df["quantity"] = rng.integers(1, 6, len(df))
unit_price = df["products"].map(lambda p: products[p][0])
df["sales"] = (df["quantity"]*unit_price * rng.uniform(0.9, 1.1, len(df))).round(2)

# introducing missing values
df.loc[df.sample(10, random_state=1).index, "region"] = np.nan
df.loc[df.sample(9, random_state=2).index,"sales"] = np.nan

df = df.sort_values("date")
df["date"] = df["date"].dt.strftime("%Y-%m-%d")
df.to_csv("data/sales.csv", index=False)
print(df.shape)
print(df.head)