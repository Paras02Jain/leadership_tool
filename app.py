"""Earnings Call Prep Room - Streamlit prototype.
All company data is SYNTHETIC (Meridian Industrial Ltd, INR crore).
Optional: set ANTHROPIC_API_KEY (env var or Streamlit secret) for AI coaching feedback.
"""
import os
import re
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Earnings Call Prep Room", page_icon="🎙️", layout="wide")

# ------------------------------------------------------------------ DATA (synthetic)
METRICS = pd.DataFrame(
    [
        ["Revenue (₹ cr)", 4620, 4050, True],
        ["Gross margin %", 31.2, 34.8, False],
        ["EBITDA margin %", 15.1, 18.4, False],
        ["Operating cash flow (₹ cr)", 310, 640, True],
        ["Free cash flow (₹ cr)", -90, 420, True],
        ["Receivable days", 78, 64, False],
        ["Inventory days", 92, 80, False],
        ["Net debt / EBITDA (x)", 1.9, 1.2, False],
    ],
    columns=["Metric", "Q2 FY27", "Q2 FY26", "pct"],
)
SEGMENTS = pd.DataFrame(
    [
        ["Industrial Automation", 2100, 22, 17.5, 19.0],
        ["Components", 1650, 9, 12.0, 18.5],
        ["Services", 870, 8, 21.0, 21.5],
    ],
    columns=["Segment", "Revenue (₹ cr)", "Growth %", "EBITDA margin % Q2 FY27", "EBITDA margin % Q2 FY26"],
)
GUIDANCE = pd.DataFrame(
    [
        ["FY27 EBITDA margin 17.5-18.5%", "Q4 FY26 call", "H1 average 15.5% (Q1 15.8%, Q2 15.1%)", "🔴 Off track"],
        ["Margin trough in Q1, improving from Q2", "Q1 FY27 call", "Q2 15.1% is below Q1 15.8%", "🔴 Missed"],
        ["Cash conversion above 85% of EBITDA", "Q4 FY26 call", "44% (OCF 310 on EBITDA 698)", "🔴 Missed"],
        ["Components margin back to 17% by H2", "Q4 FY26 call", "12.0% in Q2, from 18.5% a year ago", "🟠 At risk"],
        ["Net debt / EBITDA below 1.5x by year end", "Q4 FY26 call", "1.9x now, from 1.2x a year ago", "🟠 At risk"],
    ],
    columns=["Commitment", "Source", "Actual", "Status"],
)
QUESTIONS = [
    dict(t="Margin recovery credibility", who="Sell-side analyst", sev=5,
         q="You called Q1 the trough, yet EBITDA margin fell again to 15.1%. Why should we believe in a second-half recovery?",
         ev=["EBITDA margin 15.1% vs 15.8% in Q1 and 18.4% a year ago", "Gross margin 31.2%, down 3.6 points year on year"],
         said="“Q1 is the trough, with sequential improvement from Q2.”",
         model="We said Q1 was the trough and Q2 is lower at 15.1% against 15.8%, so we got that wrong. Gross margin fell 3.6 points, mainly because of Components. We have started repricing contracts and moving material to alternate suppliers, and we expect the first benefit in Q3. We will report gross margin by segment each quarter so you can track it.",
         keys=["Name the miss plainly", "Split the 3.6 point gross margin fall by cause", "Give one dated, measurable milestone"]),
    dict(t="Cash conversion", who="Fund manager", sev=5,
         q="Operating cash flow halved to ₹310 crore and free cash flow is negative. You promised conversion above 85% of EBITDA. What happened?",
         ev=["OCF 310 vs 640; FCF -90 vs 420", "Conversion 44% against a pledge above 85%", "Receivable days 78 vs 64; inventory days 92 vs 80"],
         said="“We expect cash conversion above 85% of EBITDA this year.”",
         model="Conversion was 44% against our commitment above 85%, which is a clear shortfall. Receivable days rose from 64 to 78 and inventory days from 80 to 92, as we built stock ahead of Automation deliveries. We have set a collections target of 70 days by Q4 and are cutting stock in Components. We will not reach 85% for the full year, and we expect the second half to recover part of the gap.",
         keys=["Admit the full-year pledge is at risk", "Tie the cash gap to receivable and inventory days", "State a target day count and date"]),
    dict(t="Components segment", who="Sell-side analyst", sev=4,
         q="Components margin dropped from 18.5% to 12.0% while revenue grew 9%. Is this volume bought with price, or is it cost?",
         ev=["Components revenue +9%, margin 12.0% vs 18.5%", "Pledge: 17% margin by H2"],
         said="“Components margin returns to 17% by the second half.”",
         model="Components margin fell 6.5 points to 12.0% even with 9% revenue growth, so this is mainly cost, not volume at any price. Input costs rose faster than our contracts allowed us to pass on. The 17% target by the second half is now at risk and I will not repeat it today. We will update you next quarter once repricing is complete.",
         keys=["Separate price from cost with a figure", "Say plainly if the 17% pledge stands", "Avoid repeating a target you no longer trust"]),
    dict(t="Quality of growth", who="Buy-side analyst", sev=3,
         q="Revenue is up 14% but profit is not. Is Automation growth of 22% coming at the expense of margin?",
         ev=["Revenue 4,620 vs 4,050 (+14.1%)", "Automation +22%, margin 17.5% vs 19.0%"],
         said="“Growth will be profitable growth.”",
         model="Automation grew 22% and its margin slipped 1.5 points to 17.5%, so part of that growth carried lower margin on new large orders. It is still our second most profitable segment after Services at 21.0%. We are applying minimum margin thresholds on new bids from this quarter and will show you order margin in the next call.",
         keys=["Quote both the growth and the margin change", "Place the segment in the wider mix", "Describe a bid discipline rule"]),
    dict(t="Balance sheet and leverage", who="Credit analyst", sev=4,
         q="Net debt to EBITDA went from 1.2x to 1.9x. You targeted below 1.5x. How are you funding this and are covenants at risk?",
         ev=["Net debt / EBITDA 1.9x vs 1.2x", "Negative FCF of ₹90 crore", "Target: below 1.5x by year end"],
         said="“We will end the year below 1.5x net debt to EBITDA.”",
         model="Leverage is 1.9x against our target below 1.5x. The rise comes from weaker EBITDA and a working capital build, with free cash flow at negative ₹90 crore. We are deferring non-critical capex and tying the target to working capital release in the second half. We expect to be above 1.5x at year end unless collections reach plan, and we will update you in Q3.",
         keys=["State leverage and the gap to target", "Name the funding source for the shortfall", "Be honest about the year-end outlook"]),
    dict(t="Guidance credibility", who="Fund manager", sev=5,
         q="Your FY27 EBITDA margin guidance is 17.5-18.5% and the first half averaged 15.5%. Are you cutting guidance?",
         ev=["H1 average 15.5% vs guidance 17.5-18.5%", "Second half would need margins well above 19%"],
         said="“FY27 EBITDA margin of 17.5-18.5%.”",
         model="With the first half at 15.5%, reaching 17.5% for the year would need a second half well above 19%, which we do not expect. We are withdrawing the 17.5-18.5% range and will give a new range once repricing and cost actions are visible next quarter. We would rather reset now than miss again.",
         keys=["Do the arithmetic on the required second half", "Decide: reaffirm, cut, or withdraw", "Do not ask investors to take it on trust"]),
    dict(t="Working capital integrity", who="Skeptical investor", sev=3,
         q="Receivable days jumped from 64 to 78 while revenue grew. Are you pulling sales forward or extending credit to win business?",
         ev=["Receivable days 78 vs 64", "Revenue +14.1%"],
         said="“Credit terms remain unchanged.”",
         model="Receivable days rose from 64 to 78. Part of this is Automation projects billed late in the quarter, and part is slower collections from two large customers. We have not changed standard terms. We are tracking overdue balances weekly and will report receivables over 90 days next quarter.",
         keys=["Give the number and the two drivers", "Answer the terms question directly", "Offer a new disclosure"]),
]

