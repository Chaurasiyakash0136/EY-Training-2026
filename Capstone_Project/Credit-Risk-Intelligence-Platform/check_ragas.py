# check_ragas.py (final working version)
# No ragas package needed — tests the direct OpenAI implementation
# python check_ragas.py

print("=" * 60)
print("RAGAS Evaluation Readiness Check")
print("(direct OpenAI implementation — no ragas package needed)")
print("=" * 60)
print()

from dotenv import load_dotenv
import os
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY", "")
enabled    = os.getenv("EVALUATION_ENABLED", "false")

print("STEP 1 — Checking .env settings...")
print(f"  OPENAI_API_KEY     : {'SET ✅' if openai_key else 'MISSING ❌  — add to .env'}")
print(f"  EVALUATION_ENABLED : {enabled} {'✅' if enabled.lower() == 'true' else '❌  — change to true in .env'}")
print()

if not openai_key:
    print("Cannot proceed — OPENAI_API_KEY is missing from .env")
    exit(1)

print("STEP 2 — Checking openai package...")
try:
    import openai
    print(f"  openai ✅  (version: {openai.__version__})")
except ImportError:
    print("  openai ❌  — run: pip install openai")
    exit(1)
print()

print("STEP 3 — Running live faithfulness + relevancy test...")
print("         Sending 2 small requests to OpenAI (~10 seconds)...")
print()

try:
    from openai import OpenAI

    client = OpenAI(api_key=openai_key)

    context = ("Deepak Sharma Net Salary Take Home Rs. 25,640. "
               "Basic Salary Rs. 18,000. HRA Rs. 5,400. Provident Fund Rs. 2,160.")
    question = "What is the net salary of Deepak Sharma?"
    answer   = "The net salary of Deepak Sharma is Rs. 25,640 per month as stated in the salary slip."

    # --- Faithfulness test ---
    faith_prompt = f"""You are evaluating an AI answer for faithfulness.

CONTEXT: {context}
AI ANSWER: {answer}

Rate how faithfully the answer sticks to the context.
10 = every statement supported by context. 0 = facts not in context.
Reply with ONLY a single integer 0-10."""

    faith_raw = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": faith_prompt}],
        temperature=0, max_tokens=5,
    ).choices[0].message.content.strip()
    faith = int("".join(c for c in faith_raw if c.isdigit())[:2]) / 10.0

    # --- Relevancy test ---
    relev_prompt = f"""QUESTION: {question}
AI ANSWER: {answer}

Rate how directly the answer addresses the question.
10 = directly and completely answers it. 0 = does not address it.
Reply with ONLY a single integer 0-10."""

    relev_raw = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": relev_prompt}],
        temperature=0, max_tokens=5,
    ).choices[0].message.content.strip()
    relev = int("".join(c for c in relev_raw if c.isdigit())[:2]) / 10.0

    print(f"  faithfulness     : {faith:.2f}  {'✅ Good' if faith >= 0.7 else '⚠️  Low'}")
    print(f"  answer_relevancy : {relev:.2f}  {'✅ Good' if relev >= 0.7 else '⚠️  Low'}")
    print()
    print("  ✅ RAGAS-style evaluation IS WORKING")
    print()
    print("  The ragas package is NOT needed — evaluation uses direct")
    print("  OpenAI API calls (same mechanism ragas uses internally).")
    print()
    print("  Now run the full evaluation:")
    print("  python tests\\evaluation\\run_evaluation.py")

except Exception as e:
    err = str(e)
    print(f"  ❌ Failed: {err[:300]}")
    print()
    if "401" in err or "api_key" in err.lower() or "authentication" in err.lower():
        print("  FIX: Your OPENAI_API_KEY is wrong or expired.")
        print("       Get a new one at https://platform.openai.com/api-keys")
    elif "429" in err or "quota" in err.lower():
        print("  FIX: OpenAI rate limit hit. Wait 1 minute and try again.")
    else:
        print("  Share this error for help.")

print()
print("=" * 60)
