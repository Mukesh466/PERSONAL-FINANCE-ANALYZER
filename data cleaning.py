# data_cleaning.py

import pandas as pd


def clean_data(file_path):
    # 1. Read CSV file
    df = pd.read_csv(file_path)

    print("Original Data:")
    print(df)

    # 2. Remove duplicate rows
    df = df.drop_duplicates()

    # 3. Convert Date column to proper date format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # 4. Remove rows where Date is invalid
    df = df.dropna(subset=["Date"])

    # 5. Clean Description
    df["Description"] = df["Description"].fillna("Unknown")
    df["Description"] = df["Description"].astype(str).str.strip()

    # 6. Clean Category
    df["Category"] = df["Category"].fillna("Other")
    df["Category"] = df["Category"].astype(str).str.strip().str.title()

    # 7. Clean Type
    df["Type"] = df["Type"].fillna("Expense")
    df["Type"] = df["Type"].astype(str).str.strip().str.title()

    # 8. Convert Amount to numeric
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    # 9. Remove rows with invalid amount
    df = df.dropna(subset=["Amount"])

    # 10. Remove negative amounts
    df = df[df["Amount"] >= 0]

    # 11. Keep only valid transaction types
    df = df[df["Type"].isin(["Income", "Expense"])]

    # 12. Sort by date
    df = df.sort_values(by="Date")

    # 13. Reset index
    df = df.reset_index(drop=True)

    return df


# Main program
if __name__ == "__main__":

    input_file = "data/transactions.csv"
    output_file = "data/cleaned_transactions.csv"

    cleaned_df = clean_data(input_file)

    # Save cleaned data
    cleaned_df.to_csv(output_file, index=False)

    print("\nCleaned Data:")
    print(cleaned_df)

    print("\nData cleaning completed successfully!")
    print(f"Cleaned file saved to: {output_file}")
