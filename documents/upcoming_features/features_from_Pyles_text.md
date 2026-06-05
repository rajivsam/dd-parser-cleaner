# 📖 Information Assay: Features from Dorian Pyle's Methodology

## 🎯 Process Summary
We performed a comprehensive review of Dorian Pyle’s *Data Preparation for Data Mining*. Rather than treating data as a static table, Pyle views data as a "shadow" of real-world objects. Our goal was to extract features that move our tooling from simple technical "janitor work" to a high-fidelity **Information Assay**. 

We focused specifically on **process-based recommendations**, **missing value patterns**, and **series behavior**. Features that involve advanced mathematical mining were set aside to maintain our commitment to domain agnosticism, while features that highlight "mineability" were prioritized.

---

## 🗂️ Feature Categorization

The findings from the review are split into two distinct buckets based on their role in the data lifecycle.

### Bucket 1: Modeling & Featurization (Future Tool)
*These features focus on preparing data for machine learning models. They will be implemented in the upcoming **Featurization Tool**.*

1.  **Future Leakage Check**: Identifying "anachronisms"—data columns that contain information that would not actually be known at the time a prediction is made.
2.  **Missing Data Signatures**: Instead of just filling in a gap, we create a "fingerprint" or hidden marker that tells the model exactly which values were missing, as the absence of data is often a signal itself.
3.  **Dataset Readiness Grade**: A high-level "Mineability Score" that helps a user decide if the data has enough signal to be used for complex math or if it is too noisy to trust.
4.  **Information Shadow Analysis**: A framework for checking if the data accurately represents the real-world objects it is meant to describe.

### Bucket 2: Cleaning & Diagnostics (Current Tool)
*These features focus on data health and structural integrity. They will be integrated directly into the **Cleaner** diagnostic suite.*

1.  **Checking for Sequence IDs**: Detecting numeric columns that are just row counters or auto-incrementing IDs. These look like data trends to a computer but have no actual predictive value and should be dropped.
2.  **Unique Value Plateau**: Spotting "Ghost" categories (like unique street addresses or long text strings). If new values never stop appearing as we read the file, the column is usually noise rather than a useful category.
3.  **Grouped Missing Data**: Looking for "Co-occurrence," where gaps in one column always happen alongside gaps in another. This reveals structural problems in how the data was gathered.
4.  **Data Personality**: Automatically figuring out if the data is "Physical" (stable and precise, like machine sensors) or "Behavioral" (messy and sparse, like human shopping habits) to suggest the best way to handle missing values.
5.  **Smart Quality Scanning**: A method for reading just enough of a large file to get an accurate health report, allowing the tool to process multi-gigabyte files in seconds instead of minutes.

---

## 🚀 Implementation Scope

*   **The Cleaner Tool**: Will focus on **Bucket 2**. Its mission is to produce a "Clean Baseline" by identifying junk data, detecting the "personality" of the set, and highlighting structural gaps.
*   **The Featurization Tool**: Will focus on **Bucket 1**. Its mission is to transform that clean baseline into the high-performance inputs required for advanced modeling.

---
*This document serves as the strategic roadmap for incorporating Information Theory into the KMDS ecosystem.*