"""Shared stub view for features not yet implemented."""

from apps.ai_tasks.base import BaseAIRunView


def make_stub_view(feature_name: str):
    class StubAIRunView(BaseAIRunView):
        feature = feature_name
        task_fn = None

    StubAIRunView.__name__ = f"{feature_name.title()}RunView"
    return StubAIRunView
