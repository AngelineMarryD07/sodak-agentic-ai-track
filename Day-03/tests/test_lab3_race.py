"""Lab 3 — two runs booking the same slot; one wins cleanly."""
import threading

from app.memory import RunStore
from app.placement_db import PlacementDb
from app.providers import ModelTurn, PositionalMock, ToolCall
from app.worker import Worker


def race_mock(student):
    return PositionalMock([
        ModelTurn(text=None, tool_calls=[ToolCall("apply_to_drive", {"student_id": student, "drive_id": 2})]),
        ModelTurn(text=None, tool_calls=[ToolCall("book_interview_slot", {"student_id": student, "slot_id": 3})]),
        ModelTurn(text="Done."),
    ])


def test_two_workers_two_runs_one_slot(db_files, clock):
    agent, place = db_files
    s1, s2 = RunStore(agent, clock), RunStore(agent, clock)
    p1, p2 = PlacementDb(place), PlacementDb(place)
    r1 = s1.enqueue(s1.create_thread("22IT017"), "Apply to TCS and book slot 3", "mock")
    r2 = s2.enqueue(s2.create_thread("22CS045"), "Apply to TCS and book slot 3", "mock")

    w1 = Worker(s1, p1, race_mock("22IT017"), worker_id="w1")
    w2 = Worker(s2, p2, race_mock("22CS045"), worker_id="w2")
    out = []
    barrier = threading.Barrier(2)

    def run(worker):
        barrier.wait()
        out.append(worker.run_once())

    a = threading.Thread(target=run, args=(w1,))
    b = threading.Thread(target=run, args=(w2,))
    a.start(); b.start(); a.join(); b.join()

    assert sorted(x[0] for x in out) == sorted([r1, r2])
    assert all(x[1] == "succeeded" for x in out)
    results = []
    for store, rid in ((s1, r1), (s2, r2)):
        results += [step["result"] for step in store.get_run(rid)["steps"]
                    if step["kind"] == "tool" and step["tool_name"] == "book_interview_slot"]
    assert sorted(r.get("status", r.get("error")) for r in results) == ["booked", "slot_taken"]
    assert p1.conn.execute("SELECT student_id FROM interview_slot WHERE id = 3").fetchone()[0] in (1, 2)


def test_truly_concurrent_claims_have_one_winner(db_files):
    _, place = db_files
    setup = PlacementDb(place)
    setup.create_application(1, 2)
    setup.create_application(2, 2)
    version = setup.slot_version(3)
    barrier = threading.Barrier(8)
    results = []
    lock = threading.Lock()

    def claim(i):
        db = PlacementDb(place)
        barrier.wait()
        won = db.claim_slot(3, 1 if i % 2 == 0 else 2, version)
        with lock:
            results.append(won)
        db.conn.close()

    threads = [threading.Thread(target=claim, args=(i,)) for i in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert setup.slot_version(3) == version + 1
