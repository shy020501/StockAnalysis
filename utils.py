import itertools
import pandas as pd

COLORS = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "magenta", "brown", "pink"]

def stock_combination(stock_info: list[pd.DataFrame], abbrs: list[str], r: int = 2, must_include: list[str] = None) -> tuple[list, list]:
    """
    주어진 주식 정보와 이에 상응하는 약자에 대해서 r개의 원소로 이루어지는 조합을 생성
    
    Args:
        stock_info (list[pd.DataFrame]): 조합을 만들 주식 정보
        abbr (list[str]): 주식 별 대표 알파벳
        r (int): 선택할 원소의 개수
        must_include (list[str]) 반드시 포함돼야 하는 주식의 대표 알파벳
    """
    
    combinations = list(itertools.combinations(range(len(abbrs)), r))
    paired_stock_info = [(stock_info[i], stock_info[j]) for i, j in combinations]
    paired_abbrs = [(abbrs[i], abbrs[j]) for i, j in combinations]
    
    if must_include is not None:
        filtered_pairs = [(s, a) for s, a in zip(paired_stock_info, paired_abbrs) if set(must_include) & set(a)]

        paired_stock_info, paired_abbrs = zip(*filtered_pairs) if filtered_pairs else ([], [])

    return list(paired_stock_info), list(paired_abbrs)

def simplify_ticker(ticker: str) -> str:
    """
    Ticker를 받아 숫자를 제거 (e.g. S8Q2 -> SQ)
    
    Args:
        ticker (str): 특정 혹은 혼합 종목에 대한 ticker
    """
    return ''.join([char for char in ticker if not char.isdigit()])

def assign_color(tickers: list[str]) -> dict:
    """
    Ticker들을 받아 각각에 대해 색깔 부여
    
    Args:
        tickers (str): 색깔을 부여할 ticker들 list
    """
    color_cycle = itertools.cycle(COLORS)
    color_map = {ticker: next(color_cycle) for ticker in tickers}
    
    return color_map


