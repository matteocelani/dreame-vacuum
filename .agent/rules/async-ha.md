---
trigger: always_on
---

# Async and the Home Assistant loop

Home Assistant runs this integration on one event loop. Blocking that loop stalls every integration in the user's process. These rules are correctness rules.

## Where code runs

- `async def` functions do not call blocking I/O. Blocking includes sockets and HTTP clients that are not async, `time.sleep`, `pathlib` operations that hit the disk beyond a trivial stat the standard library already cached, `open()`, crypto and map decoding that is more than a few cheap field reads, and any `python-miio` or MQTT call that waits.
- That work runs in `await hass.async_add_executor_job(...)`. Pass a named function, not a lambda that closes over a large device object by accident. Do not use the deprecated `async_add_job` for new code.
- Code already running in an executor job must not touch `hass`, entity state, the entity registry, or the coordinator. Hop back to the loop first.
- A callback invoked off the loop (an MQTT thread, a vendor SDK thread) schedules work with `hass.loop.call_soon_threadsafe`. It does not call `async_write_ha_state`, `async_set_updated_data`, or registry methods itself.

## Tasks

- Every `asyncio` task the integration creates is stored and cancelled from `async_unload_entry` or `async_will_remove_from_hass`, and the cancel path is registered with `entry.async_on_unload` when the task belongs to a config entry.
- Tasks are created with `hass.async_create_task(coro, eager_start=False)` so Home Assistant tracks them. A bare `asyncio.create_task` or `hass.loop.create_task` in new code fails review.
- Do not call `asyncio.get_event_loop()`, `asyncio.new_event_loop()`, or `loop.run_until_complete`.
- Fire-and-forget is forbidden. If nobody awaits the result, the task is still retained and its exception is logged.

## Coordinator

- One `DataUpdateCoordinator` subclass instance per config entry. It is stored at `hass.data[DOMAIN][entry.entry_id]` and removed on unload.
- Polling lives in `_async_update_data`. Entities do not poll, and they do not sleep-and-refresh.
- Transient device failure raises `UpdateFailed`. Authentication failure raises `ConfigEntryAuthFailed`. Anything else propagates. Catching those exceptions inside `_async_update_data` to return stale data fails review.
- `update_interval` is a named constant. A jitter or a backoff policy is explicit code, not a magic sleep in the caller.
- Push updates call `async_set_updated_data` on the loop. They do not also force a redundant refresh unless the push payload is partial and the docstring says so.

## Entities and services

- Entity classes subclass `CoordinatorEntity` parameterized with the coordinator type. They apply state in `_handle_coordinator_update` or in the standard property hooks. They do not subscribe to the device a second time.
- Service handlers and entity action handlers are coroutines. A handler that needs a blocking device call uses the executor, then writes state by requesting a coordinator refresh or by consuming the value the device core returned.
- `@callback` marks functions that must not await. Adding `await` to a `@callback` fails review.

## Setup

- `async_setup_entry` constructs the coordinator, awaits `async_config_entry_first_refresh`, stores the coordinator, then forwards platforms with `async_forward_entry_setups`.
- `async_unload_entry` unloads platforms, cancels tasks, drops the device listener, and pops the coordinator from `hass.data`. A listener that is not cancelled on unload is a review failure.
- No device I/O at import time. Importing the integration must not open a socket, read a credential, or start a thread.
