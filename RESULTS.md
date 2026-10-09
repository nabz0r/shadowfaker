# Measured results (2026-10-09)

The account-v1 response resolved `Hide on bush#KR1`. Match-v5 supplied 470 queue-420 KR IDs. Five were remakes; 465 matches yielded valid timelines and 12,510 one-minute supervised observations. The fixed seed-42 match split has 373 train, 46 validation, and 46 test matches. The account name and API response do not independently establish a person's identity.

The primary metric is exact next-region top-1 accuracy on a 16×16 grid. Scores below are **per observation**, with a paired match-level bootstrap interval for the difference from the strongest baseline. The role/phase prior is fitted on training matches only. All model and calibration choices use validation; the test set was first consulted before the later iterations, so its later scores are exploratory rather than a pristine final confirmatory result.

| Configuration | Validation region top-1 | Test region top-1 | Interpretation |
|---|---:|---:|---|
| Compact transformer, raw logits | 9.41% | 9.77% | First full run; test is below the most-frequent-region baseline. |
| Compact transformer + train-only role/phase prior | **10.59%** | 11.28% | Selected over the larger candidate on validation. |
| Wider transformer, 192 wide / 3 layers / LR 0.001, calibrated | 10.20% | Not evaluated | Lower validation score; early stopping at epoch 15. |
| Explicit spatial movement head, calibrated | 10.51% | Not evaluated | Lower validation score; early stopping at epoch 20. |

On the compact model's test split, the most frequent region reaches 11.28%, copying the current region 6.93%, staying at map center 8.94%, and the role/phase prior alone 11.61%. The model's top-5 region accuracy is 33.58%. Its gain over the best baseline is **−0.33 percentage points**, with a paired 95% bootstrap interval of **[−1.51, +0.87]** points. Mean grid distance is 4.37 cells for the model versus 3.99 for the frequent-region baseline and 3.97 for the role/phase prior. This does **not** meet the requested clear improvement for region prediction.

Validation-selected no-event bias calibration improved other heads on test: item accuracy 58.81% versus 55.30% for predicting no purchase, and skill accuracy 55.30% versus 47.03% for predicting no upgrade. Accuracy **when a purchase actually occurs** is only 10.09%, so the overall item gain mainly concerns event timing. The auxiliary outcome head's test Brier score is 0.2242 against 0.2505 for a constant training-win-rate forecast. It is an association with final outcome, not an estimate of the causal value of a decision.

The test set contains 82% mid-lane observations versus 65% in validation. This shift and the sparse 256-class target are plausible contributors to the region gap. They are diagnoses, not permission to redraw the test split or claim a win. See [PROGRESS.md](PROGRESS.md) for the full chronology and [SHADOW_PLUS.md](SHADOW_PLUS.md) for what would be needed to assess playing strength.

An exploratory train-only spatial transition table conditioned on current region, role and phase reached 10.75% on validation alone. A wide search of transition/model interpolation reached at most 10.82% on that same split, a three-sample difference from the selected compact model. This tiny, multiply searched gain was **not** promoted to a model result or checked on test. More independent games would be needed for a trustworthy selection.
