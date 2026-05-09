# Malicious Mail Analyzer

Malicious Mail Analyzer is an explainable Gmail Add-on that analyzes an opened email and produces a maliciousness score, a clear verdict, and detailed reasoning behind the result.

The project combines a Google Workspace Gmail Add-on with a Python FastAPI backend. The Gmail Add-on is the product-facing layer, while the backend performs raw email parsing, feature extraction, risk scoring, and explainable verdict generation.

---

# Demo Examples

The project includes several realistic phishing email samples under the `samples/` directory.
These examples demonstrate how different phishing indicators affect the final maliciousness verdict.

---

## Risky Attachment Detection

This example demonstrates detection of a dangerous attachment such as an executable file.

Detected signals include:

- Suspicious words
- Generic greeting
- Risky attachment detection

Example result:

![Risky Attachment Example](samples/attachment_example.png)

---

## Suspicious URL / Hard Signal Detection

This example demonstrates a phishing email containing a suspicious hidden URL behind a legitimate-looking text such as:

```text
Verify Account
```

Detected signals include:

- Suspicious words
- Generic greeting
- Suspicious URL pattern
- Hard signal escalation

Example result:

![Suspicious URL Example](samples/hard_signal_example.png)

---

## Gmail Add-on User Context

The Gmail Add-on also supports lightweight user context configuration.

The user name and email are used only for:

- Personalization detection
- Recipient validation

Example:

![User Context Example](samples/user_context.png)

---

These examples help demonstrate the difference between:

- Regular weighted scoring signals
- Hard security signals

For example:

- Generic greetings increase the numeric maliciousness score.
- Dangerous URLs or risky attachments can force stronger verdict escalation.

---

# Overview

The goal of this project is to help users quickly understand whether an opened email looks safe, suspicious, or malicious.

Instead of returning only a black-box classification, the system explains *why* an email received its verdict.

For example, the system can detect:

- Suspicious words commonly found in malicious emails
- Generic greetings that are not personalized
- Reply-To domain mismatch
- Suspicious recipient patterns
- Risky URLs
- Risky attachment file types
- Email authentication failures
- Suspicious sender domain patterns

The final result is shown directly inside Gmail as a clean, readable Gmail Add-on card.

---

# Product Flow

```text
User opens an email in Gmail
        ↓
Gmail Add-on receives the opened email context
        ↓
The Add-on extracts the raw MIME email
        ↓
The Add-on sends the email to the backend API
        ↓
Backend parses the email
        ↓
Backend extracts security features
        ↓
Backend calculates maliciousness score and verdict
        ↓
Gmail Add-on displays the verdict and explanations
```

---

# Why Raw MIME Email?

The Gmail Add-on sends the raw MIME email to the backend instead of only sending the visible email text.

This is important because raw MIME preserves security-relevant information such as:

- Full email headers
- SPF / DKIM / DMARC authentication results
- Reply-To header
- Sender metadata
- Plain text body
- HTML body
- URLs
- Attachment metadata
- MIME structure

This provides a more realistic security analysis compared to analyzing only the rendered email body.

---

# Project Structure

```text
MaliciousMailAnalyzer/
│
├── backend/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── check_api.py
│   │
│   ├── email_parsing/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── email_parser.py
│   │   ├── header_extractor.py
│   │   ├── body_extractor.py
│   │   ├── url_extractor.py
│   │   ├── attachment_extractor.py
│   │   ├── email_printer.py
│   │   └── check_email_parser.py
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── feature_result.py
│   │   ├── feature_runner.py
│   │   ├── suspicious_words_feature.py
│   │   ├── personalization_feature.py
│   │   ├── reply_to_mismatch_feature.py
│   │   ├── recipient_pattern_feature.py
│   │   ├── url_risk_feature.py
│   │   ├── attachment_risk_feature.py
│   │   ├── sender_domain_feature.py
│   │   ├── email_authentication_feature.py
│   │   └── check_features.py
│   │
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── email_scorer.py
│   │
│   └── requirements.txt
│
├── gmail_addon/
│   ├── Code.gs
│   └── appsscript.json
│
├── exploratory_data_analysis/
│   ├── phishing_email_eda.ipynb
│   └── suspicious_words/
│       ├── top_malicious_words.csv
│       ├── top_suspicious_words_by_email_count.csv
│       └── top_suspicious_words_by_total_words.csv
│
├── samples/
│   ├── sample_email.eml
│   ├── attachment_example.png
│   ├── hard_signal_example.png
│   └── user_context.png
│
├── .gitignore
└── README.md
```

