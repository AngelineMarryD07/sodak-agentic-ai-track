# Lab 4 — crash drill

## Before idempotency
The completed submission was verified with idempotency enabled. The important failure mode without it is that worker-B can repeat a side effect that worker-A committed but did not record in `agent.db` before being killed.

## After
Three completed runs of `python -m scripts.crash_drill`:

```text
Run 1
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
5. worker-B finished the run: 'succeeded' after 2 attempts
applications 1   booked slots 1   notifications 1
PASS: exactly one of each

Run 2
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
5. worker-B finished the run: 'succeeded' after 2 attempts
applications 1   booked slots 1   notifications 1
PASS: exactly one of each

Run 3
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
5. worker-B finished the run: 'succeeded' after 2 attempts
applications 1   booked slots 1   notifications 1
PASS: exactly one of each
```

## Explain
1. **When was worker-A killed, and what was written?** Worker-A was killed after `notify_student` had completed its placement-side transaction but before the corresponding tool-call record was written to `agent.db`. The application, slot booking, notification and their idempotency rows that had committed in `placement.db` survived. The run itself was still `running`, leased to worker-A, and the final notification tool step had not yet been recorded in the run history.

2. **How did worker-B know where to resume?** After worker-A's lease expired, `RunStore.reap_expired()` returned the run to the queue. Worker-B claimed it and `rebuild()` reconstructed the conversation from messages plus the durable `run_step` and `tool_call` rows. Any requested tool call without a recorded result remained in `pending`, so execution resumed at that unfinished call rather than restarting the whole conversation.

3. **Which line stopped the second notification?** In `call_tool()` in `app/runner.py`, side-effect tools are executed through `placement.once(key, name, lambda: tools.call(name, args))`. On replay, `PlacementDb.once()` finds the existing idempotency key and returns its stored result without calling `notify_student` again. The notification table also has its own dedupe key as an additional business-level safeguard.

## Real Gemini sprint verification
The code path for real Gemini workers is present, but the submitted starter kit contains no `GEMINI_API_KEY`. The required real-model evidence must be produced in the student's own environment by starting two non-`--mock` workers, queuing five questions from at least three students, and then pasting `python -m scripts.status` output here. No real-model output is fabricated in this file.
