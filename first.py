import pandas as pd

co2 = pd.read_csv("co-emissions-per-capita.csv")
pib = pd.read_csv("gdp-per-capita-worldbank.csv")
exp = pd.read_csv("life-expectancy.csv")

merge1 = pd.merge(co2,pib,on=["Entity","Code","Year"], how="left").merge(exp)

print(merge1)

