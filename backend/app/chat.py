from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .llm import ModelClient, ModelError, TokenUsage
from .models import ChatEvidence, ChatRequest, ChatResponse, ModelRun, ResearchReport
from .ontology import OntologyFact, ReportOntology, build_report_ontology, facts_for_question, validated_facts
from .security import PUBLIC_RESEARCH_MODEL_BOUNDARY, validate_public_chat_text


class ChatState(TypedDict, total=False):
    report: ResearchReport
    request: ChatRequest
    question: str
    history: list[dict[str, str]]
    ontology: ReportOntology
    answer: str
    fact_ids: list[str]
    suggested_questions: list[str]
    usage: TokenUsage
    model_used: bool
    fallback_reason: str
    response: ChatResponse


def default_suggestions(ticker: str) -> list[str]:
    return [
        f"Why did {ticker} receive this valuation verdict?",
        "How does revenue growth compare with the selected peers?",
        "What are the biggest evidence limitations?",
    ]


def deterministic_answer(report: ResearchReport, ontology: ReportOntology, question: str) -> tuple[str, list[OntologyFact]]:
    facts = facts_for_question(ontology, question)
    text = question.lower()
    by_id = ontology.by_id

    if any(word in text for word in ("buy", "sell", "trade", "place an order", "execute")):
        chosen = [by_id["report.verdict"], by_id["report.methodology"]]
        answer = "Ledger is a read-only research aid and cannot place or recommend a trade. The report’s screening verdict is shown as context, but it is not personal investment advice or an order instruction."
        return answer, chosen
    if any(word in text for word in ("forecast", "next quarter", "next year", "price target", "future revenue")):
        chosen = [by_id["financial.basis"], by_id["report.methodology"]]
        answer = f"The active report contains historical filing-derived evidence on a {by_id['financial.basis'].value} basis. It does not contain a forecast or price target, so I cannot provide that figure from this evidence set."
        return answer, chosen
    if any(word in text for word in ("risk", "downside", "break", "concern")):
        chosen = [by_id[f"risk.{index}"] for index in range(1, min(4, len(report.risks)) + 1)]
        answer = "The report flags: " + " ".join(f"{index}. {fact.value}" for index, fact in enumerate(chosen, start=1))
        return answer, chosen
    if any(word in text for word in ("peer", "compare", "competitor", "versus", " vs")):
        chosen = [fact for fact in facts if fact.category == "peers" and fact.fact_id.endswith((".revenue_growth", ".price_to_sales"))]
        rows: dict[str, dict[str, str]] = {}
        for fact in chosen:
            ticker = fact.fact_id.split(".")[1].upper()
            rows.setdefault(ticker, {})[fact.fact_id.rsplit(".", 1)[-1]] = fact.value
        answer = "On the report’s selected comparison set, " + "; ".join(
            f"{ticker} has {values.get('revenue_growth', 'unavailable')} revenue growth and {values.get('price_to_sales', 'unavailable')} P/S"
            for ticker, values in rows.items()
        ) + ". This is a relative screen; business mix and accounting comparability can differ."
        return answer, chosen
    if any(word in text for word in ("confidence", "reliable", "limitation", "method")):
        chosen = [by_id[key] for key in ("report.confidence", "financial.basis", "report.methodology")]
        answer = f"Confidence is {chosen[0].value}. The report uses {chosen[1].value}. {chosen[2].value}"
        return answer, chosen
    if any(word in text for word in ("source", "filing", "evidence", "cite", "where", "document")):
        chosen = [fact for fact in ontology.facts if fact.fact_id == "financial.basis" or fact.category == "sources"][:7]
        answer = f"The financial basis is {by_id['financial.basis'].value}. The evidence ledger contains " + ", ".join(fact.label for fact in chosen[1:]) + "."
        return answer, chosen
    if any(word in text for word in ("revenue", "growth", "margin", "cash", "debt", "financial", "flow")):
        chosen = [fact for fact in facts if fact.category == "financials"]
        answer = "The active report shows " + "; ".join(f"{fact.label.lower()}: {fact.value}" for fact in chosen) + "."
        return answer, chosen
    if "basis" in text:
        chosen = [by_id[key] for key in ("report.confidence", "financial.basis", "report.methodology")]
        answer = f"Confidence is {chosen[0].value}. The report uses {chosen[1].value}. {chosen[2].value}"
        return answer, chosen
    if any(word in text for word in ("valuation", "valued", "price", "multiple", "undervalued", "expensive", "fair", "verdict")):
        keys = ("report.verdict", "report.confidence", "valuation.price", "valuation.pe", "valuation.price_to_sales", "valuation.fcf_yield")
        chosen = [by_id[key] for key in keys]
        answer = (
            f"The report’s deterministic screen classifies {report.ticker} as {chosen[0].value} with {chosen[1].value.lower()} confidence. "
            f"At {chosen[2].value}, it shows {chosen[3].value} P/E, {chosen[4].value} P/S, and {chosen[5].value} FCF yield. "
            "This is a peer screen rather than an intrinsic-value estimate or price target."
        )
        return answer, chosen

    chosen = [by_id[key] for key in ("report.verdict", "report.confidence", "report.summary", "financial.basis")]
    answer = f"{report.ticker} is screened as {chosen[0].value} with {chosen[1].value.lower()} confidence. {chosen[2].value} The evidence basis is {chosen[3].value}."
    return answer, chosen


