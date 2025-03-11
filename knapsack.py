import argparse
import itertools
import tomllib
import yfinance as yf
from typing import Any


def calculate_allocation(prices: dict[str, float], budget: int, window=10):
    """
    prices = current ticker prices
    budget = total amount of money to be invested
    window = result window to consider.
    Ex: If window=10, consider results between [budget-10,budget]
    """

    # Get the max quantities that can be bough of each ETF given the budget.
    max_quantities: dict[str, int] = {}
    for etf, cost in prices.items():
        max_quantities[etf] = int(budget // cost)

    # Create a list of range objects, one for each ETF
    quantity_ranges: dict[str, range] = {}
    for etf, mq in max_quantities.items():
        quantity_ranges[etf] = range(mq + 1)

    # Generate all possible combinations of the varying
    # quantities of the ETFs calculated in the previous steps
    # Ex: [(2, 0, 6), (2, 0, 7), (2, 1, 0), (2, 1, 1),,...]
    # The order of the tuples is the same as the dictionary keys, since python
    # maintains the read order on every iteration. see: `product_to_combination`
    products = list(itertools.product(*quantity_ranges.values()))
    all_combinations = product_to_combination(prices, products)

    valid_combinations: list[dict[str, int]] = []
    for comb in all_combinations:
        price = calculate_buy_price(prices, comb)

        # combination can be purchased given the budget
        if price >= (budget - window) and price <= (budget + window):
            valid_combinations.append(comb)

    return valid_combinations


def product_to_combination(prices: dict[str, float], products: list[tuple[int, ...]]):
    """
    For every product with the various quantities of the ETFs,
    associate said quantities to the corresponding ETF.
    This hinges on the fact that every read of a python dictionary
    is the same on every read operation, i.e., the order of the keys of the dictionary in this function
    will be in the same order from when we calculated the various quantities previously, allowing us
    to map the quantities to the keys.
    Ex: `{'VUAA': 2, 'VWCE': 0, 'QDVE': 2}`
    """

    combinations: list[dict[str, int]] = []
    for product in products:
        combinations.append(dict(zip(prices.keys(), product)))

    return combinations


def calculate_buy_price(prices: dict[str, float], combination: dict[str, int]):
    """Calculate the total amount that
    would be spent of the budget if this
    combination were to take place
    """

    total = 0.0
    for etf, quantity in combination.items():
        total += quantity * prices[etf]

    return total


def calculate_commission(combination: dict[str, int]):
    """
    In IBKR, for each transaction, the normal commission
    is of 1,25€
    """

    # Get the number of bought ETFs thats greater than 0, which means a transaction
    transactions = sum(i > 0 for i in combination.values())

    return transactions * 1.25


def calculate_new_balance(
    prices: dict[str, float], allocation: dict[str, int], combination: dict[str, int]
):
    """
    Calculate portfolio balance with the new ETF ammount.
    This will give the weight for each ETF if a given combination choice is taken.
    """
    # Calculate the total amount of value this allocation would have if this combinations
    # were to be bought so that we can calculate the weight after.
    total_money = 0.0
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            total_money += quantity
        else:
            total_money += (quantity + combination[etf]) * prices[etf]

    new_weights: dict[str, float] = {}
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            new_weights[etf] = (quantity / total_money) * 100
        else:
            new_weights[etf] = (
                ((quantity + combination[etf]) * prices[etf]) / total_money
            ) * 100

    return new_weights


def calculate_current_balance(prices: dict[str, float], allocation: dict[str, int]):
    """
    Calculate the current portfolio balance.
    """

    total_money = 0.0
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            total_money += quantity
        else:
            total_money += quantity * prices[etf]

    weights: dict[str, float] = {}
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            weights[etf] = (quantity / total_money) * 100
        else:
            weights[etf] = ((quantity * prices[etf]) / total_money) * 100

    return weights, total_money


def get_ticker_prices(tickers: dict[str, str]):
    prices: dict[str, float] = {}
    for etf, ticker in tickers.items():
        # get the current bid price
        prices[etf] = yf.Ticker(ticker).info["bid"]

    return prices


def delta(new_weight: float, current_weight: float):
    difference = round(abs(new_weight - current_weight), 2)

    if new_weight > current_weight:
        return f"+{difference}"
    else:
        return f"-{difference}"


def load_info() -> dict[str, Any]:
    with open("info.toml", "rb") as f:
        return tomllib.load(f)


def print_combinations(
    prices: dict[str, float],
    quantity: dict[str, int],
    combinations: list[dict[str, int]],
    balance: dict[str, float],
):
    """
    Pretty print the options and possible buy combinations given the budget.
    The `balance` argument is the current balance so we can calculate the delta.
    """
    for idx, comb in enumerate(combinations):
        new_weights = calculate_new_balance(prices, quantity, comb)
        buy_price = calculate_buy_price(prices, comb)
        commissions = calculate_commission(comb)
        print(
            f"---------------------------------------------------------------",
            f"\nOpt. {idx + 1} | Buying",
            ", ".join([f"{ammount} {etf}" for etf, ammount in comb.items()]),
            f"would use {buy_price:,.2f}€",
            f"with +{commissions:,.2f}€ commission",
            f"for {(buy_price + commissions):,.2f}€ total."
            f"\nPortfolio allocation would be:",
            " | ".join(
                [
                    f"{etf}: {weight:.2f}%({delta(weight, balance[etf])}%)"
                    for etf, weight in new_weights.items()
                ]
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", help="Ammount of money to be invested")
    parser.add_argument(
        "--window",
        help="Result window to consider. ex: If window=10, consider results between [budget-10,budget]",
        default=10,
    )
    args = parser.parse_args()

    if args.budget:
        w = int(args.window)
        b = int(args.budget)
        info = load_info()
        prices = get_ticker_prices(info["tickers"])
        balance, total_money = calculate_current_balance(prices, info["allocation"])

        print(
            "ETFs Price:",
            " | ".join([f"{etf}: {price}€" for etf, price in prices.items()]),
        )
        print(
            "Portfolio Allocation:",
            " | ".join([f"{etf}: {weight:.2f}%" for etf, weight in balance.items()]),
            f"\nValue: {total_money:,.2f}€",
        )
        print(
            f"Performing calculations with Budget = {args.budget}€ and Window = {args.window}€"
        )
        combinations = calculate_allocation(prices, budget=b, window=w)
        print_combinations(prices, info["allocation"], combinations, balance)
    else:
        print("No budget ammount specified")
