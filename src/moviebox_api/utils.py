import asyncio


def build_command_group(click_group, commands_map: dict[callable, str]):

    for cmd_func, name in commands_map.items():
        click_group.add_command(cmd_func, name)

    return click_group


def get_event_loop():
    try:
        event_loop = asyncio.get_event_loop()
    except RuntimeError:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
    return event_loop
