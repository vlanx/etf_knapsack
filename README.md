# ETF Knapsack Problem

Do you invest monthly into more than one **ETF**? 

Have you ever wondered how many combinations of each ETF you can buy given your **monthly budget**?

This Python scripts is here to help.

Simply edit the `info.toml` (a sample one is provided) file with your personal portfolio allocation and savings amount and run the script.

## Usage
```
cd ~
git clone "https://github.com/dot-1q/etf_knapsack.git"
cd etf_knapsack
pip3 install -r requirements.txt
```

```
python3 knapsack.py --budget <budget>
```
or
```
python3 knapsack.py --budget <budget> --window <window>
```

## Configuration file `info.toml`

Place in `[tickers]` the tickers of the ETFs you own. The ticker has to come from [Yahoo Finance](https://finance.yahoo.com/). No registration needed, but has free usage rate limits. Check [yfinance](https://github.com/ranaroussi/yfinance)

Ex: [VWCE](https://finance.yahoo.com/quote/VWCE.DE/) is `VWCE.DE`

Edit `[allocation]` to reflect your current amount of owned ETFs positions and amount of money in savings (optional and can be deleted).

```
[tickers]
<etf1> = "<etf1_ticker>"
<etf2> = "<etf2_ticker>"
<etf3> = "<etf3_ticker>"
...

[allocation]
<etf1> = <quantity>
<etf2> = <quantity>
<etf3> = <quantity>
...
MONEY = 100000 # In Euros/Dollars
```

## Output
For the sample `info.toml` file.

```
python3 knapsack.py --budget 500
```

```
ETFs Price: VUAA: 104.165€ | VWCE: 132.04€ | QDVE: 29.41€
Portfolio Allocation: VUAA: 25.54% | VWCE: 21.58% | QDVE: 12.02% | MONEY: 40.86%
Value: 12,236.25€
Performing calculations with Budget = 500€ and Window = 10€
---------------------------------------------------------------
Opt. 1 | Buying 0 VUAA, 0 VWCE, 17 QDVE would use 499.97€ with +1.25€ comission for 501.22€ total.
Portfolio allocation would be: VUAA: 24.54%(-1.0%) | VWCE: 20.73%(-0.85%) | QDVE: 15.47%(+3.45%) | MONEY: 39.26%(-1.6%)
---------------------------------------------------------------
Opt. 2 | Buying 0 VUAA, 2 VWCE, 8 QDVE would use 499.36€ with +2.50€ comission for 501.86€ total.
Portfolio allocation would be: VUAA: 24.54%(-1.0%) | VWCE: 22.81%(+1.23%) | QDVE: 13.39%(+1.38%) | MONEY: 39.26%(-1.6%)
---------------------------------------------------------------
Opt. 3 | Buying 1 VUAA, 1 VWCE, 9 QDVE would use 500.89€ with +3.75€ comission for 504.64€ total.
Portfolio allocation would be: VUAA: 25.35%(-0.19%) | VWCE: 21.77%(+0.19%) | QDVE: 13.62%(+1.61%) | MONEY: 39.26%(-1.61%)
---------------------------------------------------------------
Opt. 4 | Buying 1 VUAA, 3 VWCE, 0 QDVE would use 500.29€ with +2.50€ comission for 502.79€ total.
Portfolio allocation would be: VUAA: 25.35%(-0.19%) | VWCE: 23.84%(+2.26%) | QDVE: 11.55%(-0.47%) | MONEY: 39.26%(-1.61%)
---------------------------------------------------------------
Opt. 5 | Buying 2 VUAA, 0 VWCE, 10 QDVE would use 502.43€ with +2.50€ comission for 504.93€ total.
Portfolio allocation would be: VUAA: 26.17%(+0.63%) | VWCE: 20.73%(-0.85%) | QDVE: 13.85%(+1.83%) | MONEY: 39.25%(-1.61%)
---------------------------------------------------------------
Opt. 6 | Buying 2 VUAA, 2 VWCE, 1 QDVE would use 501.82€ with +3.75€ comission for 505.57€ total.
Portfolio allocation would be: VUAA: 26.17%(+0.63%) | VWCE: 22.80%(+1.22%) | QDVE: 11.78%(-0.24%) | MONEY: 39.25%(-1.61%)
---------------------------------------------------------------
Opt. 7 | Buying 3 VUAA, 1 VWCE, 2 QDVE would use 503.35€ with +3.75€ comission for 507.10€ total.
Portfolio allocation would be: VUAA: 26.98%(+1.44%) | VWCE: 21.77%(+0.18%) | QDVE: 12.00%(-0.01%) | MONEY: 39.25%(-1.61%)
---------------------------------------------------------------
Opt. 8 | Buying 4 VUAA, 0 VWCE, 3 QDVE would use 504.89€ with +2.50€ comission for 507.39€ total.
Portfolio allocation would be: VUAA: 27.80%(+2.26%) | VWCE: 20.73%(-0.86%) | QDVE: 12.23%(+0.22%) | MONEY: 39.24%(-1.62%)
```

As you can see, it outputs all the combinations that you can make with 500€. It also provides the current portfolio balance given your current allocation and the new allocation were you to buy the given combination.

The window can be adjusted as well. It simply provides a range for the total amount of money that can be spent. [500-window] to [500+window].

The current commission price is calculated by [IBKR](https://www.interactivebrokers.ie/en/home.php) standards.


#### TODO
    1) Enhance the output. Probably needs to be more concise and I should add color.
    2) Provide ways to optimize the combinatorial algorithm. e.g, discard options which have an ETF you don't want to buy this month.
    3) Provide Allocation Goals (% of weight for each ETF) and present the outputs in order of best match.
    4) Provide more brokers and their respective commission policy.
    5) GUI?
    6) More API options. Currently only Yahoo Finance is available.

# ⚠️ Disclaimer
This tool is for informational and educational purposes only. It does not provide financial, investment, or trading advice. 
Use it at your own risk. Always consult a financial professional before making investment decisions. 
The author is not responsible for any financial losses or decisions made based on the output of this tool.