---

# Main Components

## Gmail Add-on

Location:

```text
gmail_addon/
```

The Gmail Add-on is the user-facing product.

It is responsible for:

- Running inside Gmail
- Reading the currently opened email
- Extracting the raw MIME email
- Reading user settings such as name and email
- Sending the email to the backend
- Displaying the final verdict, score, hard signals, and explanations

The Add-on is implemented using Google Apps Script and Google Workspace Add-on APIs.

---

## Backend API

Location:

```text
backend/api/
```

The backend API is implemented with FastAPI.

Main endpoint:

```text
POST /analyze-email
```

Request body:

```json
{
  "raw_email": "...",
  "user_name": "Zion, Zion Memun",
  "user_email": "zion@example.com"
}
```

Response body:

```json
{
  "verdict": "safe",
  "regular_score": 5,
  "hard_signals": [],
  "detected_features": []
}
```

The API receives the raw email, parses it, runs all security features, calculates the final score, and returns an explainable result.

---

## Email Parsing

Location:

```text
backend/email_parsing/
```

The email parser converts a raw MIME email into a normalized `ParsedEmail` object.

The parser extracts:

- Sender name
- Sender email
- Sender domain
- Reply-To address
- Reply-To domain
- To / Cc / Bcc recipients
- Subject
- Plain text body
- HTML body
- URLs
- Attachments
- Headers

The normalized structure allows every feature to work on the same clean interface.

---

## Feature Extraction

Location:

```text
backend/features/
```

Each feature analyzes one security aspect of the email and returns a standard `FeatureResult`.

A feature result includes:

```python
feature_id
title
description
detected
score
evidence
minimum_verdict
```

This structure makes the system explainable and frontend-friendly.

---

# Feature Design

The system uses two types of signals:

## Hard Signals

Hard signals are strong security indicators.

If a hard signal is detected, it can force the final verdict to a high-risk state even if the regular score is low.

Examples:

- Suspicious URL infrastructure
- SPF / DKIM / DMARC authentication failure
- Suspicious sender TLD
- Reply-To mismatch

Hard signals are not treated as normal score contributions.  
Instead, they set a minimum verdict.

Example:

```text
URL shortener detected
→ minimum_verdict = high_risk
→ score = 0
```

This design prevents dangerous infrastructure indicators from being diluted by benign-looking text.

---

## Regular Weighted Signals

Regular signals are weaker indicators that are meaningful mainly when combined.

Examples:

- Suspicious words
- Generic greeting
- Recipient pattern
- Risky attachment extension
- Digit substitution in sender domain

These features contribute to the regular maliciousness score.

---

# Implemented Features

## Suspicious Words Feature

This feature checks the email subject and body for suspicious words.

The words are grouped into threat categories.

The score is based on the number of matched groups, not the number of words.

```text
1 group  → 10 points
2 groups → 20 points
3 groups → 30 points
4+ groups → 40 points
```

---

## Personalization Feature

This feature checks whether the email addresses the user personally.

The user can provide multiple names, separated by commas.

Example:

```text
Zion, Zion Memun, ZionMemun, ציון
```

The feature checks:

- Whether one of the provided names appears in the email
- Whether greetings such as `Hi`, `Hello`, `Hey`, or `Dear` are followed by one of the names
- Whether there is a greeting without a provided name

Scoring:

```text
Provided name found       → -15 points
Greeting without name     → +10 points
No personalization signal → 0 points
```

---

## Reply-To Mismatch Feature

This feature compares the sender address and the Reply-To address.

A mismatch can be suspicious because attackers often send from one visible identity but redirect replies elsewhere.

The implementation does not simply require exact domain equality.  
It allows related domains and addresses to avoid false positives.

Example considered related:

```text
From: NVIDIA HR <nvidia@myworkday.com>
Reply-To: donotreply@nvidia.com
```

If the sender and Reply-To appear unrelated, the feature returns:

```text
minimum_verdict = suspicious
score = 0
```

---

## Recipient Pattern Feature

