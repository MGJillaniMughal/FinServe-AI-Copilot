"""FinServe AI Engine.

Dual-mode intelligence:
  * LLM mode  - uses an OpenAI-compatible chat model when OPENAI_API_KEY is set.
  * Local mode - a deterministic, explainable analytical engine (weighted
                 lexicons + TF-IDF retrieval) that runs fully offline.

The active mode is surfaced through `status()` and the /health endpoint.

Developed by Jillani SofTech (Muhammad Ghulam Jillani).
"""
import re
from typing import Dict, List

from backend.config import settings
from backend.utils.logger import get_logger
from backend.services.vector_store import VectorStore

logger = get_logger("ai-engine")

# Weighted compliance evidence (term -> weight) per framework
FRAMEWORKS = {
    "AML": {"aml": 3, "anti-money": 3, "laundering": 3, "suspicious": 2,
            "sar": 2, "fatf": 2, "monitoring": 1, "screening": 1},
    "KYC": {"kyc": 3, "know your customer": 3, "identity": 2, "verification": 2,
            "due diligence": 3, "onboarding": 2, "cdd": 2, "edd": 2},
    "GDPR": {"gdpr": 3, "personal data": 3, "data subject": 3, "consent": 2,
             "privacy": 2, "erasure": 2, "retention": 1, "processing": 1},
    "SOC 2": {"soc 2": 3, "soc2": 3, "trust services": 3, "availability": 2,
              "controls": 2, "audit trail": 2, "access control": 2, "confidentiality": 1},
}

# Risk lexicon with severity weights
RISK_TERMS = {
    "default": 9, "breach": 8, "fraud": 9, "insolvency": 9, "litigation": 7,
    "downgrade": 7, "loss": 6, "exposure": 5, "leverage": 6, "concentration": 6,
    "volatility": 5, "liquidity": 4, "covenant": 5, "delay": 3, "arrears": 6,
    "diversified": -4, "hedged": -4, "stable": -3, "compliant": -3, "surplus": -3,
}

MITIGATION_MAP = {
    "concentration": "Reduce single-name/sector concentration through diversification limits.",
    "volatility": "Apply volatility-based position sizing and hedging overlays.",
    "leverage": "Lower gross leverage and enforce margin/maintenance thresholds.",
    "liquidity": "Hold a liquidity buffer and maintain committed credit lines.",
    "default": "Tighten counterparty credit limits and require collateral posting.",
    "exposure": "Set automated exposure alerts and counterparty caps.",
    "covenant": "Negotiate covenant headroom and add early-warning triggers.",
}


