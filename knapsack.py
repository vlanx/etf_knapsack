import yfinance as yf
import argparse
import tomllib
import itertools


def calculate_allocation(prices, budget, window=10):
    """
    prices = current ticker prices
    budget = total amount of money to be invested
    window = result window to consider.
    Ex: If window=10, consider results between [budget-10,budget]
    """

    # Get the max quantities that can be bough of each ETF given the budget.
    max_quantities = {}
    for etf, cost in prices.items():
        max_quantities[etf] = int(budget // cost)

    # Create a list of range objects, one for each ETF
    quantity_ranges = {}
    for etf, mq in max_quantities.items():
        quantity_ranges[etf] = range(mq + 1)

    # Generate all possible combinations of the varying
    # quantities of the ETFs calculated in the previous steps
    products = itertools.product(*quantity_ranges.values())
    all_combinations = product_to_combination(prices, products)

    valid_combinations = []
    for comb in all_combinations:
        price = calculate_buy_price(prices, comb)

        # combination can be purchased given the budget
        if price >= (budget - window) and price <= (budget + window):
            valid_combinations.append(comb)

    return valid_combinations


def product_to_combination(prices, products):
    combinations = []
    """
    For every product with the various quantities of the ETFs,
    associate said quantities to the corresponding ETF.
    This hinges on the fact that every read of a python dictionary
    is the same, i.e., the order of etfs is the same.
    """
    for product in products:
        combinations.append(dict(zip(prices.keys(), product)))

    return combinations


def calculate_buy_price(prices, combination):
    """Calculate the total amount that
    would be spent of the budget if this
    combination were to take place
    """

    total = 0
    for etf, quantity in combination.items():
        total += quantity * prices[etf]

    return total


def calculate_commission(combination):
    """
    In IBKR, for each transaction, the normal commission
    is of 1,25€
    """

    # Get the number of bought ETFs thats greater than 0, which means a transaction
    transactions = sum(i > 0 for i in combination.values())

    return transactions * 1.25


def calculate_new_balance(prices, allocation, combination):
    """
    Calculate portfolio balance with the new ETF ammount.
    This will give the weight for each ETF if a given combination choice is taken.
    """
    # Calculate the total amount of value this allocation would have if this combinations
    # were to be bought so that we can calculate the weight after.
    total_money = 0
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            total_money += quantity
        else:
            total_money += (quantity + combination[etf]) * prices[etf]

    new_weights = {}
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            new_weights[etf] = (quantity / total_money) * 100
        else:
            new_weights[etf] = (
                ((quantity + combination[etf]) * prices[etf]) / total_money
            ) * 100

    return new_weights


def calculate_current_balance(prices, allocation):
    """
    Calculate the current portfolio balance.
    """

    total_money = 0
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            total_money += quantity
        else:
            total_money += quantity * prices[etf]

    weights = {}
    for etf, quantity in allocation.items():
        # Money quantity is a special case
        if etf == "MONEY":
            weights[etf] = (quantity / total_money) * 100
        else:
            weights[etf] = ((quantity * prices[etf]) / total_money) * 100

    return weights, total_money


def get_ticker_prices(tickers):
    prices = {}
    for etf, ticker in tickers.items():
        # get the current bid price
        prices[etf] = yf.Ticker(ticker).info["bid"]

    return prices


def load_info():
    with open("info.toml", "rb") as f:
        return tomllib.load(f)


def print_combinations(prices, quantity, combinations, balance):
    """
    Pretty print the options and possible buy combinations given the budget.
    The `balance` argument is the current balance so we can calculate the delta.
    """
    for idx, comb in enumerate(combinations):
        new_weights = calculate_new_balance(prices, quantity, comb)
        buy_price = calculate_buy_price(prices, comb)
        comissions = calculate_commission(comb)
        print(
            f"---------------------------------------------------------------",
            f"\nOpt. {idx+1} | Buying",
            ", ".join([f"{ammount} {etf}" for etf, ammount in comb.items()]),
            f"would use {buy_price:,.2f}€",
            f"with +{comissions:,.2f}€ comission",
            f"for {(buy_price+comissions):,.2f}€ total."
            f"\nPortfolio allocation would be:",
            " | ".join(
                [
                    f"{etf}: {weight:.2f}%({delta(weight,balance[etf])}%)"
                    for etf, weight in new_weights.items()
                ]
            ),
        )


def delta(new_weight, current_weight):
    difference = round(abs(new_weight - current_weight), 2)

    if new_weight > current_weight:
        return f"+{difference}"
    else:
        return f"-{difference}"


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
