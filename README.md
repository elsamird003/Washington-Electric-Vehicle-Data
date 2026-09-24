# Washington EV registrations

Small pipeline that reads Washington State electric vehicle registrations, validates the file, and writes the top models as a table, chart, and quality metrics.

Source data: [Electric Vehicle Population Data](https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2) from data.wa.gov. Place the CSV at `asset/Data.csv`.

## Setup

```powershell
python -m venv myenv
myenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python index.py
```

Optional flags:

```powershell
python index.py --input asset/Data.csv --top-n 30 --output-dir outputs
```

Outputs:

- `outputs/top_models.csv` — ranked model counts
- `outputs/top_models.png` — horizontal bar chart
- `outputs/metrics.json` — row count, distinct models, null rate, top-N share

## Tests

```powershell
pytest
```

## Docker

```powershell
docker build -t ev-registrations .
docker run --rm -v ${PWD}/outputs:/app/outputs ev-registrations
```