# ------------------------------------------------------------------ SCORING
def _nums(text):
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    text = re.sub(r"\b(FY|Q|H)\d+", "", text)
    return [n.lstrip("-") for n in re.findall(r"-?\d+(?:\.\d+)?", text)]

_blob = json.dumps([METRICS.values.tolist(), SEGMENTS.values.tolist(), GUIDANCE.values.tolist(),
                    [[x["ev"], x["said"]] for x in QUESTIONS]], ensure_ascii=False)
KNOWN = set(_nums(_blob)) | {"3.6", "6.5", "1.5", "0.7", "7", "14", "44", "15.5", "19", "90", "70"}

RUBRIC = [
    ("Owns the miss plainly", 25, lambda t, k: bool(re.search(r"(wrong|shortfall|missed|\bmiss\b|below (our|the)|short of|fell|disappoint|not where we|behind|at risk|clear)", t, re.I))),
    ("Cites at least two figures from the disclosures", 20, lambda t, k: k["good"] >= 2),
    ("Explains the cause", 15, lambda t, k: bool(re.search(r"(because|due to|driven by|mainly|result of|comes from|reflect|as we|input costs|rise)", t, re.I))),
    ("States a specific action", 15, lambda t, k: bool(re.search(r"(we have (started|set|begun|applied)|we are (cutting|deferring|tracking|applying|withdrawing|moving)|repric|target of|threshold)", t, re.I))),
    ("Gives a dated, checkable commitment", 15, lambda t, k: bool(re.search(r"(Q[1-4]|second half|H2|next quarter|next call|year end|from this quarter|each quarter)", t, re.I))),
    ("Avoids evasive language", 10, lambda t, k: not re.search(r"(challenging environment|macro|transitory|one[- ]off|temporary|headwind|remain confident|not material|going forward|difficult to say|too early)", t, re.I)),
]

