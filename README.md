# Rider Payout Dispute Desk

ProcureYard take-home assignment for the **ML/AI Engineer Intern** role. Start with `BRIEF.md`.

An AI operations agent built to handle rider payout disputes. The system leverages **FastAPI, PostgreSQL, and Groq's LLM API (`openai/gpt-oss-20b`)** to parse natural language complaints, safely infer trip dates, execute deterministic financial calculations via internal tools, and log all traces for review.

## Features & Architecture

* **Conversational AI with Guardrails:** Uses `openai/gpt-oss-20b` via Groq to understand Hinglish complaints, while system-level constraints strictly enforce security and date-inference rules.

* **Deterministic Financial Math:** To eliminate LLM arithmetic errors, actual payout calculations (₹25 base fare, ₹6/km distance fee after 2 km, 1.5× surge multiplier, ₹10 cancellation penalty, and ₹150 daily incentives for 12+ trips) are strictly computed inside a Python backend tool.

* **Security & Authentication:** `rider_id` values are securely injected via the webhook payload, preventing cross-account impersonation and prompt-injection attacks.

* **Full Audit Trail:** Every message, tool call, and agent reply is structurally logged in the PostgreSQL `agent_traces` table.

* **Built-in Ops Dashboard:** Includes a fully functional web interface at `/ops`, where operations staff can view, approve, or reject pending payouts flagged by the agent.

## How to Run

### 1. Environment Setup

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_api_key
```

### 2. Start the Infrastructure

```bash
docker compose up -d
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Application

Run the FastAPI application using Uvicorn:

```bash
python -m uvicorn main:app --reload
```

### 5. Run the Evaluation Suite

In a separate terminal, execute the evaluation script against your local service:

```bash
python eval.py http://127.0.0.1:8000
```

## API Endpoints

1. **POST `/messages`**: Receives incoming webhook messages from riders and returns `{"reply": "..."}`.

2. **GET `/trace/{rider_id}`**: Returns a structured JSON history of all agent steps, including message inputs, tool calls, decisions, and replies.

3. **GET `/ops/pending`**: Returns a JSON list of all payout discrepancies awaiting manual operations approval.

4. **GET `/ops`**: Serves an interactive HTML dashboard for operations staff to review and resolve pending approvals.Open 
```
http://127.0.0.1:8000/ops
```
 and you cancheck that the approvals table.

## Assumptions Made

### Date Inference

Riders frequently omit the month and year in casual chat (e.g., `"20 wala"`). The agent dynamically converts these into full `YYYY-MM-DD` strings using the webhook's `received_at` timestamp as a baseline.

### Database Auto-Provisioning

To prevent foreign key constraint violations (`ForeignKeyViolation`) when evaluation scripts dynamically create test riders, an automatic UPSERT operation is performed on the `riders` table upon message intake.

### Rate Limiting Protection

The evaluation script uses a controlled 4-second delay between requests to remain safely under Groq's free-tier rate limits.

## Evaluation Results

The agent successfully processes evaluation test cases, enforces strict security boundaries against adversarial prompt injections, accurately calculates payout disparities using database state, and formats outputs into natural Hinglish responses.


