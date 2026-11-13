"""La URL de pruebas no autoriza eliminar recursos preexistentes."""

from uuid import uuid4

import pytest

from tests.conftest import qdrant as qdrant_fixture


def alias(qdrant, name, collection):
    qdrant.call(
        "POST",
        "/collections/aliases",
        json={"actions": [{"create_alias": {"alias_name": name, "collection_name": collection}}]},
    )


def test_fixture_preserves_preexisting_collections_and_aliases(qdrant):
    existing = "ocd_" + uuid4().hex
    qdrant.create(existing)
    alias(qdrant, "lector_preexistente", existing)
    probe = qdrant_fixture.__wrapped__()
    inner = next(probe)
    candidate = "ocd_" + uuid4().hex
    inner.create(candidate)
    alias(inner, "ocd_actual", candidate)
    with pytest.raises(StopIteration):
        next(probe)
    assert qdrant.collections() == {existing}
    assert qdrant.aliases() == {"lector_preexistente": existing}


def test_fixture_skips_existing_production_alias_without_mutation(qdrant):
    existing = "ocd_" + uuid4().hex
    qdrant.create(existing)
    alias(qdrant, "ocd_actual", existing)
    with pytest.raises(pytest.skip.Exception):
        next(qdrant_fixture.__wrapped__())
    assert qdrant.target() == existing
    assert qdrant.collections() == {existing}
