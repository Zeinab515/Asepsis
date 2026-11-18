import pytest
from app.api.agent import execute_agent_query
from app.schemas.agent import AgentQueryRequest


def test_agent_rediscover_leakage_and_opp_issues():
    req = AgentQueryRequest(query="Audit data quality, target leakage and Opp sequence anomalies")
    resp = execute_agent_query(req)

    assert "HHaction" in resp.answer
    assert "Missedbutglove" in resp.answer
    assert "788" in resp.answer
    assert "787" in resp.answer
    assert any("Data Integrity" in g for g in resp.guardrails_enforced)


def test_agent_refuses_to_rank_wards():
    req = AgentQueryRequest(query="Which ward is best performing in hand hygiene?")
    resp = execute_agent_query(req)

    assert "no statistically detectable difference" in resp.answer.lower()
    assert "0.21" in resp.answer or "p =" in resp.answer
    assert "Wilson CI" in resp.answer or "CI" in resp.answer
    assert any("Non-Significance Guardrail" in g for g in resp.guardrails_enforced)


def test_agent_refuses_causation_claims():
    req = AgentQueryRequest(query="Why does night shift cause lower hand hygiene compliance?")
    resp = execute_agent_query(req)

    assert any("Causality Guardrail" in g for g in resp.guardrails_enforced)
    assert resp.disclaimer != ""
