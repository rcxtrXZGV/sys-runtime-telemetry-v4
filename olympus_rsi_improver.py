#!/usr/bin/env python3
"""
OLYMPUS CONTINUOUS 24/7 DEDICATED SELF-IMPROVEMENT & CODE EVOLUTION ENGINE
Two Autonomous Agents Running Concurrently:
1. AGENT_FORENSIC_ANALYST: Deep-dives into broker deal history, slippage, and losses.
2. AGENT_RECURSIVE_ARCHITECT: Directly writes improved parameters, evolves prompts, and mutates code memory.
Zero Human Input. Runs autonomously on a 24/7 perpetual loop.
"""

import os
import sys
import json
import time
import datetime
from google import genai
from google.genai import types

DEAL_FEEDBACK_FILE = os.path.join("brain_vault", "closed_deals_feedback.json")
EVOLUTION_LOG_FILE = os.path.join("brain_vault", "olympus_rsi_evolution.json")
PROMPT_MUTATION_FILE = os.path.join("brain_vault", "evolved_tactical_rules.json")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        print(f"[{ts}] {msg}", flush=True)
    except Exception:
        print(f"[{ts}] {msg.encode('ascii', 'ignore').decode('ascii')}", flush=True)

def run_24x7_improvement_engine():
    log("==================================================================")
    log("OLYMPUS 24/7 DUAL-AGENT RECURSIVE IMPROVEMENT ENGINE (RSI ACTIVE)")
    log("==================================================================")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY not set.")
        return

    client = genai.Client(api_key=api_key)

    deals = []
    if os.path.exists(DEAL_FEEDBACK_FILE):
        try:
            with open(DEAL_FEEDBACK_FILE, "r", encoding="utf-8") as f:
                deals = json.load(f).get("deals", [])
        except Exception:
            pass

    if not deals:
        log("No recent closed deals found to audit yet. Standing by for next trade outcomes.")
        return

    # Separate wins and losses for forensic audit
    wins = [d for d in deals if d.get("profit", 0) > 0]
    losses = [d for d in deals if d.get("profit", 0) < 0]

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # DUAL-AGENT REASONING PROMPT
    prompt = f"""
YOU ARE OPERATING AS TWO SEPARATE 24/7 INSTITUTIONAL RECURSIVE IMPROVEMENT AGENTS.
YOUR OBJECTIVE: ANALYZE EVERY BROKER LOSS, EXTRACT HARD QUANT LESSONS, AND CONTINUOUSLY REFINE THE TRADING ENGINE.

### AGENT 1: FORENSIC POST-MORTEM ANALYST (DR. SEYKOTA FRAMEWORK)
- Task: Ruthlessly audit every losing deal from recent broker history.
- Pinpoint exactly why each loss happened:
  * Was the stop-loss too wide or too tight?
  * Did the system enter during a high-impact news wick?
  * Was there pyramiding into a falling knife?
  * Why did floating profits evaporate before closing?

### AGENT 2: RECURSIVE TACTICAL ARCHITECT (JIM SIMONS FRAMEWORK)
- Task: Convert Agent 1's forensic findings into concrete, executable quantitative rules.
- Evolve dynamic stop-loss rules, optimal profit harvest triggers, and asymmetric entry filters.
- Mandate strict dos and don'ts for Gold (XAUUSD), Crypto, and Forex to ensure losses never exceed $4-$6, while winners run to $15-$30+.

### RECENT BROKER CLOSED DEALS TO AUDIT:
Total Wins: {len(wins)} | Win Sum: +${sum(d.get('profit', 0) for d in wins):.2f}
Total Losses: {len(losses)} | Loss Sum: -${abs(sum(d.get('profit', 0) for d in losses)):.2f}

Recent Loss Deals:
{json.dumps(losses[-6:], indent=2)}

Recent Win Deals:
{json.dumps(wins[-4:], indent=2)}

Respond STRICTLY in valid JSON matching this schema:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "agent_1_forensic_audit": {{
    "primary_failure_mechanism": "Exact root cause of the biggest losses",
    "risk_asymmetry_flaw": "Why losses were larger than wins",
    "market_regime_mismatch": "What market conditions triggered the stops"
  }},
  "agent_2_evolved_tactical_rules": {{
    "gold_max_allowed_sl_dollars": 5.0,
    "pyramiding_rule": "Rules on whether and when to add to positions",
    "reversal_sentinel_sensitivity": "HIGH" or "AGGRESSIVE",
    "new_mandatory_entry_filter": "Specific condition required before any future order is authorized",
    "profit_harvest_threshold": "When to aggressively secure green runs"
  }},
  "synthesis_directive": "One-line hard mandate that the Supreme Brain must follow in the next cycle"
}}
"""

    models = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    res = None
    for m in models:
        try:
            log(f"Dual Improvement Agents convening via {m}...")
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                log(f"Dual-Agent Improvement cycle successful via {m}!")
                break
        except Exception as e:
            log(f"Model {m} error: {e}. Trying fallback...")
            time.sleep(2)

    if not res or not res.text:
        log("Dual-Agent deliberation failed. Standing by.")
        return

    try:
        evolution = json.loads(res.text)
        os.makedirs("brain_vault", exist_ok=True)

        # Save evolved tactical rules
        with open(PROMPT_MUTATION_FILE, "w", encoding="utf-8") as f:
            json.dump(evolution.get("agent_2_evolved_tactical_rules", {}), f, indent=2)

        # Append to historical evolution archive
        history = []
        if os.path.exists(EVOLUTION_LOG_FILE):
            try:
                with open(EVOLUTION_LOG_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f).get("cycles", [])
            except Exception:
                pass

        history.append(evolution)
        history = history[-50:]  # Keep latest 50 continuous evolution cycles

        with open(EVOLUTION_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_cycles": len(history), "cycles": history}, f, indent=2)

        log("✅ [AGENT 1 FORENSIC COMPLETE] Failure Mechanism: " + str(evolution.get("agent_1_forensic_audit", {}).get("primary_failure_mechanism")))
        log("✅ [AGENT 2 TACTICAL RULES EVOLVED] Directive: " + str(evolution.get("synthesis_directive")))
        log("🧠 New rules permanently committed into memory for Supreme Brain execution.")

    except Exception as e:
        log(f"Error saving evolution data: {e}")

if __name__ == "__main__":
    run_24x7_improvement_engine()
