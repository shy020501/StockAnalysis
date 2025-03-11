import os
import numpy as np
import argparse
import yfinance as yf
from matplotlib.patches import Patch
import matplotlib.ticker as mticker
from matplotlib.ticker import MultipleLocator

from analysis import *
from utils import *

AVAIL_ANALYSIS = ["avg_return_volatility", "compare_avg_return_volatility", "long_term_investment", "cummulative_return"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETF Analysis Script")
    
    available_methods = ", ".join(method for method in AVAIL_ANALYSIS)
    parser.add_argument("--analysis", type=str, required=True, help=f"Type of analysis to perform: {available_methods}")
    parser.add_argument("--tickers", type=lambda s: s.split(' '), required=True,
                        help="Whitespace-separated list of ETF tickers (default: SCHD SPY QQQ)")
    parser.add_argument("--save_path", type=str, default="./output", help="Directory to save results")
    
    # avg_return_volatility & single_avg_return_volatility 전용
    parser.add_argument("--downward_only", action="store_true", help="Get downward value only (default: False)")
    parser.add_argument("--abbrs", type=lambda s: s.split(' '), default=None,
                        help="Whitespace-separated list of abbreviation of ETF tickers (default: S P Q)")
    parser.add_argument("--must_include", type=lambda s: s.split(' '), default=None,
                        help="Whitespace-separated list of abbreviation of ETF that must be included in combination (default: None)")
    
    # long_term_investment 전용
    parser.add_argument("--min_year", type=int, default=2, help="Minimum years of investment")
    parser.add_argument("--max_year", type=int, default=10, help="Maximum years of investment")
    parser.add_argument("--interval", type=int, default=2, help="Interval of years to investigate effect of long-term investment")
    parser.add_argument("--num_samples", type=int, default=500, help="Number of samples")
    
    # cummulative_return 전용
    parser.add_argument("--start_year", type=int, default=None, help="Starting year to measure cummulative return")
    
    args = parser.parse_args()
    
    error_msg = f"{args.analysis}은 가능한 분석 목록에 없습니다."
    assert args.analysis in AVAIL_ANALYSIS, error_msg
    
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
        
    if args.analysis == "avg_return_volatility":
        assert len(args.tickers) == len(args.abbrs), "Tickers와 abbrs의 개수가 같아야 합니다."
        assert all(len(abbr) == 1 for abbr in args.abbrs), "각 종목은 1개의 알파벳으로 표현해야 합니다."
        assert len(args.abbrs) == len(set(args.abbrs)), "각 종목은 각각 다른 알파벳으로 표현해야 합니다."
        assert args.must_include is None or all(len(abbr) == 1 for abbr in args.must_include), "must_include는 abbreviation으로 주어져야 합니다."
        assert args.must_include is None or all(abbr in args.abbrs for abbr in args.must_include), "must_include에 포함된 종목들은 abbrs 안에 정의돼있어야 합니다."
        
        save_dir = f"{args.save_path}/avg_return_volatility/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        analysed_info = {}
        
        if len(args.tickers) > 1:
            stock_info = get_multiple_stock_info(args.tickers)
            paired_stock_info, paired_abbrs = stock_combination(stock_info, args.abbrs, 2, args.must_include)
            
            for stock_comb, abbr_comb in zip(paired_stock_info, paired_abbrs):
                stock_comb = list(stock_comb)
                abbr_comb = list(abbr_comb)
                
                ratio_interval = np.arange(0.1, 1.0, 0.1)
                ratios = [[r, 1 - r] for r in ratio_interval]
                
                for ratio in ratios:
                    weighted_return, combined_ticker = get_mixed_data(stock_comb, ratio, abbr_comb)
                    avg_return = get_annual_return(weighted_return)
                    avg_volatility = get_annual_volatility(weighted_return, args.downward_only)
                    
                    analysed_info[combined_ticker] = (avg_return, avg_volatility)
        else:
            stock_info = [yf.download(args.tickers[0], period="max", interval="1d", auto_adjust=False)]
            
        # get_annual_return()와 get_annual_volatility()에서 첫 & 마지막 연도 제거할 것을 고려하여 설정
        start_year = stock_info[0].index.min().year + 1
        end_year = stock_info[0].index.max().year - 1
                    
        for i in range(len(args.tickers)):
            daily_return = stock_info[i]['Adj Close'].pct_change().dropna()
            avg_return = get_annual_return(daily_return)
            avg_volatility = get_annual_volatility(daily_return, args.downward_only)
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

        x_label = "Downside Volatility" if args.downward_only else "Volatility"
        file_name = "-".join([ticker for ticker in args.tickers])
        
        if args.downward_only:
            file_name += "-downward_only"
        if args.must_include is not None:
            file_name += "-must_include-"
            file_name += "-".join([ticker for ticker in args.must_include])
        
        plt.xlabel(f"{x_label} (%)")
        plt.ylabel("Average Annual Return (%)")
        plt.title(f"Average Return & {x_label} ({start_year} ~ {end_year})")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f"{save_dir}/{file_name}.png")
    
    if args.analysis == "compare_avg_return_volatility":
        save_dir = f"{args.save_path}/compare_avg_return_volatility/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        analysed_info = {}
        valid_years = {}
        
        single_ticker_info = {}
        
        for portfolio_str in args.tickers:
            portfolio = parse_string_digit_pairs(portfolio_str)
            
            if len(portfolio) > 1:
                tickers, ratios = zip(*portfolio)
                
                tickers = list(tickers)
                ratios = list(ratios)
                
                stock_info = get_multiple_stock_info(tickers)
                daily_return, _ = get_mixed_data(stock_info, ratios, None)
                
                avg_return = get_annual_return(daily_return)
                avg_volatility = get_annual_volatility(daily_return, args.downward_only)
                
                for i in range(len(stock_info)):
                    single_ticker = stock_info[i].columns.get_level_values('Ticker').unique()[0]
                    if single_ticker not in single_ticker_info:
                        daily_return = stock_info[i]['Adj Close'].pct_change().dropna()
                        
                        single_avg_return = get_annual_return(daily_return)
                        single_avg_volatility = get_annual_volatility(daily_return, args.downward_only)
                        
                        single_ticker_info[single_ticker] = (single_avg_return, single_avg_volatility)
            else:
                ticker = portfolio[0][0]
                df = yf.download(ticker, period="max", interval="1d", auto_adjust=False)
                daily_return = df['Adj Close'].pct_change().dropna()
                
                avg_return = get_annual_return(daily_return)
                avg_volatility = get_annual_volatility(daily_return, args.downward_only)
                
            start_year = daily_return.index.min().year + 1
            end_year = daily_return.index.max().year - 1
            
            if len(portfolio) > 1:
                rounded_ratios = [round(r * 10) for r in ratios]
                portfolio_name = "-".join(f"{ticker}{ratio}" for ticker, ratio in zip(tickers, rounded_ratios))
            else:
                portfolio_name = ticker
                
            analysed_info[portfolio_name] = (avg_return, avg_volatility)
            valid_years[portfolio_name] = (start_year, end_year)
            
        color_map = assign_color(list(analysed_info.keys()) + list(single_ticker_info.keys()))
        
        plt.figure(figsize=(10, 6))
        
        legend_handles = []
        
        for portfolio_name, (avg_return, avg_volatility) in analysed_info.items():
            color = color_map[portfolio_name]
            plt.scatter(avg_volatility * 100, avg_return * 100, s=500, color=color, alpha=0.6, edgecolors='black')
            
            start_year, end_year = valid_years[portfolio_name]
            legend_label = f"{portfolio_name} ({start_year} ~ {end_year})"
            legend_handles.append(Patch(facecolor=color, edgecolor='black', label=legend_label))
            
        for ticker_name, (avg_return, avg_volatility) in single_ticker_info.items():
            color = color_map[ticker_name]
            
            plt.scatter(avg_volatility * 100, avg_return * 100, s=500, color=color, alpha=0.6, edgecolors='black')
            plt.text(avg_volatility * 100, avg_return * 100, ticker_name, fontsize=8, ha='center', va='center', fontweight='bold')

        file_name = "-".join([ticker for ticker in args.tickers])
        if args.downward_only:
            file_name += "-downward_only"
            
        x_label = "Downside Volatility" if args.downward_only else "Volatility"
        
        plt.xlabel(f"{x_label} (%)")
        plt.ylabel("Average Annual Return (%)")
        plt.title(f"Average Return & {x_label}")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(handles=legend_handles, title="Portfolios",loc='lower right', bbox_to_anchor=(0.98, 0.02), fontsize=10)
        plt.savefig(f"{save_dir}/{file_name}.png")

    if args.analysis == "long_term_investment":
        assert len(args.tickers) == 1, "여러 종목으로 이루어진 포트폴리오에 대한 수익률을 원하는 경우는 README를 참고하여 하나의 string으로 작성 바랍니다."
        
        save_dir = f"{args.save_path}/long_term_investment/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        portfolio = parse_string_digit_pairs(args.tickers[0])
        
        if len(portfolio) > 1:
            tickers, ratios = zip(*portfolio)
            
            tickers = list(tickers)
            ratios = list(ratios)
            
            stock_info = get_multiple_stock_info(tickers)
            daily_return, _ = get_mixed_data(stock_info, ratios, None)
        else:
            ticker = portfolio[0][0]
            df = yf.download(ticker, period="max", interval="1d", auto_adjust=False)
            daily_return = df['Adj Close'].pct_change().dropna()
            
        start_date = str(daily_return.index.min().date())
        end_date = str(daily_return.index.max().date())
            
        invest_years = list(range(args.min_year, args.max_year+1, args.interval))
        if invest_years[-1] != args.max_year:
            invest_years.append(args.max_year)
            
        if len(portfolio) > 1:
            rounded_ratios = [round(r * 10) for r in ratios]
            file_name = "-".join(f"{ticker}{ratio}" for ticker, ratio in zip(tickers, rounded_ratios))
        else:
            file_name = ticker
            
        bin = None
            
        fig, axes = plt.subplots(nrows=len(invest_years), figsize=(10, len(invest_years) * 5))  # 개수만큼 세로 배치

        plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False
        
        fig.suptitle(f"Long-Term Investment of {file_name} ({start_date} ~ {end_date})", fontsize=16, fontweight='bold')
        
        for i, (ax, invest_year) in enumerate(zip(axes, invest_years)):
            sampled_returns = sample_random_returns(daily_return, invest_year, args.num_samples)
            
            if i == 0:
                bins = np.arange(min(sampled_returns) // 5 * 5, max(sampled_returns) // 5 * 5 + 6, 5) # 5% 단위로 수익률 계산

            counts, edges = np.histogram(sampled_returns, bins=bins)

            ax.bar(edges[:-1], counts, width=5, edgecolor="black", align="edge")
            ax.set_xlabel("Average Annual Return (%)")
            ax.set_ylabel("Num Samples")
            ax.set_title(f"Distribution of annual return of {invest_year}-year investment")
            ax.set_xticks(edges)
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # suptitle이 잘리지 않도록 여백 확보
        plt.savefig(f"{save_dir}/{file_name}.png")
        
    if args.analysis == "cummulative_return":
        assert len(args.tickers) == 1, "여러 종목으로 이루어진 포트폴리오에 대한 수익률을 원하는 경우는 README를 참고하여 하나의 string으로 작성 바랍니다."
        
        save_dir = f"{args.save_path}/cummulative_return/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        portfolio = parse_string_digit_pairs(args.tickers[0])
        cumulative_returns = []
        labels = []
        
        if len(portfolio) > 1:
            tickers, ratios = zip(*portfolio)
            
            tickers = list(tickers)
            ratios = list(ratios)
            
            rounded_ratios = [round(r * 10) for r in ratios]
            file_name = "-".join(f"{ticker}{ratio}" for ticker, ratio in zip(tickers, rounded_ratios))
            
            stock_info = get_multiple_stock_info(tickers)
            
            if args.start_year is not None:
                start_datetime = pd.to_datetime(f"{args.start_year}-01-01")
                for i in range(len(stock_info)):
                    stock_info[i] = stock_info[i][stock_info[i].index >= start_datetime]
                file_name += f"-from_{args.start_year}"
            
            for i, info in enumerate(stock_info):
                daily_return = info['Adj Close'].pct_change().dropna()
                cumulative_return = (1 + daily_return).cumprod() - 1
                cumulative_returns.append(cumulative_return * 100)
                labels.append(tickers[i])
            
            daily_return, _ = get_mixed_data(stock_info, ratios, None)
            cumulative_return = (1 + daily_return).cumprod() - 1
            cumulative_returns.append(cumulative_return * 100)
            labels.append(file_name)
        else:
            ticker = portfolio[0][0]
            df = yf.download(ticker, period="max", interval="1d", auto_adjust=False)
            
            file_name = ticker
            
            if args.start_year is not None:
                start_datetime = pd.to_datetime(f"{args.start_year}-01-01")
                df = df[df.index >= start_datetime]
                file_name += f"-from_{args.start_year}"
            
            daily_return = df['Adj Close'].pct_change().dropna()
            cumulative_return = (1 + daily_return).cumprod() - 1
            cumulative_returns.append(cumulative_return * 100)
            labels.append(ticker)
            
        color_map = assign_color(labels)
        start_date = str(cumulative_returns[0].index.min().date())
        end_date = str(cumulative_returns[0].index.max().date())
            
        plt.figure(figsize=(12, 6))

        for i, cumulative_return in enumerate(cumulative_returns):
            plt.plot(cumulative_return.index, cumulative_return, label=labels[i], color=color_map[labels[i]])

        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        plt.title(f"Cumulative Return ({start_date} ~ {end_date})")
        plt.xlabel("Time (Year)")
        plt.ylabel("Cumulative Return (%)")
        plt.legend()
        plt.grid(True)

        plt.savefig(f"{save_dir}/{file_name}.png")