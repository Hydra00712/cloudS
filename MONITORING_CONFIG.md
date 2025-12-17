# Azure Monitoring Configuration

## App Service Logging Enabled ✅

**Configuration**:
- Application Logging: Filesystem
- Level: Information
- Resource: engagement-app-demo
- Location: France Central

**Log Stream Evidence**:
```
2025-12-17T00:00:44 [INFO] Starting gunicorn 23.0.0
2025-12-17T00:00:44 [INFO] Listening at: http://0.0.0.0:8000 (2111)
2025-12-17T00:00:44 [INFO] Using worker: sync
2025-12-17T00:00:44 [INFO] Booting worker with pid: 2114
2025-12-17T00:00:45 "GET /robots933456.txt HTTP/1.1" 404 (Health Check)
2025-12-17T00:02:15 "GET / HTTP/1.1" 200 (Browser access)
2025-12-17T00:04:25 "GET / HTTP/1.1" 200 (API access)
```

**Status**: App Service running successfully, serving HTTP 200 responses

---

## Alert Scenario: HTTP 5xx Error Rate

**Alert Configuration** (to be implemented via Azure Monitor):

**Metric**: HTTP Server Errors (5xx)
**Condition**: Count > 10 in 5-minute window
**Severity**: Error (Sev 2)
**Action**: Email notification to admin

**Threshold Justification**:
- Baseline: < 1 error per hour in normal operation
- Alert triggers if sustained error rate indicates model/app failure
- Prevents silent degradation of service quality

**Implementation Command** (not executed - documentation only):
```bash
az monitor metrics alert create \
  --name "High-5xx-Error-Rate" \
  --resource-group rg-engagement-ml \
  --scopes /subscriptions/10ceef72.../resourceGroups/rg-engagement-ml/providers/Microsoft.Web/sites/engagement-app-demo \
  --condition "count Http5xx > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Alert when HTTP 5xx errors exceed 10 in 5 minutes"
```

**Expected Outcome**:
- Email alert sent when threshold breached
- Operations team investigates model loading errors, resource constraints, or code bugs

---

## Additional Monitoring Recommendations

### Application Insights (Future Enhancement)

**Metrics to Track**:
- Model prediction latency (p50, p95, p99)
- Prediction errors per bucket (Q1-Q5)
- Request throughput (requests/sec)
- Model loading time on cold start

**Custom Events**:
- `model_prediction` (logs each prediction with engagement_bucket)
- `blob_model_load` (logs successful model load from Azure Blob)
- `prediction_error` (logs MAE > 1.0 cases for investigation)

**Implementation**:
```python
from applicationinsights import TelemetryClient
tc = TelemetryClient('<instrumentation-key>')

# Log prediction
tc.track_event('model_prediction', {
    'bucket': bucket,
    'prediction': pred,
    'latency_ms': latency
})
```

### Log Analytics Queries

**Query 1: Request Volume by Hour**
```kusto
AppServiceHTTPLogs
| where TimeGenerated > ago(24h)
| summarize RequestCount = count() by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

**Query 2: Error Rate Trending**
```kusto
AppServiceHTTPLogs
| where TimeGenerated > ago(7d)
| summarize Errors = countif(ScStatus >= 500), Total = count() by bin(TimeGenerated, 1h)
| extend ErrorRate = (Errors * 100.0) / Total
| project TimeGenerated, ErrorRate
```

---

## Monitoring Evidence Summary

✅ Application Logging: Enabled (filesystem, info level)
✅ Log Stream: Verified (HTTP 200 responses observed)
✅ Alert Scenario: Documented (HTTP 5xx rate > 10 per 5min)
⏳ Application Insights: Recommended for production
⏳ Log Analytics: Queries prepared for KQL investigation

**Status**: CDDA Monitoring step complete with documented alert strategy
