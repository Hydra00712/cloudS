# 9️⃣ MONITORING & ALERTING STRATEGY

## Overview

```
Azure ML Endpoint / Function
    ↓ (sends metrics)
Application Insights
    ↓
Azure Monitor Dashboard
    ↓
Alerts Triggered
    ↓
Email / Webhook
```

## Metrics to Track

### 1. Inference Latency
- **Metric:** Time to generate prediction
- **Good:** < 200ms
- **Warning:** 200-500ms
- **Alert:** > 500ms

### 2. Error Rate
- **Metric:** % of failed predictions
- **Good:** < 1%
- **Warning:** 1-5%
- **Alert:** > 5%

### 3. Model Drift
- **Metric:** Change in prediction distribution
- **Concern:** If avg engagement rate deviates from training distribution

### 4. Resource Utilization
- **Metric:** CPU, Memory, Disk on compute cluster
- **Alert:** > 80% utilization

### 5. Data Quality
- **Metric:** Missing values, outliers in input
- **Alert:** Unexpected null values

## Implementation Files

### File: `monitoring.py` (Instrumentation)

```python
"""Application Insights monitoring for engagement model"""

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics, trace
import time
import logging

# === CONFIGURE AZURE MONITOR ===
configure_azure_monitor(
    connection_string="InstrumentationKey={KEY}"
)

logger = logging.getLogger(__name__)
meter = metrics.get_meter(__name__)
tracer = trace.get_tracer(__name__)

# === CREATE CUSTOM METRICS ===
prediction_latency = meter.create_histogram(
    name="prediction_latency_ms",
    description="Latency of inference in milliseconds",
    unit="ms"
)

prediction_counter = meter.create_counter(
    name="predictions_total",
    description="Total number of predictions",
    unit="1"
)

error_counter = meter.create_counter(
    name="prediction_errors",
    description="Number of failed predictions",
    unit="1"
)

engagement_rate_histogram = meter.create_histogram(
    name="engagement_rate_distribution",
    description="Distribution of predicted engagement rates",
    unit="1"
)


def monitor_prediction(features_dict, predicted_engagement_rate, error=None):
    """
    Log prediction metrics to Application Insights
    
    Args:
        features_dict: Input features
        predicted_engagement_rate: Model output (0-1)
        error: Exception if prediction failed
    """
    
    with tracer.start_as_current_span("predict") as span:
        start_time = time.time()
        
        # === LOG CUSTOM PROPERTIES ===
        span.set_attribute("platform", features_dict.get("platform"))
        span.set_attribute("topic_category", features_dict.get("topic_category"))
        span.set_attribute("engagement_level", 
            "HIGH" if predicted_engagement_rate > 0.6 else 
            "MODERATE" if predicted_engagement_rate > 0.3 else "LOW"
        )
        
        # === RECORD METRICS ===
        latency_ms = (time.time() - start_time) * 1000
        prediction_latency.record(latency_ms)
        prediction_counter.add(1)
        
        if error:
            error_counter.add(1)
            logger.error(f"❌ Prediction failed: {error}")
            span.set_attribute("error", str(error))
        else:
            engagement_rate_histogram.record(predicted_engagement_rate)
            logger.info(f"✅ Latency: {latency_ms:.2f}ms, Engagement: {predicted_engagement_rate:.2f}")


def check_data_quality(features_dict):
    """
    Validate input features for anomalies
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    
    # Check for None values
    if any(v is None for v in features_dict.values()):
        logger.warning("⚠️ Null values detected in input")
        return False
    
    # Check sentiment bounds
    if not (-1 <= features_dict.get("sentiment_score", 0) <= 1):
        logger.warning("⚠️ Sentiment out of bounds")
        return False
    
    # Check toxicity bounds
    if not (0 <= features_dict.get("toxicity_score", 0) <= 1):
        logger.warning("⚠️ Toxicity out of bounds")
        return False
    
    return True
```

### File: `alerts_config.json` (Alert Rules)

```json
{
  "alerts": [
    {
      "name": "High Latency Alert",
      "metric": "prediction_latency_ms",
      "threshold": 500,
      "operator": "GreaterThan",
      "aggregation": "Average",
      "window": "5m",
      "severity": 2,
      "action": "email"
    },
    {
      "name": "High Error Rate",
      "metric": "prediction_errors",
      "threshold": 0.05,
      "operator": "GreaterThan",
      "aggregation": "Average",
      "window": "10m",
      "severity": 1,
      "action": "email"
    },
    {
      "name": "Model Accuracy Drift",
      "metric": "engagement_rate_distribution",
      "threshold": 0.15,
      "operator": "GreaterThan",
      "window": "24h",
      "severity": 2,
      "action": "email"
    }
  ]
}
```

