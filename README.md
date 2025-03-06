# StockAnalysis
📊 Yahoo Finance 데이터 기반 주식/ETF 분석 및 시각화 스크립트

# Installation
```bash
conda create -n stock_analysis python=3.10
conda activate stock_analysis
pip install -r requirements.txt
```

# Run Analysis
⚠️ Tickers, abbrs(abbreviations), must_include에 여러 종목을 넣을 시, 반드시 따옴표(" or ')로 감싸서 입력하세요.<br>
⚠️ Tickers와 abbrs의 수는 반드시 동일해야 합니다.
```bash
python main.py --analysis <분석 방법> --tickers <종목 코드> --abbrs <종복 별 대표 알파벳> --must_include <조합에 반드시 포함할 종목> --downward_only --save_dir <저장 위치>
```

## Arguments

| Name             | Type        | Explanation                                                  | Required       | Example                 |
|------------------|-------------|--------------------------------------------------------------|----------------|-------------------------|
| `--analysis`     | `str`       | 사용할 분석 방식 ("Analysis methods" 참고)                    | True           | `avg_return_volatility` |
| `--tickers`      | `str`       | 분석할 종목 코드(들) (default: SCHD SPY QQQ)                  | False          | `"SCHD QQQ TLT"`        |
| `--abbrs`        | `str`       | 각 종목 별 약자(들) (default: S P Q)                          | False          | `"S Q T"`               |
| `--must_include` | `str`       | 조합에 반드시 포함할 종목. None이면 모든 종목. (default: None)  | False          | `"S T"`                 |
| `--downward_only`| `bool`      | 특정 분석에서 하락 계산만 진행할지 여부 (default: False)        | False          | `--downward_only`       |
| `--save_dir`     | `str`       | 저장할 디렉토리 (default: output)                             | False          | `output`                |

# Analysis Methods

## 1. Average return and volatility (Annual)
- 특정 종목 혹은 여러 종목들에 대해 분산투자하였을 때의 연평균 수익률과 연평균 변동률에 대해 계산
- `--analysis avg_return_volatility` 사용
- 하락 변동성만 확인하고 싶을 때는 `--downward_only` 사용
- 특정 종목이 들어간 조합(포트폴리오)만을 보고 싶으면 `--must_include` 사용

### Example
```bash
python main.py --analysis "avg_return_volatility" --tickers "SCHD QQQ TLT" --abbrs "S Q T" --downward_only --save_dir "./output"
```

### Output
<img src="./output/avg_return_volatility/SCHD-QQQ-TLT-downward_only.png" alt="ETF Graph" width="500">