from nicegui import ui
from layout.navbar import navbar

form_data = []

@ui.page('/demo')
def demo():
    navbar()
    ui.label('📝 Fill the form below').classes('text-lg mt-2 text-center')

    # --- FORM ---
    with ui.row().classes('w-full justify-center mt-10'):
        with ui.card().classes('w-full max-w-md p-6 shadow-lg'):
            name = ui.input('Name').classes('w-full').props('required')
            email = ui.input('Email').classes('w-full').props('type="email" required')
            phone = ui.input('Phone').classes('w-full').props('type="tel" required')
            address = ui.textarea('Address').classes('w-full').props('required')

            def on_submit():
                if not (name.value and email.value and phone.value and address.value):
                    ui.notify('All fields are required', type='negative')
                    return

                form_data.append({
                    'name': name.value,
                    'email': email.value,
                    'phone': phone.value,
                    'address': address.value,
                })

                ui.notify('Data Saved', type='positive')
                name.value = ''
                email.value = ''
                phone.value = ''
                address.value = ''
                refresh_table()

            ui.button('Submit', on_click=on_submit).classes('mt-4 bg-blue-600 text-white')

    # --- TABLE HEADER ---
    ui.separator().classes('my-6')
    ui.label('Submitted Data').classes('text-xl text-center')

    table_container = ui.column().classes('w-full max-w-6xl mx-auto')

    def refresh_table():
        table_container.clear()

        if not form_data:
            with table_container:
                ui.label('No data yet.').classes('text-center text-gray-500 mt-4 text-base italic')
            return

        # Table Header
        with table_container:
            with ui.row().classes(
                'w-full flex-nowrap bg-blue-700 text-white font-semibold py-2 px-4 rounded-t-md shadow'
            ):
                ui.label('Name').classes('w-1/5 text-sm')
                ui.label('Email').classes('w-1/5 text-sm')
                ui.label('Phone').classes('w-1/5 text-sm')
                ui.label('Address').classes('w-1/5 text-sm')
                ui.label('Actions').classes('w-1/5 text-sm')


        # Data Rows
        for index, entry in enumerate(form_data):
            bg_class = 'bg-white' if index % 2 == 0 else 'bg-gray-50'
            with table_container:
                with ui.row().classes(
                    f'{bg_class} w-full flex-nowrap items-center py-3 px-4 hover:bg-blue-50 border-b border-gray-300 transition-all duration-200'
                ):
                    ui.label(entry['name']).classes('w-1/5 text-sm text-gray-800')
                    ui.label(entry['email']).classes('w-1/5 text-sm text-gray-800')
                    ui.label(entry['phone']).classes('w-1/5 text-sm text-gray-800')
                    ui.label(entry['address']).classes('w-1/5 text-sm text-gray-800')
                    with ui.row().classes('w-1/5 gap-3 flex-nowrap'):
                        ui.button(icon='edit', on_click=lambda e=entry: edit_entry(e)) \
                            .props('flat color=primary').classes('text-sm')
                        ui.button(icon='delete', on_click=lambda e=entry: delete_entry(e)) \
                            .props('flat color=red').classes('text-sm')




    def edit_entry(entry):
        name.value = entry['name']
        email.value = entry['email']
        phone.value = entry['phone']
        address.value = entry['address']
        form_data.remove(entry)
        refresh_table()

    def delete_entry(entry):
        form_data.remove(entry)
        ui.notify('Entry Deleted', type='warning')
        refresh_table()

    refresh_table()
