# Test Report
## Project: Public Transport Ridership Analytics

### 1. Objective
To verify the dataset, association-rule mining pipeline, backend API, and dashboard date filters.

### 2. Dataset Validation

| Test | Expected Result | Observed Result | Status |
|---|---|---|---|
| Source dataset loading | Dataset loads successfully | 1,048,575 records loaded | PASS |
| Card number validation | Check missing values | 0 missing card numbers | PASS |
| Duplicate card validation | Check duplicate card numbers | 0 duplicate card records | PASS |
| Bus service count | Count distinct services | 9 services | PASS |
| Boarding stop count | Count distinct boarding stops | 316 stops | PASS |

### 3. Association Rule Mining

| Test | Observed Result | Status |
|---|---|---|
| Frequent itemset generation | 1,106 itemsets | PASS |
| Association rule generation | 1,228 rules | PASS |
| Confidence filtering | Minimum confidence 0.60 | PASS |
| Reproducibility | Random sample seed set to 42 | PASS |

Note: Association rules are mined from a sample of up to 50,000 records to manage memory usage.

### 4. Backend API Testing

| Test | Expected Result | Observed Result | Status |
|---|---|---|---|
| Dashboard API | HTTP 200 response | HTTP 200 | PASS |
| Monthly date filter | Return February 2018 data | 1,048,575 rides | PASS |
| Weekly date filter | Return filtered date data | 249,187 rides | PASS |
| Association rules endpoint data | Return available rules | 200 rules returned by dashboard API | PASS |

### 5. Dashboard Testing
- Dashboard opens at the local frontend URL.
- Summary metrics and charts are displayed.
- Date filters update the displayed data.
- Association-rule results are displayed in the interface.

### 6. Limitations
- The association-rule mining process uses a sample of up to 50,000 source records rather than the entire dataset.
- The dashboard API currently returns a maximum of 200 association rules.
- Results depend on the selected support and confidence thresholds.

### 7. Conclusion
The source dataset, association-rule mining pipeline, backend API, and dashboard date filters were tested successfully based on the recorded test outputs.
