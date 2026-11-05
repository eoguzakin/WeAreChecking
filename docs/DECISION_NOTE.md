# Decision note — first draft

**Date:** 5 November 2026
**Status:** ongoing development

We built an auditable historical forecasting workflow before attempting a live service. The immediate question was whether a learned post-qualifying race ranking improves on qualifying order alone.

The simple Bahrain 2024 example runs end to end: data snapshot → allowlisted inputs → saved ranking → race-label evaluation. It produces position MAE 2.3 and Spearman 0.886, but a single race cannot establish generalization.

The broader experiment trains on 2022–2023, selects among three models on 2024 and evaluates a frozen model on 2025. Ridge alpha 100 is the selected trained candidate. Its 2025 position MAE is 3.338, compared with 3.324 for qualifying order. The paired difference interval spans zero. We therefore retain qualifying order as the default and describe the trained model as experimental.

The weekend engine demonstrates sequential updates for remaining sessions. Its fixed weights, practice timing proxy and replay roster assumptions have not been validated as predictive improvements. Reviewed driver events support identity changes and provenance, while automatic news collection remains future work.

The next justified investment is better pre-race information: penalty-aware grid positions, clean session-specific pace features, forecast weather and circuit characteristics. We also need verified entry availability, event correction handling and a new untouched holdout before making stronger accuracy claims.

The project is ready as a runnable first draft and portfolio development repository. It is not ready to claim production reliability, live forecasting or superior predictive performance.
