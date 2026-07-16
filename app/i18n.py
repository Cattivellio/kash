from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "es": {
        # App
        "app_name": "Kash",
        "app_tagline": "Controla tu dinero, simple y rápido",

        # Onboarding
        "onboarding_title": "Bienvenido a Kash",
        "onboarding_subtitle": "¿Cómo te llamas?",
        "onboarding_name_placeholder": "Tu nombre",
        "onboarding_button": "Empezar",
        "onboarding_locale_label": "Idioma",

        # Nav
        "nav_dashboard": "Inicio",
        "nav_income": "Ingresos",
        "nav_expenses": "Gastos",
        "nav_history": "Historial",

        # Dashboard
        "dashboard_title": "Resumen del mes",
        "dashboard_income": "Ingresos",
        "dashboard_expense": "Gastos",
        "dashboard_balance": "Balance",
        "dashboard_recent": "Últimos registros",
        "dashboard_empty": "Aún no hay registros",

        # Forms
        "form_name": "Nombre",
        "form_name_placeholder": "Ej: Venta de producto",
        "form_amount": "Monto",
        "form_amount_placeholder": "0.00",
        "form_date": "Fecha",
        "form_time": "Hora",
        "form_method": "Método de pago",
        "form_note": "Nota (opcional)",
        "form_note_placeholder": "Detalles adicionales...",
        "form_submit_add": "Agregar",
        "form_submit_save": "Guardar",
        "form_cancel": "Cancelar",

        # Payment methods
        "method_cash": "Efectivo",
        "method_card": "Tarjeta",
        "method_zelle": "Zelle",

        # Record kinds
        "kind_income": "Ingreso",
        "kind_expense": "Gasto",

        # History
        "history_title": "Historial",
        "history_filter_kind": "Tipo",
        "history_filter_all": "Todos",
        "history_filter_from": "Desde",
        "history_filter_to": "Hasta",
        "history_filter_method": "Método",
        "history_apply": "Filtrar",
        "history_clear": "Limpiar",
        "history_empty": "No se encontraron registros",
        "history_count": "{n} registros",

        # Actions
        "action_edit": "Editar",
        "action_delete": "Eliminar",
        "action_confirm_delete": "¿Eliminar este registro?",

        # Footer
        "footer_text": "Kash · tu dinero, simple",

        # Months
        "month_1": "Enero",
        "month_2": "Febrero",
        "month_3": "Marzo",
        "month_4": "Abril",
        "month_5": "Mayo",
        "month_6": "Junio",
        "month_7": "Julio",
        "month_8": "Agosto",
        "month_9": "Septiembre",
        "month_10": "Octubre",
        "month_11": "Noviembre",
        "month_12": "Diciembre",

        # Misc
        "sign_out": "Cerrar sesión",
        "no_records": "Sin registros",
        "currency_symbol": "$",
    },
    "en": {
        # App
        "app_name": "Kash",
        "app_tagline": "Track your money, simple and fast",

        # Onboarding
        "onboarding_title": "Welcome to Kash",
        "onboarding_subtitle": "What's your name?",
        "onboarding_name_placeholder": "Your name",
        "onboarding_button": "Get started",
        "onboarding_locale_label": "Language",

        # Nav
        "nav_dashboard": "Home",
        "nav_income": "Income",
        "nav_expenses": "Expenses",
        "nav_history": "History",

        # Dashboard
        "dashboard_title": "Monthly summary",
        "dashboard_income": "Income",
        "dashboard_expense": "Expenses",
        "dashboard_balance": "Balance",
        "dashboard_recent": "Recent records",
        "dashboard_empty": "No records yet",

        # Forms
        "form_name": "Name",
        "form_name_placeholder": "Ex: Product sale",
        "form_amount": "Amount",
        "form_amount_placeholder": "0.00",
        "form_date": "Date",
        "form_time": "Time",
        "form_method": "Payment method",
        "form_note": "Note (optional)",
        "form_note_placeholder": "Additional details...",
        "form_submit_add": "Add",
        "form_submit_save": "Save",
        "form_cancel": "Cancel",

        # Payment methods
        "method_cash": "Cash",
        "method_card": "Card",
        "method_zelle": "Zelle",

        # Record kinds
        "kind_income": "Income",
        "kind_expense": "Expense",

        # History
        "history_title": "History",
        "history_filter_kind": "Type",
        "history_filter_all": "All",
        "history_filter_from": "From",
        "history_filter_to": "To",
        "history_filter_method": "Method",
        "history_apply": "Filter",
        "history_clear": "Clear",
        "history_empty": "No records found",
        "history_count": "{n} records",

        # Actions
        "action_edit": "Edit",
        "action_delete": "Delete",
        "action_confirm_delete": "Delete this record?",

        # Footer
        "footer_text": "Kash · your money, simple",

        # Months
        "month_1": "January",
        "month_2": "February",
        "month_3": "March",
        "month_4": "April",
        "month_5": "May",
        "month_6": "June",
        "month_7": "July",
        "month_8": "August",
        "month_9": "September",
        "month_10": "October",
        "month_11": "November",
        "month_12": "December",

        # Misc
        "sign_out": "Sign out",
        "no_records": "No records",
        "currency_symbol": "$",
    },
}


def t(locale: str, key: str, **kwargs: str | int) -> str:
    lang = STRINGS.get(locale, STRINGS["es"])
    val = lang.get(key, key)
    if kwargs:
        return val.format(**kwargs)
    return val
