def build_command_group(click_group, commands_map: dict[callable, str]):

    for cmd_func, name in commands_map.items():
        click_group.add_command(cmd_func, name)

    return click_group