async def guard_input(state: ChatState) -> ChatState:
    PUBLIC_RESEARCH_MODEL_BOUNDARY.enforce()
    question = validate_public_chat_text(state["request"].question)
    history = [
        {"role": message.role, "content": validate_public_chat_text(message.content)}
        for message in state["request"].history
    ]
    return {"question": question, "history": history}


async def assemble_context(state: ChatState) -> ChatState:
    return {"ontology": build_report_ontology(state["report"])}


async def generate_answer(state: ChatState) -> ChatState:
    report = state["report"]
    ontology = state["ontology"]
    model = ModelClient()
    if not model.enabled:
        answer, facts = deterministic_answer(report, ontology, state["question"])
        return {
            "answer": answer,
            "fact_ids": [fact.fact_id for fact in facts],
            "suggested_questions": default_suggestions(report.ticker),
            "usage": TokenUsage(),
            "model_used": False,
            "fallback_reason": "No OPENAI_API_KEY configured; used the deterministic report answerer.",
        }
    try:
        result, usage = await model.answer_report_question(
            question=state["question"],
            history=state["history"],
            ontology=ontology.prompt_packet(),
        )
        return {
            "answer": result["answer"],
            "fact_ids": result["fact_ids"],
            "suggested_questions": result["suggested_questions"],
            "usage": usage,
            "model_used": True,
        }
    except ModelError as exc:
        answer, facts = deterministic_answer(report, ontology, state["question"])
        return {
            "answer": answer,
            "fact_ids": [fact.fact_id for fact in facts],
            "suggested_questions": default_suggestions(report.ticker),
            "usage": TokenUsage(),
            "model_used": False,
            "fallback_reason": str(exc),
        }


async def verify_answer(state: ChatState) -> ChatState:
    report = state["report"]
    ontology = state["ontology"]
    facts = validated_facts(ontology, state.get("fact_ids", []))
    if not facts:
        answer, facts = deterministic_answer(report, ontology, state["question"])
        state["answer"] = answer
        state["model_used"] = False
        state["fallback_reason"] = "The model response did not cite a valid report fact; used the deterministic report answerer."

    citation_indexes: list[int] = []
    for fact in facts:
        for source_id in fact.source_ids:
            if source_id.startswith("source."):
                try:
                    index = int(source_id.split(".", 1)[1]) - 1
                except ValueError:
                    continue
                if 0 <= index < len(report.citations) and index not in citation_indexes:
                    citation_indexes.append(index)

    model = ModelClient()
    usage = state.get("usage", TokenUsage())
    response = ChatResponse(
        run_id=report.run_id,
        ticker=report.ticker,
        answer=state["answer"][:1800],
        evidence=[ChatEvidence(fact_id=fact.fact_id, label=fact.label, value=fact.value, source_ids=list(fact.source_ids)) for fact in facts],
        citations=[report.citations[index] for index in citation_indexes[:6]],
        suggested_questions=state.get("suggested_questions", default_suggestions(report.ticker))[:3],
        model=ModelRun(
            enabled=state.get("model_used", False),
            provider=model.provider,
            name=model.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            fallback_reason=state.get("fallback_reason"),
        ),
    )
    return {"response": response}


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("guard", guard_input)
    graph.add_node("context", assemble_context)
    graph.add_node("generate", generate_answer)
    graph.add_node("verify", verify_answer)
    graph.add_edge(START, "guard")
    graph.add_edge("guard", "context")
    graph.add_edge("context", "generate")
    graph.add_edge("generate", "verify")
    graph.add_edge("verify", END)
    return graph.compile()


CHAT_GRAPH = build_chat_graph()


async def run_report_chat(report: ResearchReport, request: ChatRequest) -> ChatResponse:
    result: dict[str, Any] = await CHAT_GRAPH.ainvoke({"report": report, "request": request})
    return ChatResponse.model_validate(result["response"])
