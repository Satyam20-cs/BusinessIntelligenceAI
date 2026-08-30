from engine.kpi_engine import detect_kpi_changes
from engine.driver_engine import find_drivers
from engine.confidence_engine import calculate_confidence
from engine.action_engine import generate_actions
from engine.materiality import check_materiality
from engine.reconciliation import reconcile
from engine.unstructured_engine import analyze_feedback
from evidence.lineage import build_lineage
from ai.narrative import generate_narrative


def run_insight_pipeline(
    sales,
    inventory=None,
    customer_metrics=None,
    customer_feedback=None
):
    """
    Main InsightX AI pipeline.

    Flow:
    Detect -> Explain -> Connect -> Recommend -> Learn
    """


    kpi_changes = detect_kpi_changes(sales)

    if not kpi_changes:
        return {
            "status": "no_significant_change",
            "message": "No material KPI changes detected.",
            "insights": []
        }

    insights = []


    for change in kpi_changes:

      

        material = check_materiality(change)

        if not material:
            continue

        

        drivers = find_drivers(
            change=change,
            sales=sales,
            inventory=inventory,
            customer_metrics=customer_metrics
        )

        

        feedback_analysis = None

        if customer_feedback is not None:

            feedback_analysis = analyze_feedback(
                customer_feedback,
                change
            )

       

        reconciliation = reconcile(
            change=change,
            drivers=drivers
        )

        

        confidence = calculate_confidence(
            change=change,
            drivers=drivers,
            reconciliation=reconciliation
        )

        

        actions = generate_actions(
            change=change,
            drivers=drivers,
            confidence=confidence
        )

        

        evidence = build_lineage(
            change=change,
            drivers=drivers,
            feedback_analysis=feedback_analysis
        )

        

        narrative = generate_narrative(
            change=change,
            drivers=drivers,
            actions=actions,
            confidence=confidence,
            evidence=evidence
        )

        insights.append({
            "kpi": change,
            "drivers": drivers,
            "feedback": feedback_analysis,
            "reconciliation": reconciliation,
            "confidence": confidence,
            "actions": actions,
            "evidence": evidence,
            "narrative": narrative
        })

    return {
        "status": "success",
        "insights": insights
    }