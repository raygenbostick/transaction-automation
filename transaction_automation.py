"""
Transaction data automation.

Loads the transaction file, filters to a target quarter and set of states,
builds the broker output file, and prints a state-by-state premium
validation summary for comparison against the FDW validation pull.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TRANSACTION_FILE = "2026.02 Transaction Data.xlsm"

STATES = [
    "AL",
    "CO",
    "KS",
    "MT",
    "OK",
    "SD",
    "TN",
    "WY",
]

YEAR = 2026
QUARTER = 2

QUARTER_MONTHS = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
    4: [10, 11, 12],
}

# ---------------------------------------------------------------------------
# Broker map
# ---------------------------------------------------------------------------
BROKER_MAP = {
    "Burns and Wilcox": {
        "BrokerNumber": 16865716,
        "BrokerFirstName": "Samuel",
        "BrokerLastName": "Carson",
    },
    "Braishfield Associates Inc": {
        "BrokerNumber": 124318,
        "BrokerFirstName": "John",
        "BrokerLastName": "Barfield",
    },
}

# ---------------------------------------------------------------------------
# Load the transaction file
# ---------------------------------------------------------------------------
df = pd.read_excel(
    TRANSACTION_FILE,
    sheet_name=1,
    engine="openpyxl",
)
df.columns = df.columns.str.strip()
print(df.shape)

# ---------------------------------------------------------------------------
# Quarter filter
# ---------------------------------------------------------------------------
df["Policy Effective Date"] = pd.to_datetime(
    df["Policy Effective Date"], errors="coerce"
)

df = df[
    (df["Policy Effective Date"].dt.year == YEAR)
    & (df["Policy Effective Date"].dt.month.isin(QUARTER_MONTHS[QUARTER]))
].copy()

print("Rows after quarter filter:", len(df))

# ---------------------------------------------------------------------------
# State filter
# ---------------------------------------------------------------------------
df = df[df["State (of Risk)"].isin(STATES)].copy()

print("Rows after state filter:", len(df))

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
print("Policy Effective Date Min:", df["Policy Effective Date"].min())
print("Policy Effective Date Max:", df["Policy Effective Date"].max())
print("Rows after quarter filter:", len(df))

# ---------------------------------------------------------------------------
# Create output
# ---------------------------------------------------------------------------
output = pd.DataFrame()

output["BrokerNumber"] = df["Program Administrator Name"].map(
    lambda x: BROKER_MAP[x]["BrokerNumber"]
)
output["BrokerFirstName"] = df["Program Administrator Name"].map(
    lambda x: BROKER_MAP[x]["BrokerFirstName"]
)
output["BrokerLastName"] = df["Program Administrator Name"].map(
    lambda x: BROKER_MAP[x]["BrokerLastName"]
)

# TODO: the ISIPC source column was unreadable in the original screenshot
# output["ISIPC"] = df["<source column>"]

output["PolicyNumber"] = (
    df["Policy Number"]
    .fillna(0)
    .astype(int)
    .astype(str)
)

output["InsuredName"] = (
    df["First Name of Primary Insured"].fillna("").astype(str)
    + " "
    + df["Last Name of Primary Insured"].fillna("").astype(str)
)

output["State"] = df["State (of Risk)"]

output["EffectiveDate"] = pd.to_datetime(
    df["Transaction Effective Date"]
).dt.strftime("%m/%d/%Y")

output["Premium"] = df["P&L Impact"]

output["CustomPolicyID"] = ""
output["CustomTransactionID"] = ""

# ---------------------------------------------------------------------------
# Validate output
# ---------------------------------------------------------------------------
print("Rows:", len(output))
print("Premium Total:", round(output["Premium"].sum(), 2))

# ---------------------------------------------------------------------------
# Export to CSV
# ---------------------------------------------------------------------------
outfile = f"13167_NorthLight_MultiState_Q{QUARTER}_{YEAR}.csv"

output.to_csv(outfile, index=False)

print("Created:", outfile)

# ---------------------------------------------------------------------------
# State premium validation summary
#
# Creates a state-by-state premium total from the final output and displays
# the overall premium. Lets the user quickly compare automation results
# against the FDW validation pull to confirm that all states and premium
# amounts were included correctly before submission.
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STATE PREMIUM VALIDATION SUMMARY")
print("=" * 60)

state_summary = (
    output.groupby("State")["Premium"]
    .sum()
    .sort_index()
)

for state, premium in state_summary.items():
    print(f"{state}: ${premium:,.2f}")

print("-" * 60)
print(f"TOTAL PREMIUM: ${state_summary.sum():,.2f}")
print("=" * 60)
