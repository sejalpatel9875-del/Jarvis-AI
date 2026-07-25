import asyncio
import main
import contextlib

async def runner():
    loop = asyncio.get_running_loop()
    # Run the synchronous main loop in a separate thread so it doesn't block the async loop
    task = loop.run_in_executor(None, main.main)
    # Schedule cancellation in 8 seconds
    await asyncio.sleep(8)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("\n[Test] Main loop cancelled successfully.")
    except Exception as e:
        print(f"\n[Test] Main loop encountered exception: {e}")

if __name__ == "__main__":
    print("--- Starting Automated Boot Test of main.py ---")
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        pass
    print("--- Boot Test Complete ---")