def score(text):
    k = {"good": 0, "bad": []}
    for n in _nums(text):
        if n in KNOWN or str(float(n)).rstrip("0").rstrip(".") in KNOWN:
            k["good"] += 1
        elif float(n) >= 5 or "." in n:
            k["bad"].append(n)
    words = len(text.split())
    total, checks = 0, []
    for name, pts, fn in RUBRIC:
        ok = fn(text, k)
        total += pts if ok else 0
        checks.append((name, pts, ok))
    len_ok = 40 <= words <= 130
    if not len_ok:
        total = max(0, total - 10)
    total = max(0, total - 5 * min(len(k["bad"]), 3))
    return dict(score=total, checks=checks, words=words, len_ok=len_ok, bad=k["bad"], text=text)

def get_api_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY")

def ai_coach(q, answer, key):
    import anthropic
    facts = json.dumps({"metrics": METRICS.drop(columns="pct").values.tolist(),
                        "segments": SEGMENTS.values.tolist(), "guidance": GUIDANCE.values.tolist()}, ensure_ascii=False)
    system = ("You are an investor-relations coach. Use ONLY the facts supplied. Critique the executive's answer in: "
              "1) what works, 2) gaps vs the on-record commitment, 3) any figure not supported by the facts, "
              "4) a tighter rewrite under 100 words. Be concise and direct.")
    msg = f"FACTS: {facts}\nON RECORD: {q['said']}\nQUESTION: {q['q']}\nANSWER: {answer}"
    client = anthropic.Anthropic(api_key=key)
    r = client.messages.create(model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=700,
                               system=system, messages=[{"role": "user", "content": msg}])
    return "".join(b.text for b in r.content if b.type == "text")

# ------------------------------------------------------------------ UI
st.session_state.setdefault("results", {})
res = st.session_state["results"]

st.title("🎙️ Earnings Call Prep Room")
st.caption("Meridian Industrial Ltd (synthetic) · Q2 FY27 · Find where results contradict past commitments, then rehearse the hard questions.")

