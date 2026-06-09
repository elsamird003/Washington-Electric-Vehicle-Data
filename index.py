import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

data = pd.read_csv("asset/Data.csv")

top_n = 30
top_models = data["Make"].value_counts().nlargest(15)
# subset = data[data["Make"].isin(top_models)]

plt.figure(figsize=(10, 6))
sns.barplot(x=top_models.values, y=top_models.index, palette="viridis")
plt.title("Top 15 EV Manufacturers in Washington")
plt.xlabel("Total Vehicles Registered")
plt.ylabel("Manufacturer (Make)")
plt.tight_layout()
plt.show()

