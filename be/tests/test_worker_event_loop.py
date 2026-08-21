import asyncio

from be.workers import ai_task_worker


async def _loop_identifier() -> int:
    return id(asyncio.get_running_loop())


def test_worker_reuses_one_event_loop_for_multiple_tasks():
    previous_loop = ai_task_worker._worker_loop
    ai_task_worker._worker_loop = None
    try:
        first_loop_id = ai_task_worker.run_in_worker_loop(_loop_identifier())
        second_loop_id = ai_task_worker.run_in_worker_loop(_loop_identifier())
        assert first_loop_id == second_loop_id
    finally:
        if ai_task_worker._worker_loop and not ai_task_worker._worker_loop.is_closed():
            ai_task_worker._worker_loop.close()
        ai_task_worker._worker_loop = previous_loop
