"""Telco Customer Churn - exploratory data analysis.

Dataset: IBM Telco Customer Churn sample (7,043 customers).
Public dataset, source: github.com/IBM/telco-customer-churn-on-icp4d

The script cleans the data, computes the key churn drivers and saves the
charts used in the README to the charts/ folder.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(HERE, "charts")
os.makedirs(CHARTS, exist_ok=True)

plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False})

# ---------- load and clean ----------
df = pd.read_csv(os.path.join(HERE, "data", "Telco-Customer-Churn.csv"))
print("rows, cols:", df.shape)

# TotalCharges comes in as text with blank values for new customers
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
blank_total = df["TotalCharges"].isna().sum()
print("blank TotalCharges filled with 0 (tenure 0 customers):", blank_total)
df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
overall = df["ChurnFlag"].mean()
print(f"overall churn rate: {overall:.1%}")

# ---------- 1. churn by contract type ----------
ct = df.groupby("Contract")["ChurnFlag"].agg(["mean", "count"]).sort_values("mean")
print("\nchurn by contract:\n", ct.assign(mean=(ct["mean"] * 100).round(1)))

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(ct.index, ct["mean"] * 100, color=["#d62728", "#ff7f0e", "#1f77b4"])
for i, v in enumerate(ct["mean"] * 100):
    ax.text(i, v + 1, f"{v:.0f}%", ha="center")
ax.set_ylabel("Churn rate (%)")
ax.set_title("Churn rate by contract type")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "churn_by_contract.png"))
plt.close(fig)

# ---------- 2. churn by tenure band ----------
bins = [0, 6, 12, 24, 48, 72]
labels = ["0-6", "7-12", "13-24", "25-48", "49-72"]
df["TenureBand"] = pd.cut(df["tenure"], bins=bins, labels=labels, include_lowest=True)
tb = df.groupby("TenureBand", observed=False)["ChurnFlag"].mean()
print("\nchurn by tenure band (months):\n", (tb * 100).round(1))

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(labels, tb.values * 100, marker="o", color="#d62728")
for x, v in zip(labels, tb.values * 100):
    ax.annotate(f"{v:.0f}%", (x, v), textcoords="offset points", xytext=(0, 8), ha="center")
ax.set_xlabel("Tenure (months)")
ax.set_ylabel("Churn rate (%)")
ax.set_title("Churn falls sharply with tenure")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "churn_by_tenure.png"))
plt.close(fig)

# ---------- 3. monthly charges distribution by churn ----------
fig, ax = plt.subplots(figsize=(7, 4))
for churn, color in [(0, "#1f77b4"), (1, "#d62728")]:
    ax.hist(df.loc[df["ChurnFlag"] == churn, "MonthlyCharges"], bins=30, alpha=0.6,
            label="Churned" if churn else "Stayed", color=color)
ax.set_xlabel("Monthly charges ($)")
ax.set_ylabel("Customers")
ax.set_title("Monthly charges: churned vs stayed")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "monthly_charges_distribution.png"))
plt.close(fig)

# ---------- 4. churn by internet service ----------
isv = df.groupby("InternetService")["ChurnFlag"].agg(["mean", "count"]).sort_values("mean")
print("\nchurn by internet service:\n", isv.assign(mean=(isv["mean"] * 100).round(1)))

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(isv.index, isv["mean"] * 100, color="#9467bd")
for i, v in enumerate(isv["mean"] * 100):
    ax.text(i, v + 1, f"{v:.0f}%", ha="center")
ax.set_ylabel("Churn rate (%)")
ax.set_title("Churn rate by internet service")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "churn_by_internet_service.png"))
plt.close(fig)

# ---------- 5. churn heatmap: contract x payment method ----------
pivot = df.pivot_table(index="Contract", columns="PaymentMethod", values="ChurnFlag",
                       aggfunc="mean") * 100
fig, ax = plt.subplots(figsize=(8, 4))
im = ax.imshow(pivot.values, cmap="Reds", aspect="auto")
ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=20, ha="right")
ax.set_yticks(range(len(pivot.index)), pivot.index)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        ax.text(j, i, f"{pivot.values[i, j]:.0f}%", ha="center", va="center", fontsize=9)
ax.set_title("Churn rate (%): contract type x payment method")
fig.colorbar(im, label="Churn rate (%)")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "churn_heatmap_contract_payment.png"))
plt.close(fig)

# ---------- summary table ----------
summary = pd.DataFrame({
    "segment": ["Overall"] + [f"Contract: {i}" for i in ct.index] + [f"Internet: {i}" for i in isv.index],
    "churn_rate_%": [round(overall * 100, 1)] + [round(v * 100, 1) for v in ct["mean"]]
    + [round(v * 100, 1) for v in isv["mean"]],
})
summary.to_csv(os.path.join(CHARTS, "summary.csv"), index=False)
print("\nsummary:\n", summary)
print("\ndone. charts in", CHARTS)
