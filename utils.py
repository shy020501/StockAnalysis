import itertools
import pandas as pd
import re

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


def parse_string_digit_pairs(s: str):
    """
    주어진 문자열이 {str}{digit}{string}{digit}... 형태인지 확인하고,
    올바른 형식이면 [(str, digit), (str, digit), ...] 형태로 변환하여 반환.
    
    Args:
        s (str): 패턴을 확인할 문자열
    """
    if s and s[0].isdigit():
        return [(s, None)]
    
    pattern = r'^([A-Za-z]+(?:\d+[A-Za-z]+)*\d*)$'
    
    if not re.fullmatch(pattern, s):
        return None  # 형식이 올바르지 않으면 None 반환
    
    matches = re.findall(r'([A-Za-z]+)(\d*)', s)
    parsed_result = [(text, float(num) / 10 if num else None) for text, num in matches]
    
    return parsed_result

def remove_first_last_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    주어진 DataFrame에서 첫 연도와 마지막 연도를 제거

    Args:
        df (pd.DataFrame): 수정할 DataFrame (DatetimeIndex가 설정된 DataFrame)
    """
    assert isinstance(df.index, pd.DatetimeIndex), "DataFrame의 index는 DatetimeIndex여야 합니다."
    
    df = df.sort_index()

    first_year = df.index[0].year  # 가장 첫 연도
    last_year = df.index[-1].year  # 가장 마지막 연도

    filtered_returns = df[(df.index.year != first_year) & (df.index.year != last_year)]

    return filtered_returns