with st.sidebar:
    st.header("About")
    st.markdown("**Assumptions**\n- All figures are synthetic, in ₹ crore.\n- Prior guidance and quotes are illustrative.\n- Scoring is a rule-based proxy for answer quality.")
    st.markdown("**AI coaching** (optional)")
    key = get_api_key()
    key = st.text_input("Anthropic API key", type="password", value="", placeholder="Uses secret/env if set") or key
    st.caption("AI coach on" if key else "AI coach off: rule-based scoring only")

tab1, tab2 = st.tabs(["1. Fact base and gaps", "2. Rehearse"])

with tab1:
    m = METRICS.set_index("Metric")
    c = st.columns(4)
    def pct(a, b): return f"{(a - b) / abs(b) * 100:+.1f}% YoY"
    c[0].metric("Revenue (₹ cr)", f"{m.loc['Revenue (₹ cr)','Q2 FY27']:,}", pct(4620, 4050))
    c[1].metric("EBITDA margin", "15.1%", "-3.3 pts", delta_color="inverse" if False else "normal")
    c[2].metric("Operating cash flow (₹ cr)", "310", pct(310, 640))
    c[3].metric("Net debt / EBITDA", "1.9x", "+0.7x", delta_color="inverse")
    st.subheader("Results vs last year")
    st.dataframe(METRICS.drop(columns="pct"), hide_index=True, width='stretch')
    st.subheader("Segment EBITDA margin")
    st.bar_chart(SEGMENTS.set_index("Segment")[["EBITDA margin % Q2 FY26", "EBITDA margin % Q2 FY27"]])
    st.caption("Components drives most of the margin loss.")
    st.subheader("What management said vs what happened")
    st.dataframe(GUIDANCE, hide_index=True, width='stretch')
    st.info("All five prior commitments are off track. Investors will quote them back, so answer the commitment before the explanation.")

with tab2:
    left, right = st.columns([1, 2])
    labels = [f"{'▮' * x['sev']}{'▯' * (5 - x['sev'])}  {x['t']}" + (f"  ({res[i]['score']})" if i in res else "") for i, x in enumerate(QUESTIONS)]
    with left:
        idx = st.radio("Likely questions (by severity)", range(len(QUESTIONS)), format_func=lambda i: labels[i])
    q = QUESTIONS[idx]
    with right:
        st.caption(q["who"])
        st.subheader(f"“{q['q']}”")
        st.warning(f"**On the record:** {q['said']}")
        st.markdown("**Evidence they will use**\n" + "\n".join(f"- {e}" for e in q["ev"]))
        ans = st.text_area("Your answer, as you would say it on the call", value=res.get(idx, {}).get("text", ""), height=150, key=f"a{idx}")
        b1, b2, b3 = st.columns(3)
        if b1.button("Score my answer", type="primary") and ans.strip():
            res[idx] = score(ans)
        show_model = b2.toggle("Show model answer")
        coach = b3.button("AI coach feedback", disabled=not key)
        if idx in res:
            r = res[idx]
            st.metric("Score", f"{r['score']}/100")
            st.progress(r["score"] / 100)
            for name, pts, ok in r["checks"]:
                st.write(f"{'✅' if ok else '❌'} {name} ({pts})")
            st.write(f"{'✅' if r['len_ok'] else '⚠️'} Length {r['words']} words (aim for 40 to 130)")
            if r["bad"]:
                st.error(f"Consistency flag: {', '.join(r['bad'])} not found in the disclosures. Verify before saying them.")
            else:
                st.success("All figures quoted match the fact base.")
        if coach and ans.strip():
            with st.spinner("Coaching..."):
                try:
                    st.markdown(ai_coach(q, ans, key))
                except Exception as e:
                    st.error(f"AI coach unavailable: {e}")
        if show_model:
            st.success(q["model"])
            st.markdown("**What a strong answer does**\n" + "\n".join(f"- {k}" for k in q["keys"]))