This feature analyzes recipient behavior.

It checks:

- Many visible recipients
- User email missing from To/Cc
- Undisclosed recipients

Scoring:

```text
Many visible recipients          → +10 points
User not in visible recipients   → +10 points
Undisclosed recipients           → +10 points
Maximum score                    → 25 points
```

---

## URL Risk Feature

This feature analyzes URLs found in the email.

It checks only real web URLs and ignores non-web links such as:

```text
mailto:
tel:
cid:
data:
```

Suspicious URL patterns include:

- IP address used instead of a domain
- URL shortener domain
- Suspicious top-level domain

Any suspicious URL pattern is treated as a hard signal:

```text
minimum_verdict = high_risk
score = 0
```

---

## Attachment Risk Feature

This feature analyzes attachment extensions.

Scoring:

```text
.exe / .bat / .cmd / .vbs / .ps1 / .scr → +60
.js / .jse / .wsf                       → +45
.docm / .xlsm / .pptm                   → +35
.zip / .rar / .7z                       → +20
```

---

## Sender Domain Feature

This feature checks the sender domain for suspicious structural patterns.

It currently checks:

### Suspicious TLD

Examples:

```text
.xyz
.top
.click
.ru
```

A suspicious TLD is treated as:

```text
minimum_verdict = high_risk
score = 0
```

### Digit-Letter Substitution

Examples:

```text
amaz0n.com
micr0soft.com
paypa1.com
g00gle.com
```

This pattern receives:

```text
+25 points
```

---

## Email Authentication Feature

This feature analyzes authentication headers such as:

```text
Authentication-Results
ARC-Authentication-Results
Received-SPF
```

It extracts:

```text
SPF
DKIM
DMARC
```

Failed checks such as:

```text
spf=fail
dkim=fail
dmarc=fail
```

are treated as hard signals:

```text
minimum_verdict = high_risk
score = 0
```

---

# Scoring Model

The scoring model separates hard signals from regular weighted scoring.

## Regular Score

The regular score is the sum of all feature scores.

It is normalized to stay between 0 and 100:

```text
score < 0   → 0
score > 100 → 100
```

---

## Score-Based Verdict

If no hard signal exists, the verdict is based on the regular score:

```text
0–14    → Safe
15–39   → Low Risk
40–69   → Suspicious
70–100  → High Risk
```

---

## Hard Signal Override

If any hard signal is detected, it can override the score-based verdict.

Example:

```text
Regular score: 5
Hard signal: Suspicious URL detected
Final verdict: High Risk
```

---

# Running The Backend Locally

Navigate to the backend directory:

```powershell
cd backend
```

Set `PYTHONPATH`:

```powershell
$env:PYTHONPATH="."
```

Run the FastAPI server:

```powershell
uvicorn api.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

---

# Exposing Backend To Gmail Add-on

During local development, the backend is exposed using ngrok:

```powershell
ngrok http 8000
```

This creates a public HTTPS URL:

```text
https://example.ngrok-free.dev
```

The Gmail Add-on uses:

```javascript
const BACKEND_URL =
  "https://example.ngrok-free.dev/analyze-email";
```

---

# Security Considerations

Security was treated as a first-class concern.

Design choices include:

- Parsing raw MIME instead of rendered text
- Treating emails as untrusted input
- Keeping feature logic in the backend rather than the Add-on
- Avoiding secrets in the repository
- Using explainable deterministic features
- Separating hard signals from weighted signals
- Handling attachments by metadata rather than executing or opening them

The system does not execute attachments, follow links, or trust email content.

---

# Future Improvements

With more time, I would add:

- Cloud deployment for the backend
- URL reputation service integration
- Attachment hash scanning
- ML-based text classifier
- Domain age / WHOIS signals
- Better brand impersonation detection
- Organization allowlist
- User feedback loop
- Admin dashboard
- Better multilingual support
- More advanced Gmail Add-on UX

---

# Summary

Malicious Mail Analyzer is an explainable Gmail Add-on for email threat scoring.

It demonstrates:

- Product thinking
- Gmail Workspace integration
- Backend architecture
- Raw MIME parsing
- Security-focused feature engineering
- Explainable scoring
- Clean code structure
- Practical trade-off awareness

The system is intentionally designed to be understandable, modular, and easy to extend.