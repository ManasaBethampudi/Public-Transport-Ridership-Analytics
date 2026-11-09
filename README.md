# Public Transport Ridership Analytics

## Project Overview

Public Transport Ridership Analytics is a data analytics project that examines bus ridership records to understand travel patterns, bus service usage, boarding and alighting locations, and relationships between travel-related attributes. It combines Python-based data processing, association-rule mining, a FastAPI backend, and a React dashboard.

## Objectives

- Analyze public transport ride records and summarize ridership.
- Identify frequently occurring combinations of travel attributes.
- Generate association rules using the Apriori algorithm.
- Visualize daily ridership, bus services, travel modes, card types, and stops.
- Provide an interactive dashboard with date filters.

## Technology Stack

- **Language:** Python, JavaScript
- **Data processing:** Pandas, NumPy
- **Association-rule mining:** MLxtend, Apriori
- **Backend:** FastAPI, Uvicorn
- **Frontend:** React, Vite
- **Visualization:** Recharts
- **Data format:** CSV

## Dataset

The main dataset is `data/BUS_DATA_FEB_2018.csv`, containing 1,048,575 records for February 2018 and 13 columns.

Important fields include card type, travel mode, bus service number, direction, boarding stop, alighting stop, ride start date and time, and ride end date and time.

The association-rule mining script uses a reproducible random sample of up to 50,000 records from the original dataset to control memory usage. The generated mining results therefore describe this sample, not necessarily the entire dataset.

## Main Features

- Ridership summary metrics
- Daily ridership analysis
- Top boarding and alighting stops
- Travel-mode and card-type analysis
- Bus-service comparisons
- Apriori frequent-itemset mining
- Association rules with support, confidence, and lift
- Date-range filtering
- React dashboard connected to a FastAPI API

## Project Structure

```text
Public_Transport_Ridership_Analytics/
├── backend/
│   └── main.py
├── data/
│   ├── BUS_DATA_FEB_2018.csv
│   ├── cleaned_ridership_data.csv
│   └── ridership_data.csv
├── frontend/
│   └── src/
├── results/
│   ├── association_rules.csv
│   ├── frequent_itemsets.csv
│   └── other analysis CSV files
├── src/
│   └── association_rules.py
├── README.md
└── requirements.txt
```

## Installation and Setup

### 1. Install Python dependencies

From the project root, run:

```powershell
python -m pip install pandas numpy mlxtend fastapi "uvicorn[standard]"
```

### 2. Generate association rules

Run this from the project root:

```powershell
python src\association_rules.py
```

The script saves frequent itemsets and association rules in the `results` directory.

### 3. Start the backend

Open a terminal:

```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

Backend API documentation is available at:

`http://127.0.0.1:8000/docs`

### 4. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173`

Keep both the backend and frontend running while using the dashboard.

## API Endpoints

- `GET /` — backend information
- `GET /api/health` — backend and dataset health
- `GET /api/dashboard` — dashboard summary, charts, and association rules
- `GET /api/association-rules` — association-rule results

The dashboard endpoint accepts `start_date` and `end_date` query parameters.

## Association-Rule Metrics

- **Support:** Proportion of sampled transactions containing the item combination.
- **Confidence:** Proportion of transactions containing the antecedent that also contain the consequent.
- **Lift:** Strength of the association relative to the consequent's overall frequency.

Association indicates a pattern, not a causal relationship.

## Initial Testing Results

- Original dataset loaded: 1,048,575 records.
- Card number validation: 1,048,575 distinct values and no missing card numbers.
- Frequent itemsets generated: 1,106.
- Association rules generated: 1,228.
- Dashboard API returned summary metrics and 200 rules in the tested response.

These results reflect the current implementation and the sampled mining workflow. Additional validation of date filters, chart values, and association-rule interpretations is recommended before final submission.

## Limitations

- Association rules are generated from a sample of up to 50,000 records.
- Results may change if the sampling method or mining thresholds change.
- Card-number uniqueness should be interpreted according to the source dataset's data definition.
- Association rules do not establish cause and effect.
- The current dataset covers February 2018 only.

## Future Enhancements

- Evaluate association rules against larger samples and alternative support thresholds.
- Add route-level demand forecasting.
- Improve validation and error handling.
- Add downloadable filtered reports.
- Extend analysis to additional months of ridership data.

## Conclusion

The project demonstrates an end-to-end public transport analytics workflow using Python, association-rule mining, FastAPI, and React. It transforms ride records into summary statistics, visualizations, and discoverable travel-pattern associations through an interactive dashboard.
