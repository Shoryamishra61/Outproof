"""Normalize explicit aggregate cost evidence; labels and menu items are not bounds."""

from ground_rule.models import CompilationFailure, Evidence, Money, PriceConfidence, PriceEvidence


def mandatory_price(
    record: Evidence | None, confidence: PriceConfidence
) -> PriceEvidence | CompilationFailure:
    """The supplying source must explicitly cover every mandatory expense.

    Freshness, provenance, scope and cap eligibility are still checked by policy.
    This function never fills missing amounts/currencies or upgrades confidence.
    """
    if record is None:
        return PriceEvidence(confidence="UNKNOWN", lower=None, upper=None, scope=None, evidence=())
    record = Evidence.model_validate(record)
    if confidence == PriceConfidence.UNKNOWN and record.value is None:
        return PriceEvidence(
            confidence="UNKNOWN", lower=None, upper=None, scope=None, evidence=(record,)
        )
    fields = {
        "currency_code",
        "lower_minor_units",
        "upper_minor_units",
        "scope",
        "covers_all_mandatory_costs",
    }
    value = record.value
    try:
        if (
            record.field != "price"
            or not isinstance(value, dict)
            or set(value) != fields
            or value["covers_all_mandatory_costs"] is not True
        ):
            raise ValueError("No complete mandatory price bound")
        price = PriceEvidence(
            confidence=confidence,
            lower=Money(
                currency_code=value["currency_code"], minor_units=value["lower_minor_units"]
            ),
            upper=Money(
                currency_code=value["currency_code"], minor_units=value["upper_minor_units"]
            ),
            scope=value["scope"],
            evidence=(record,),
        )
        if price.confidence == PriceConfidence.VERIFIED and price.lower != price.upper:
            raise ValueError("Verified exact aggregate cannot have different bounds")
        return price
    except (ValueError, TypeError):
        return CompilationFailure(
            code="NO_BUDGET_VERIFIED_PLAN",
            message="Source does not supply a complete typed mandatory cost bound",
        )