### File: Azure Monitor Dashboard (via Portal)

Create via Azure Portal:

1. **Azure Portal** → **Monitor** → **Dashboards**
2. **Create Dashboard**
3. Add charts:

```
┌──────────────────────────────────────────────────────────┐
│        ENGAGEMENT ML MODEL - MONITORING DASHBOARD        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐        │
│  │ Prediction Latency  │  │  Error Rate (%)     │        │
│  │ ░░░░░░░░░░░░░░░░░ │  │ ░░░░░░░░░░░░░░░░░ │        │
│  │ Avg: 145ms          │  │ Avg: 0.8%           │        │
│  │ Max: 421ms          │  │ Max: 2.3%           │        │
│  │ ✅ Within SLA       │  │ ✅ Acceptable       │        │
│  └─────────────────────┘  └─────────────────────┘        │
│                                                           │
│  ┌───────────────────────────────────────────────┐       │
│  │ Predictions per Hour                          │       │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 1,245     │       │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 1,100              │       │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 980                        │       │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 756                            │       │
│  │ ▓▓▓▓▓▓▓▓▓▓ 512                                 │       │
│  │ 12pm  1pm  2pm  3pm  4pm                       │       │
│  └───────────────────────────────────────────────┘       │
│                                                           │
│  ┌───────────────────────────────────────────────┐       │
│  │ Engagement Level Distribution                 │       │
│  │ 🔴 LOW:      45%  ███████████████████         │       │
│  │ 🟡 MODERATE: 35%  █████████████               │       │
│  │ 🟢 HIGH:     20%  ████████                    │       │
│  └───────────────────────────────────────────────┘       │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Resource Utilization                             │    │
│  │ CPU:      ▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░ 25%      │    │
│  │ Memory:   ▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░ 35%      │    │
│  │ Disk:     ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░  5%      │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Alert Scenario Examples

### Scenario 1: Latency Spike

**What happens:**
- Prediction latency exceeds 500ms for 5 minutes
- Alert rule triggers

**Cause:** High CPU usage on compute cluster

**Action:**
- Email sent to ops team
- Auto-scale compute (if configured)
- Check Application Insights logs
- Scale up if needed

### Scenario 2: Error Rate High

**What happens:**
- 5% of predictions fail within 10 minutes
- Alert triggers

**Cause:** Database connection timeout / Model endpoint down

**Action:**
- Health check endpoint status
- Restart function app
- Check SQL database connectivity
- Review logs for specific errors

### Scenario 3: Model Drift

**What happens:**
- Engagement rate distribution changes significantly
- 24-hour alert window

**Cause:** Data distribution changed / Model performance degraded

**Action:**
- Investigate new data characteristics
- Review recent feature changes
- Trigger retraining if needed
- Check for data quality issues

## Log Analytics Queries (KQL)

### Query 1: Latency Percentiles

```kusto
customMetrics
| where name == "prediction_latency_ms"
| summarize 
    p50=percentile(value, 50),
    p95=percentile(value, 95),
    p99=percentile(value, 99)
    by bin(timestamp, 1h)
| render timechart
```

### Query 2: Error Rate by Platform

```kusto
customEvents
| where name == "prediction_error"
| extend Platform = tostring(customDimensions["platform"])
| summarize ErrorCount=count() by Platform
| join (
    customEvents
    | where name == "prediction_success"
    | extend Platform = tostring(customDimensions["platform"])
    | summarize SuccessCount=count() by Platform
) on Platform
| extend ErrorRate = (ErrorCount / (ErrorCount + SuccessCount)) * 100
| render barchart
```

### Query 3: Prediction Volume Trend

```kusto
customMetrics
| where name == "predictions_total"
| summarize PredictionCount=sum(value) by bin(timestamp, 30m)
| render timechart
```

## Setting Up Alerts via Azure Portal

1. **Azure Portal** → **Monitor** → **Alerts**
2. **Create Alert Rule**
3. Configure:
   - **Resource:** engagement-endpoint / function-app
   - **Condition:** prediction_latency_ms > 500
   - **Action Group:** Email ops@company.com
4. **Create Alert Rule**

## Notification Methods

| Method | Setup | Cost |
|---|---|---|
| **Email** | Action Group | Free |
| **SMS** | Action Group + Twilio | ~$0.01/msg |
| **Webhook** | Custom action | Free |
| **Logic App** | Azure Logic Apps | ~$0.50-2/mo |
| **Teams** | Teams connector | Free |

Recommended for academic: **Email** (simplest, free)

