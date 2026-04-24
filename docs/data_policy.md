# Ethical Data Policy

## Overview

SoukAI is built on the principle of **ethical, legal, and transparent data use**. We do not scrape, harvest, or store any personal or proprietary data without explicit consent.

## Data Sources

| Source | Type | Usage |
|--------|------|-------|
| `data/products.csv` | Manually curated sample data | Training / demo |
| `data/comments.csv` | Manually written example comments | NLP intent detection demo |
| User-uploaded CSVs | User-owned data | On-demand analysis only |

## What We Do NOT Do

- ❌ We do **not** scrape Jumia, Avito, Facebook, Instagram, or any website
- ❌ We do **not** collect personal identifiable information (PII)
- ❌ We do **not** store uploaded data beyond the current session (MVP scope)
- ❌ We do **not** share any data with third parties

## Darija / Arabic Language Handling

- All Darija and Arabic text is processed locally on the server
- No text data is sent to external AI APIs

## Roadmap – Data Ethics

- [ ] Add user consent flow for CSV uploads
- [ ] Auto-delete uploaded files after analysis
- [ ] GDPR-compatible data retention policy
