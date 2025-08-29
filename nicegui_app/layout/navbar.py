from nicegui import ui

def navbar():
    with ui.header().classes('bg-black text-white'):
        ui.label('NiceGUI').classes('text-xl font-bold ml-4')
        with ui.row().classes('ml-auto mr-4'):
            ui.link('Home', '/').classes('text-white hover:underline')
            ui.link('Demo', '/demo').classes('text-white hover:underline')
