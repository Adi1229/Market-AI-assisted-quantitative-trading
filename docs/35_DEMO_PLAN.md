# 35 — Demo Plan

| Field | Value |
|---|---|
| **Document ID** | DEMO-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [MVP Scope](./03_MVP_SCOPE.md), [Acceptance Criteria](./34_ACCEPTANCE_CRITERIA.md) |

---

## 1. Demo Objectives

Demonstrate the MVP platform's core capabilities to stakeholders, specifically highlighting the decoupled architecture between Decision and Execution.

---

## 2. Demo Scenarios

### Scenario 1: Strategy Studio & Backtesting
| Step | Action | Expected Outcome |
|---|---|---|
| 1 | Show Strategy Studio | List of registered strategies and status |
| 2 | Configure Backtest | Select instrument, dates, and strategy parameters |
| 3 | Run Backtest | Performance report with metrics and equity curve |

### Scenario 2: Strategy-Only Mode & Telegram Approval
| Step | Action | Expected Outcome |
|---|---|---|
| 1 | Set Decision Mode to STRATEGY_ONLY | System configured |
| 2 | Activate "Momentum V2" strategy | Strategy is ACTIVE |
| 3 | Trigger manual signal generation | Signal Engine generates opportunity |
| 4 | Show Telegram Bot | Alert received with Strategy score |
| 5 | Click [TAKE PAPER TRADE] in Telegram | Execution Engine processes paper trade |
| 6 | Show Portfolio Dashboard | Position appears in virtual portfolio |

### Scenario 3: Hybrid Decision Mode
| Step | Action | Expected Outcome |
|---|---|---|
| 1 | Set Decision Mode to HYBRID | System configured |
| 2 | Trigger manual signal generation | Signal Engine generates opportunity |
| 3 | Show Opportunity Details (Web) | Distinct Strategy Score AND AI Score visible |
| 4 | Show AI Evidence | Structured reasoning, sentiment, market regime |
| 5 | Show Decision Aggregator | Combined score calculation explained |

### Scenario 4: Risk Engine Intervention
| Step | Action | Expected Outcome |
|---|---|---|
| 1 | Set global Max Position Size to 1% | Risk limit tightened |
| 2 | Generate signal requiring 5% capital | Opportunity created |
| 3 | Observe Risk Engine log | Opportunity REJECTED; User notified of failure |

### Scenario 5: AI Chatbot (Market Intelligence)
| Step | Action | Expected Outcome |
|---|---|---|
| 1 | Ask "What is the P/E ratio of [instrument]?" | Grounded answer with source |
| 2 | Ask "How did Momentum V2 perform?" | Backtest results summary |
| 3 | Ask "Why was the last trade rejected?" | Explains Risk Engine max position failure |

---

## 3. Demo Data Requirements
| Data | Requirements |
|---|---|
| Instruments | At least 10-20 Indian equities + 1-2 indices |
| Telegram | Active Telegram Bot token and chat ID configured |

---

## 4. Key Points to Highlight
| Point | Importance |
|---|---|
| **Separation of Concerns** | Strategy, AI, and Execution are independent |
| **No "Magic Confirmation"** | Hybrid mode explicitly separates AI and Strategy evidence |
| **Human-in-the-loop** | Telegram approval required; live trading disabled |
| **Paper Trading** | Realistic execution simulation and portfolio tracking |
