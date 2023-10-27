def run_iter(iter_count: int, AI: bool, VISUAL: bool):
    import time

    from state import State, Action
    from physics import physics_transform_state
    if AI:
        from ai import get_ai_action, get_total_reward, save_model
    if VISUAL:
        from visual import render_state

    state = State()
    action = Action(0, 0)

    def perf_track(func, name):
        start = time.perf_counter()
        value = func()
        print(f"{name} - {round((time.perf_counter() - start) * 1000)} ms, ", end="")
        return value

    try:
        frame_count = 0
        for i in range(iter_count):
            frame_count += 1
            print(f"F{frame_count}, ", end="")
            perf_track(lambda: physics_transform_state(state, action), "physics")
            if VISUAL:
                action = perf_track(lambda: render_state(state), "render")
            if AI:
                action = perf_track(lambda: get_ai_action(state), "ai")
                print(f"total reward = {get_total_reward()}")
            else:
                print()
    finally:
        state.save_to_file()
        if AI:
            save_model()

if __name__ == "__main__":
    run_iter(10000, True, True)