from commands import command, console


@command("/exit", "Esci dalla CLI")
async def cmd_exit(_args):
    console.print("\n[dim]Che la fortuna vi arrida, avventurieri.[/dim]")
    raise SystemExit(0)
