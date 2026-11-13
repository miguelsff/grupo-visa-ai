from uuid import uuid4

import httpx
import pytest

from ocd_ingesta.publication import Publisher


def publish(publisher, records):
    name = "ocd_" + uuid4().hex
    records = [r.model_copy(update={"ingestion_run_id": name[4:]}) for r in records]
    publisher.publish(name, records, [[1.0] + [0.0] * 1535 for _ in records])
    return name


def test_repeat_retains_active_and_predecessor(qdrant, records, tmp_path):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    second = publish(publisher, records)
    third = publish(publisher, records)
    assert qdrant.target() == third
    assert qdrant.collections() == {second, third}
    assert first not in qdrant.collections()
    # Reiniciar el objeto simula otra CLI y conserva el diario.
    restarted = Publisher(qdrant, tmp_path)
    restarted.recover()
    assert restarted.state["previous"] == second
    assert qdrant.collections() == {second, third}


def test_partial_write_keeps_alias_and_recovers(qdrant, records, tmp_path, monkeypatch):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    write = qdrant.write

    def fail(name, records, vectors):
        write(name, records[:1], vectors[:1])
        raise httpx.ReadTimeout("Fallo parcial")

    monkeypatch.setattr(qdrant, "write", fail)
    with pytest.raises(httpx.ReadTimeout):
        publish(publisher, records)
    assert qdrant.target() == first
    assert len(qdrant.collections()) == 2
    Publisher(qdrant, tmp_path).recover()
    assert qdrant.collections() == {first}


def test_mismatched_ingestion_run_is_rejected_before_write(qdrant, records, tmp_path):
    publisher = Publisher(qdrant, tmp_path)
    with pytest.raises(ValueError, match="ingestion_run_id"):
        publisher.publish("ocd_" + uuid4().hex, records, [[1.0] + [0.0] * 1535 for _ in records])
    assert qdrant.target() is None
    assert not qdrant.collections()


@pytest.mark.parametrize("applied", [True, False])
@pytest.mark.parametrize("failure", [httpx.ReadTimeout, httpx.RemoteProtocolError])
def test_uncertain_alias_result_never_deletes_active(
    qdrant, records, tmp_path, monkeypatch, applied, failure
):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    original = qdrant.switch

    def uncertain(name, old):
        if applied:
            original(name, old)
        raise failure("Respuesta perdida")

    monkeypatch.setattr(qdrant, "switch", uncertain)
    if applied:
        pending = publish(publisher, records)
        assert publisher.state["pending"] is None
    else:
        with pytest.raises(failure):
            publish(publisher, records)
        pending = publisher.state["pending"]["candidate"]
    restarted = Publisher(qdrant, tmp_path)
    restarted.recover()
    assert qdrant.target() == (pending if applied else first)
    assert qdrant.collections() == ({first, pending} if applied else {first})


def test_alias_unreadable_defers_all_cleanup(qdrant, records, tmp_path, monkeypatch):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    original = qdrant.switch
    target = qdrant.target

    def unreadable():
        raise httpx.ConnectError("Sin conexión")

    def uncertain(name, old):
        original(name, old)
        monkeypatch.setattr(qdrant, "target", unreadable)
        raise httpx.ReadTimeout("Respuesta perdida")

    monkeypatch.setattr(qdrant, "switch", uncertain)
    with pytest.raises(httpx.ConnectError):
        publish(publisher, records)
    with pytest.raises(httpx.ConnectError):
        Publisher(qdrant, tmp_path).recover()
    assert first in qdrant.collections()
    assert len(qdrant.collections()) == 2
    monkeypatch.setattr(qdrant, "target", target)
    Publisher(qdrant, tmp_path).recover()
    assert len(qdrant.collections()) == 2


def test_failed_verification_never_publishes(qdrant, records, tmp_path, monkeypatch):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    write = qdrant.write

    def missing_point(name, records, vectors):
        write(name, records[:-1], vectors[:-1])

    monkeypatch.setattr(qdrant, "write", missing_point)
    with pytest.raises(ValueError, match="incompleta"):
        publish(publisher, records)
    publisher.recover()
    assert qdrant.collections() == {first}
    assert qdrant.target() == first


def test_cleanup_protects_other_aliases_and_unowned(qdrant, records, tmp_path):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    qdrant.call(
        "POST",
        "/collections/aliases",
        json={
            "actions": [
                {"create_alias": {"alias_name": "lector_externo", "collection_name": first}}
            ]
        },
    )
    foreign = "ocd_" + uuid4().hex
    qdrant.create(foreign)
    publish(publisher, records)
    publish(publisher, records)
    assert first in qdrant.collections()
    assert foreign in qdrant.collections()


def test_alias_ack_without_change_is_not_reported_as_success(
    qdrant, records, tmp_path, monkeypatch
):
    publisher = Publisher(qdrant, tmp_path)
    first = publish(publisher, records)
    monkeypatch.setattr(qdrant, "switch", lambda name, old: None)
    with pytest.raises(ValueError, match="no quedó publicada"):
        publish(publisher, records)
    assert qdrant.target() == first
    assert qdrant.collections() == {first}
