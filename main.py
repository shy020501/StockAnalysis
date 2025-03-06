import os
import numpy as np
import argparse

from analysis import *
from utils import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETF Analysis Script")
    
    parser.add_argument("--analysis", type=str, required=True, help="Type of analysis to perform")
    parser.add_argument("--tickers", type=lambda s: s.split(' '), default=["SCHD", "SPY", "QQQ"],
                        help="Whitespace-separated list of ETF tickers (default: SCHD SPY QQQ)")
    parser.add_argument("--abbrs", type=lambda s: s.split(' '), default=["S", "P", "Q"],
                        help="Whitespace-separated list of abbreviation of ETF tickers (default: S P Q)")
    parser.add_argument("--downward_only", action="store_true", help="Get downward value only (default: False)")
    parser.add_argument("--save_path", type=str, default="./output", help="Directory to save results")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
    
    if args.analysis == "avg_return_volatility":
        save_dir = f"{args.save_path}/avg_return_volatility/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        analysed_info = {}
        
        if len(args.tickers) > 1:
            stock_info, latest_start_date = get_multiple_stock_info(args.tickers)
            paired_stock_info, paired_abbrs = stock_combination(stock_info, args.abbrs, 2)
            
            for stock_comb, abbr_comb in zip(paired_stock_info, paired_abbrs):
                stock_comb = list(stock_comb)
                abbr_comb = list(abbr_comb)
                
                ratio_interval = np.arange(0.1, 1.0, 0.1)
                ratios = [[r, 1 - r] for r in ratio_interval]
                
                for ratio in ratios:
                    weighted_return, combined_ticker = get_mixed_data(stock_comb, abbr_comb, ratio)
                    _, avg_return = get_annual_return(weighted_return)
                    _, avg_volatility = get_annual_volatility(weighted_return, args.downward_only)
                    
                    analysed_info[combined_ticker] = (avg_return, avg_volatility)
        else:
            stock_info = [yf.download(args.tickers[0], period="max", interval="1d", auto_adjust=False)]
                    
        for i in range(len(args.tickers)):
            daily_return = stock_info[i]['Adj Close'].pct_change().dropna()
            _, avg_return = get_annual_return(daily_return)
            _, avg_volatility = get_annual_volatility(daily_return, True)
            analysed_info[args.tickers[i]] = (avg_return, avg_volatility)
                
        color_map = assign_color(list(set([simplify_ticker(ticker) for ticker in analysed_info.keys()])))

        plt.figure(figsize=(10, 6))
        for ticeker, (avg_return, avg_volatility) in analysed_info.items():
            base = simplify_ticker(ticeker)
            color = color_map[base] if base in color_map else "gray"
            
            plt.scatter(avg_volatility * 100, avg_return * 100, s=500, color=color, alpha=0.6, edgecolors='black')
            plt.text(avg_volatility * 100, avg_return * 100, ticeker, fontsize=8, ha='center', va='center', fontweight='bold')

        abbr_text = "\n".join([f"{abbr}: {ticker}" for abbr, ticker in zip(args.abbrs, args.tickers)])
        plt.text(1.02, 0.5, abbr_text, transform=plt.gca().transAxes, fontsize=10, verticalalignment='center', bbox=dict(facecolor='white', alpha=0.5))

        x_label = "Downside Volatility (%)" if args.downward_only else "Volatility (%)"
        file_name = "-".join([ticker for ticker in args.tickers])
        
        if args.downward_only:
            file_name += "-downward_only"
        
        plt.xlabel(x_label)
        plt.ylabel("Average Annual Return (%)")
        plt.title(f"Start date : {latest_start_date}")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f"{save_dir}/{file_name}.png")
