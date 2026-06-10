import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

data = pd.read_csv("asset/Data.csv")

top_n = 30
top_models = data["Model"].value_counts().nlargest(top_n).index
subset = data[data["Model"].isin(top_models)]

plt.figure(figsize=(10, 8)) ## 10 witdth an 8 inches height
plt.countplot(
    y="Model",
    data=subset,
    order=top_models[::-1],  # highest count at top
    color="red",
)
plt.
plt.title(f"Top {top_n} EV models (Washington registrations)")
plt.xlabel("Count")
plt.ylabel("Model")
plt.tight_layout()
plt.show()

