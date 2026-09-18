import time  # noqa: F401  (you will time each tool call)
from collections.abc import Callable

from app.memory import ConversationStore
from app.providers import AgentError  # noqa: F401
from app.tools.placement_tools import PlacementTools

MAX_STEPS = 8

SYSTEM = """You are the Placement Assistant for an engineering college's placement cell.
You are talking to the student with roll number {student_id}. Act only for this student.
Use the tools for every fact about drives, eligibility, applications and slots; never guess.
Eligibility is decided by check_eligibility, not by you. Keep replies short and concrete."""


class Agent:
    """A small agent: one student, one conversation, the placement tools."""

    def __init__(self, provider, tools: PlacementTools, student_id: str,
                 memory: ConversationStore | None = None, thread_id: str | None = None,
                 on_step: Callable[[dict], None] | None = None):
        self.provider = provider
        self.tools = tools
        self.system = SYSTEM.format(student_id=student_id)
        self.memory = memory
        self.thread_id = thread_id
        self.on_step = on_step
        self.contents: list[dict] = []
        self.trace: list[dict] = []

        if self.memory and self.thread_id:
            self.contents = self.memory.load_history(self.thread_id)

    def _log(self, entry: dict) -> None:
        """Add one entry to the trace and tell on_step about it. (Given.)"""
        self.trace.append(entry)
        if self.on_step:
            self.on_step(entry)

    # ------------------------------------------------------------------ Part 2.1

    def run_tool(self, name: str, args: dict) -> dict:
        """Call one tool with self.tools.call(name, args). Never raise."""
        try:
            return self.tools.call(name, args)

        except NotImplementedError as exc:
            return {
                "error": "not_implemented",
                "hint": str(exc) or f"Tool {name} is not implemented yet."
            }

        except Exception as exc:
            return {
                "error": "tool_failed",
                "hint": str(exc)
            }

    # ------------------------------------------------------------------ Part 2.2

    def ask(self, text: str) -> str:
        """One user turn: loop model calls and tool calls until the model answers."""
        self.contents.append({"role": "user", "text": text})

        run_id = None

        if self.memory and self.thread_id:
           self.memory.append_message(self.thread_id, "user", text)
           run_id = self.memory.start_run(self.thread_id, "mock")

        step = 0

        while step < MAX_STEPS:
            step += 1

            try:
                turn = self.provider.generate(
                   self.system,
                   self.contents,
                   list(self.tools.functions().values())
                )
            except AgentError as exc:
                if self.memory and run_id:
                    self.memory.finish_run(run_id, "failed", exc.code)
                raise

            self._log({
                "step": step,
                "kind": "model",
                "tokens_in": turn.tokens_in,
                "tokens_out": turn.tokens_out
            })
            if self.memory and run_id:
                self.memory.record_model_step(
                     run_id,
                     step,
                     turn.tokens_in,
                     turn.tokens_out
                )

            if not turn.tool_calls:
               reply = turn.text or ""
               self.contents.append({
                 "role": "model",
                 "text": reply,
                 "raw": turn.raw
               })

               if self.memory and self.thread_id:
                 self.memory.append_message(self.thread_id, "model", reply)
               if self.memory and run_id:
                 self.memory.finish_run(run_id, "succeeded")

               return reply

            self.contents.append({
                "role": "model",
                "text": turn.text,
                "raw": turn.raw,
                "tool_calls": [
                    {
                        "name": call.name,
                        "args": call.args
                    }
                    for call in turn.tool_calls
                ]
            })

            for call in turn.tool_calls:
                started = time.perf_counter()

                result = self.run_tool(call.name, call.args)

                elapsed_ms = int((time.perf_counter() - started) * 1000)

                step += 1

                self._log({
                    "step": step,
                    "kind": "tool",
                    "tool": call.name,
                    "args": call.args,
                    "result": result,
                    "ok": "error" not in result,
                    "ms": elapsed_ms
                })
                if self.memory and run_id:
                    self.memory.record_tool_call(
                      run_id,
                      step,
                      call.name,
                      call.args,
                      result,
                      "error" not in result,
                      elapsed_ms
                    )

                self.contents.append({
                    "role": "tool",
                    "name": call.name,
                    "result": result
                })

                if step >= MAX_STEPS:
                    break

        raise AgentError("step_limit", "Agent reached the maximum number of steps.")