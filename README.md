# StockAnalysis
📊 Yahoo Finance 데이터 기반 주식/ETF 분석 및 시각화 스크립트

# Installation
```bash
conda create -n stock_analysis python=3.10
conda activate stock_analysis
pip install -r requirements.txt
```

# Run Analysis
⚠️ Tickers, abbrs 등 여러 종목을 입력할 시, 반드시 따옴표(" or ')로 감싸서 입력하세요.<br>
⚠️ 수행하고자 하는 분석 방식에 맞는 arguments들을 사용해주세요.
```bash
python main.py --analysis <분석 방법> --tickers <종목 코드> --save_dir <저장 위치> # 그 외 분석에 필요한 arguments
```

## Arguments

| Name             | Type        | Explanation                                                  | Required       | Example                 |
|------------------|-------------|--------------------------------------------------------------|----------------|-------------------------|
| `--analysis`     | `str`       | 사용할 분석 방식 ("Analysis methods" 참고)                    | True           | `avg_return_volatility` |
| `--tickers`      | `str`       | 분석할 종목 코드(들) (default: SCHD SPY QQQ)                  | False          | `"SCHD QQQ TLT"`        |
| `--save_dir`     | `str`       | 저장할 디렉토리 (default: output)                             | False          | `./output`              |

# Analysis Methods

## 1. Average return and volatility (Annual)
- 특정 종목 혹은 여러 종목들에 대해 (분산)투자하였을 때의 연평균 수익률과 연평균 변동률에 대해 계산
- `--analysis avg_return_volatility`
- 각 종목에 대응되는 알파벳을 `--abbrs`로 정의 (중복 X)
- 특정 종목이 들어간 조합(포트폴리오)만을 보고 싶으면 `--must_include` 사용
- 하락 변동성만 확인하고 싶을 때는 `--downward_only` 사용

### Arguments
| Name             | Type        | Explanation                                                  | Required       | Example                 |
|------------------|-------------|--------------------------------------------------------------|----------------|-------------------------|
| `--abbrs`        | `str`       | 각 종목 별 약자(들) (default: S P Q)                          | True           | `"S Q T"`               |
| `--must_include` | `str`       | 조합에 반드시 포함할 종목. None이면 모든 종목. (default: None)  | False          | `"S T"`                 |
| `--downward_only`| `bool`      | 하락 변동률만 계산할지 여부 (default: False)                   | False          | `--downward_only`       |

### Example
```bash
python main.py --analysis "avg_return_volatility" --tickers "SCHD QQQ TLT" --abbrs "S Q T" --downward_only --save_dir "./output"
```

### Output
<img src="./output/avg_return_volatility/SCHD-QQQ-TLT-downward_only.png" alt="ETF Graph" width="500">