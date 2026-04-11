---
title: Data Privacy Agent GEU
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Data Privacy & Compliance Officer Environment

This environment evaluates AI agents on their ability to sanitize sensitive datasets.

## Tasks

- **Easy** (`mask-emails`): Identify and mask PII (emails) in CSV format.
- **Medium** (`redact-phones`): Use pattern matching to redact international phone numbers.
- **Hard** (`sanitize-json`): Perform structural transformations and hashing on JSON objects.

## Setup

```
pip install openenv-core
openenv validate .
```
