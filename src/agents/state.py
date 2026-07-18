import operator
from typing import Annotated, TypedDict


class CompetitorIntelState(TypedDict):
    competitor_name: str
    user_request: str
    research_data: str
    internal_data: str
    draft_report: str
    final_report: str
    revision_count: Annotated[int, operator.add]
