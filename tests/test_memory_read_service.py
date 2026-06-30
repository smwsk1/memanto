from unittest.mock import MagicMock

from memanto.app.services.memory_read_service import MemoryReadService


def test_search_multi_scope_builds_namespaces_from_scope_definitions():
    client = MagicMock()
    client.similarity_search.query.return_value = {"results": [], "execution_time": 0.01}
    service = MemoryReadService(client)

    result = service.search_multi_scope(
        query="deployment preference",
        scopes=[
            {"scope_type": "agent", "scope_id": "planner"},
            {"scope_type": "agent", "scope_id": "reviewer"},
        ],
    )

    assert result["searched_namespaces"] == [
        "memanto_agent_planner",
        "memanto_agent_reviewer",
    ]
    client.similarity_search.query.assert_called_once_with(
        query="deployment preference",
        namespaces=["memanto_agent_planner", "memanto_agent_reviewer"],
        top_k=10,
        threshold=None,
        kiosk_mode=False,
    )
