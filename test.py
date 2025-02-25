import pandas as pd

# Read CSV file into a DataFrame
df = pd.read_csv("accList.csv")

# Check if 'phonggoldz1' exists in the 'acc' column
if "phonggoldz1" in df["acc"].values:
    row = df[df["acc"] == "phonggoldz1"]
    print(row["pass"].values[0])
else:
    print("no")