class AIEngine:
    def __init__(self) -> None:
        self.client = None
        self.mode = "local"
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.mode = "llm"
                logger.info("AI engine: LLM mode (%s)", settings.MODEL_NAME)
            except Exception as exc:
                logger.warning("OpenAI unavailable, using local engine: %s", exc)
        if self.mode == "local":
            logger.info("AI engine: Local Intelligence mode (offline, no key required)")

    # ----- identity -----
    @property
    def model(self) -> str:
        return settings.MODEL_NAME if self.mode == "llm" else "finserve-local-intelligence-v2"

    def status(self) -> Dict[str, str]:
        return {
            "mode": self.mode,
            "label": "LLM" if self.mode == "llm" else "Local Intelligence",
            "status": "Active",
        }

    def _chat(self, system: str, user: str):
        if self.mode == "llm" and self.client is not None:
            try:
                r = self.client.chat.completions.create(
                    model=settings.MODEL_NAME,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                    temperature=0.2,
                )
                return r.choices[0].message.content
            except Exception as exc:
                logger.warning("LLM call failed, using local engine: %s", exc)
        return None

    # ----- RAG answer -----
    def answer(self, query: str, contexts: List[Dict], store: VectorStore) -> str:
        joined = "\n".join(c["text"] for c in contexts)
        llm = self._chat(
            "You are FinServe AI by Jillani SofTech, an enterprise financial intelligence "
            "assistant. Answer only from the provided context and cite document names.",
            f"Question: {query}\n\nContext:\n{joined}",
        )
        if llm:
            return llm
        if not contexts:
            return ("No relevant passages were found in the indexed corpus for this question. "
                    "Upload a related financial or compliance document and try again.")
        key = store.best_sentences(query, contexts, n=3)
        files = sorted({c["filename"] for c in contexts})
        body = " ".join(key) if key else contexts[0]["text"][:300]
        return f"{body} (Synthesised from {len(contexts)} passage(s) across {', '.join(files)}.)"

    def summarize(self, text: str) -> str:
        llm = self._chat("Summarise this document for executives in 3 sentences.", text)
        if llm:
            return llm
        sents = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(sents[:3]).strip() or "No content to summarise."

    # ----- Risk -----
    def analyze_risk(self, text: str, subject: str) -> Dict:
        lower = text.lower()
        hits = {term: lower.count(term) for term in RISK_TERMS if term in lower}
        raw = 42 + sum(RISK_TERMS[t] * min(n, 3) for t, n in hits.items())
        score = float(max(5, min(96, raw)))
        category = "High" if score >= 70 else "Medium" if score >= 45 else "Low"

        contributors = sorted(
            [(t, RISK_TERMS[t] * n) for t, n in hits.items() if RISK_TERMS[t] > 0],
            key=lambda x: x[1], reverse=True,
        )
        drivers = [t.capitalize() for t, _ in contributors[:4]] or ["Market exposure", "Liquidity profile"]
        signal_density = min(1.0, sum(hits.values()) / 12)
        confidence = round(0.74 + 0.2 * signal_density, 2)

        mitigation = []
        for t, _ in contributors:
            if t in MITIGATION_MAP and MITIGATION_MAP[t] not in mitigation:
                mitigation.append(MITIGATION_MAP[t])
        if not mitigation:
            mitigation = ["Maintain diversification and monitor exposure with periodic stress tests."]
        mitigation = mitigation[:4]

        findings = [
            f"Overall risk profile for {subject} assessed as {category} (score {score:.0f}/100).",
            f"Detected {sum(1 for t in hits if RISK_TERMS[t] > 0)} adverse and "
            f"{sum(1 for t in hits if RISK_TERMS[t] < 0)} mitigating signal type(s).",
            "Top drivers: " + ", ".join(drivers) + ".",
        ]
        return {
            "subject": subject, "risk_score": round(score, 1), "risk_category": category,
            "key_findings": findings, "risk_drivers": drivers, "mitigation": mitigation,
            "confidence": confidence, "model": self.model,
        }

    # ----- Compliance -----
    def review_compliance(self, text: str, framework: str) -> Dict:
        lower = text.lower()
        frameworks, findings = [], []
        total_cov = 0.0
        for name, terms in FRAMEWORKS.items():
            weight_hit = sum(w for term, w in terms.items() if term in lower)
            weight_max = sum(terms.values())
            coverage = round(100 * weight_hit / weight_max, 1)
            status = "Strong" if coverage >= 60 else "Partial" if coverage >= 25 else "Gap"
            frameworks.append({"name": name, "coverage": coverage, "status": status})
            total_cov += coverage
            findings.append(f"{name}: {status.lower()} coverage ({coverage:.0f}%).")

        score = round(min(98, 45 + total_cov / len(FRAMEWORKS) * 0.55 + 15), 1)
        level = "Low" if score >= 80 else "Medium" if score >= 60 else "High"
        gaps = [f["name"] for f in frameworks if f["status"] != "Strong"]
        recommendations = []
        if "AML" in gaps:
            recommendations.append("Define explicit AML monitoring thresholds and SAR escalation workflow.")
        if "KYC" in gaps:
            recommendations.append("Document risk-based KYC/CDD and re-verification cadence for high-risk customers.")
        if "GDPR" in gaps:
            recommendations.append("Add data-retention schedule and data-subject access/erasure procedure.")
        if "SOC 2" in gaps:
            recommendations.append("Formalise access controls and an immutable audit trail for SOC 2.")
        if not recommendations:
            recommendations.append("Controls are well covered; schedule periodic independent review.")

        return {
            "compliance_score": score, "risk_level": level, "frameworks": frameworks,
            "findings": findings, "recommendations": recommendations,
            "human_review": level != "Low", "model": self.model,
        }


ai_engine = AIEngine()
