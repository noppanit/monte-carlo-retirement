import numpy as np

from src.shiller import *
from src.cdc_life_tables import *


def run_histories(starting_assets,
                  yearly_expense,
                  stock_fraction,
                  starting_age,
                  state_abbrev,
                  demographic_group,
                  n_mc=1000):
    # Life table
    table = life_table(state_abbrev, demographic_group)

    mc_histories = []
    rand = np.random.random_sample

    for i in range(n_mc):

        age = starting_age
        current_assets = starting_assets
        expenses_per_year = yearly_expense

        assets = [current_assets]

        # Loop over years
        while current_assets > 0:

            # Death this year.
            if age >= 110 or rand() <= table[int(age)]:
                # Die at random point in year
                current_assets -= expenses_per_year * rand()
                break

            # Subtracting expenses for year
            current_assets -= expenses_per_year

            # Pick past year by random to base inflation, stock return data
            i = np.random.randint(inflation.size, size=1)
            i = int(i)

            # Adjust expenses for inflation.
            expenses_per_year *= 1.0 + inflation.iloc[i]

            # Adding stock investment increase
            stock_gains = stock_returns.iloc[i] * (current_assets * stock_fraction)

            # Adding bond investment increase
            bond_gains = interest_rates.iloc[i] * (current_assets * (1 - stock_fraction))

            current_assets += stock_gains
            current_assets += bond_gains

            # Saving current assets
            assets.append(current_assets)

            # Getting old
            age += 1.0

        assets = np.array(assets)

        mc_histories.append((assets))

    return mc_histories


if __name__ == '__main__':
    run_histories(yearly_expense=50000.00, starting_assets=500000.00, stock_fraction=0.5,
                  starting_age=65, state_abbrev='IA', demographic_group='white female', n_mc=100)
