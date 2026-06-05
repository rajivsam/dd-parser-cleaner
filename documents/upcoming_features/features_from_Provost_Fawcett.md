# 📈 Business-to-Mining Bridge: Features from Provost & Fawcett

## 🎯 Process Summary
We reviewed *Data Science for Business* by Foster Provost and Tom Fawcett. This review focused on the **CRISP-DM process**, the **decomposition of business problems**, and the **evaluation of data utility**. While Pyle focuses on the "shadow of objects," Provost and Fawcett focus on the "logic of the task."

We have integrated these principles to ensure our tool doesn't just "clean" data, but prepares it specifically for canonical data mining tasks.

---

## 🗂️ Feature Categorization

### Bucket 1: Modeling & Featurization (Future Tool)
*These items focus on the transition from a clean baseline to a predictive model.*

1.  **Supervised Task Identifier**: Help users define the "Target Variable" (Label) and determine if the problem is Classification or Regression.
2.  **Leakage Sentinel**: Identifying variables that contain "future" information (e.g., tax paid on a purchase that hasn't happened yet).
3.  **Similarity & Link Prediction**: Logic to suggest connections between data items (e.g., "People who bought X also bought Y").
4.  **Causal Logic Check**: Flagging the assumptions required when a user attempts to draw causal conclusions from observational data.

### Bucket 2: Cleaning & Diagnostics (Current Tool)
*These items focus on the "Data Understanding" and "Data Preparation" stages of the CRISP-DM cycle.*

1.  **Numeric Scaling/Normalization**: Detecting when numeric columns have wildly different scales that would distort similarity matching or distance-based algorithms.
2.  **Behavioral Profiling**: Establishing norms for specific attributes to facilitate anomaly detection (e.g., identifying fraud or system intrusions).
3.  **Record Matching (Entity Resolution)**: Identifying if multiple rows represent the same customer or business despite minor naming variations.
4.  **False Alarm Diagnostics**: Warning the user when a column's distribution suggests it might produce high false-positive rates in a laboratory evaluation.
5.  **Data Reliability Assay**: Part of "Data Understanding"—flagging when historical data collection methods might not align with current business needs.

---

## 🚀 Implementation Scope

*   **The Cleaner Tool**: Will implement **Bucket 2**, focusing on the "Data Understanding" and "Data Preparation" phases of the CRISP-DM cycle.
*   **The Featurization Tool**: Will implement **Bucket 1**, focusing on "Modeling" and the rigorous "Evaluation" of patterns.

---
*This document complements the Pyle Information Assay to provide a complete strategic roadmap for KMDS.*