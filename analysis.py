import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_annual_return(daily_returns: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    일 별 수익률을 받아, 연간 수익률 반환
    
    Args:
        daily_return (pd.DataFrame): 일 별 수익률
    """
    assert daily_returns.shape[1] == 1, "DataFrame에는 하나의 컬럼(수익률)만 존재해야 합니다."
    
    returns = daily_returns.iloc[:, 0]
    index_dates = daily_returns.index
    
    annual_data = {}

    for year in sorted(index_dates.year.unique()):
        yearly_returns = returns[index_dates.year == year] # 연도 별로 계산

        # 연간 수익률 = ∏(1 + r_daily) - 1
        annual_return = np.prod(1 + yearly_returns) - 1  
        annual_data[year] = annual_return

    # DataFrame 변환
    result_df = pd.DataFrame(annual_data.items(), columns=['Year', 'Return']).dropna()

    return result_df, result_df['Return'].mean()

def get_annual_volatility(daily_returns: pd.DataFrame, downward_only: bool = True) -> tuple[pd.DataFrame, float]:
    """
    일 별 수익률을 받아, 연간 변동성 반환
    
    Args:
        daily_return (pd.DataFrame): 일 별 수익률
        downward_only (bool): 하락 구간만 계산할지 여부
    """
    assert daily_returns.shape[1] == 1, "DataFrame에는 하나의 컬럼(수익률)만 존재해야 합니다."
    
    returns = daily_returns.iloc[:, 0]
    index_dates = daily_returns.index

    volatility_data = {}

    for year in sorted(index_dates.year.unique()):
        yearly_returns = returns[index_dates.year == year]

        # downward_only일 경우, 하락 구간(음수 수익률)만 선택
        selected_returns = yearly_returns[yearly_returns < 0] if downward_only else yearly_returns
        
        # σ_annual = σ_daily × √거래일
        volatility = selected_returns.std() * np.sqrt(len(selected_returns)) if not selected_returns.empty else np.nan
        volatility_data[year] = volatility

    # DataFrame 변환
    result_df = pd.DataFrame(volatility_data.items(), columns=['Year', 'Volatility']).dropna()

    return result_df, result_df['Volatility'].mean()

def get_mixed_data(stock_info: list[pd.DataFrame], abbrs: list[str], ratio: list[float]) -> tuple[pd.DataFrame, str]:
    """
    여러 개의 주식을 특정 비율에 따라 투자했을 때의 일 별 수익률을 반환
    
    Args:
        tickers (list[pd.DataFrame]): 합칠 종목 정보
        abbrs (list[str]): 각 종목을 대표할 알파벳 1개
        ratio (list[float]): 합칠 비율 (소수점)
    """
    assert abs(sum(ratio) - 1) < 1e-6, "Ratio의 합은 1이어야 합니다."
    
    # 합친 종목 코드 생성 (e.g. S8Q2)
    rounded_ratios = [round(r * 10) for r in ratio]
    combined_ticker = "".join(f"{abbr}{r}" for abbr, r in zip(abbrs, rounded_ratios))
        
    combined_df = pd.concat(stock_info, axis=1, join='inner') # 가장 최근에 만들어진 종목에 맞춰서 데이터 사용
    daily_return = combined_df['Adj Close'].pct_change().dropna() # 각 종복에 대해서 일 별 수익률 사용

    weighted_return = (daily_return @ ratio).to_frame(name=combined_ticker) # 투자 비율에 맞춰 일 별 총 수익률 계산
    
    return weighted_return, combined_ticker

def get_multiple_stock_info(tickers: list[str]) -> list[pd.DataFrame]:
    """
    여러 종목 번호를 받아 Yahoo Finance에서 데이터 수집 후, 
    가장 최근에 상장된 주식의 시작 날짜 이후의 데이터만 반환
    
    Args:
        tickers (list[str]): 불러올 종목 번호
    """
    data_list = []
    start_dates = []
    
    for ticker in tickers:
        df = yf.download(ticker, period="max", interval="1d", auto_adjust=False)
        if not df.empty:
            start_dates.append(df.index.min())  # 첫 데이터 날짜
            data_list.append(df)
            
    if not start_dates:
        return data_list
    
    latest_start_date = max(start_dates)
    filtered_data_list = [df[df.index >= latest_start_date] for df in data_list]

    return filtered_data_list, latest_start_date.date()