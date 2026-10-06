from data_layer import load_and_validate, DataValidationError
import pandas as pd
import json

# test1 : normal data
df, report = load_and_validate()
print(json.dumps(report, ensure_ascii=False, indent=2))

# test2 : missing value--> error
pd.DataFrame({"date": ["2025-01-01"], "products": ["Smartphones"]}).to_csv("data/bad.csv", index=False)
try:
    load_and_validate("data/bad.csv")
except DataValidationError as e:
    print("\nexpected error report ->", e)

# test3: file not exist
try:
    load_and_validate("data/nope.csv")
except DataValidationError as e:
    print("expected error report ->", e)