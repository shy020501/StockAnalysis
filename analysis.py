import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import remove_first_last_year

def get_annual_return(daily_returns: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    일 별 수익률을 받아, 연 평균 수익률 반환
    
    Args:
        daily_return (pd.DataFrame): 일 별 수익률
    """
    assert daily_returns.shape[1] == 1, "DataFrame에는 하나의 컬럼(수익률)만 존재해야 합니다."
    
    daily_returns = remove_first_last_year(daily_returns)
    
    returns = daily_returns.iloc[:, 0]
    index_dates = daily_returns.index
    
    total_return = np.prod(1 + returns) - 1

    start_year = index_dates.min().year
    end_year = index_dates.max().year
    num_years = end_year - start_year + 1
    
    annualized_return = (1 + total_return) ** (1 / num_years) - 1

    return annualized_return

def get_annual_volatility(daily_returns: pd.DataFrame, downward_only: bool = True) -> tuple[pd.DataFrame, float]:
    """
    일 별 수익률을 받아, 연간 변동성 반환
    
    Args:
        daily_return (pd.DataFrame): 일 별 수익률
        downward_only (bool): 하락 구간만 계산할지 여부
    """
    assert daily_returns.shape[1] == 1, "DataFrame에는 하나의 컬럼(수익률)만 존재해야 합니다."
    
    daily_returns = remove_first_last_year(daily_returns)
    
    returns = daily_returns.iloc[:, 0]
    index_dates = daily_returns.index

    volatility_data = {}

    for year in sorted(index_dates.year.unique()):
        yearly_returns = returns[index_dates.year == year]

        # downward_only일 경우, 하락 구간(음수 수익률)만 선택
        selected_returns = yearly_returns[yearly_returns < 0] if downward_only else yearly_returns
        
        # σ_annual = σ_daily × √252 => 252는 연간 거래일 수 
        volatility = selected_returns.std() * np.sqrt(252) if not selected_returns.empty else np.nan
        volatility_data[year] = volatility

    result_df = pd.DataFrame(volatility_data.items(), columns=['Year', 'Volatility']).dropna()

    return result_df['Volatility'].mean()

def get_mixed_data(stock_info: list[pd.DataFrame], ratio: list[float], abbrs: list[str] = None) -> tuple[pd.DataFrame, str]:
    """
    여러 개의 주식을 특정 비율에 따라 투자했을 때의 일 별 수익률을 반환
    
    Args:
        tickers (list[pd.DataFrame]): 합칠 종목 정보
        ratio (list[float]): 합칠 비율 (소수점)
        abbrs (list[str]): 각 종목을 대표할 알파벳 1개
    """
    assert abs(sum(ratio) - 1) < 1e-6, "Ratio의 합은 1이어야 합니다."
    
    # 합친 종목 코드 생성 (e.g. S8Q2)
    rounded_ratios = [round(r * 10) for r in ratio]
    
    combined_ticker = "".join(f"{abbr}{r}" for abbr, r in zip(abbrs, rounded_ratios)) if abbrs is not None else None
        
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

    return filtered_data_list

def sample_random_returns(daily_return: pd.DataFrame, invest_year: int, sample_num: int) -> list[float]:
    """
    주어진 일일 수익률 데이터에서 invest_year년 동안의 구간을 무작위로 sample_num개 샘플링하여,
    각 구간에서 invest_year년 동안 일적립식 투자를 하였을 때 연 평균 수익률을 계산 후 반환
    
    Args:
        daily_return (pd.DataFrame): 주식/포트폴리오의 일일 수익률
        invest_year (int): 투자할 연수
        sample_num (int): 샘플링할 구간의 개수
    """
    available_dates = daily_return.index.sort_values()
    
    # 샘플 가능한 시작 지점
    latest_start_date = available_dates[-1] - pd.DateOffset(years=invest_year)
    valid_start_dates = available_dates[available_dates <= latest_start_date]
    
    if len(valid_start_dates) == 0:
        raise ValueError(f"투자 기간({invest_year}년)에 해당하는 충분한 데이터가 없습니다.")
    
    sampled_start_dates = np.random.choice(valid_start_dates, size=sample_num, replace=False)
    sampled_returns = []
    
    for start_date in sampled_start_dates:
        target_date = start_date + pd.DateOffset(years=invest_year)
        future_dates = available_dates[available_dates >= target_date] # target_date가 실제 존재하지 않으면, 가장 가까운 다음 거래일 찾기
        
        # 해당 기간 이후 데이터가 없으면 스킵
        if len(future_dates) == 0:
            continue
        
        actual_end_date = future_dates[0]
        invest_period = daily_return.loc[start_date:actual_end_date]
        
        cumulative_earning = (1 + invest_period).cumprod().iloc[-1]
        annualized_return = float(cumulative_earning.iloc[0]) ** (1 / invest_year) - 1
        sampled_returns.append(annualized_return * 100)
    
    return sampled_returns