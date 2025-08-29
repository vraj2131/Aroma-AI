from nicegui import ui
from layout.navbar import navbar

@ui.page('/')
def home():
    navbar()
    ui.label('Welcome to the Home Page!').classes('text-2xl mt-4')

    def on_click():
        ui.notify('You clicked Home button')
        ui.navigate.to('/demo')

    ui.button('Click Me!', on_click=on_click)
