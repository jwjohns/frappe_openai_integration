import frappe
from frappe import _
from frappe.utils import now
try:
    from openai import OpenAI
except ImportError:
    # If openai is not installed, we can still proceed if the user selects ollama
    pass

try:
    import ollama
except ImportError:
    # If ollama is not installed, we can still proceed if the user selects openai
    pass


def get_llm_settings():
    """
    Fetch LLM integration settings.
    """
    return frappe.get_single("OpenAI Integration Settings")


def get_llm_response(prompt):
    settings = get_llm_settings()

    try:
        if settings.llm_provider == "ollama":
            if 'ollama' not in globals():
                frappe.throw(_("Ollama library is not installed. Please install it using: pip install ollama"))

            client = ollama.Client(host=settings.ollama_api_url)
            response = client.chat(
                model=settings.model if settings.model != "Auto" else "llama2", # Default to llama2 if Auto for ollama
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response['message']['content']
            return answer

        elif settings.llm_provider == "openai":
            if 'OpenAI' not in globals():
                frappe.throw(_("OpenAI library is not installed. Please install it using: pip install openai"))

            client = OpenAI(api_key=settings.api_key)
            # Use "gpt-3.5-turbo" if model is "Auto" or not set for OpenAI
            model_to_use = settings.model
            if not model_to_use or model_to_use == "Auto":
                model_to_use = "gpt-3.5-turbo"

            response = client.chat.completions.create(
                model=model_to_use, messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            return answer

        else:
            frappe.throw(_("Invalid LLM provider selected in settings."))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("LLM API Error"))
        return _("Sorry, I could not process your request at this time. Error: {}").format(str(e))


@frappe.whitelist()
def ask_llm(prompt):
    answer = get_llm_response(prompt)
    return answer


@frappe.whitelist()
def save_chat_message(prompt, response):
    # Save the conversation linked with the logged in user
    doc = frappe.get_doc(
        {
            "doctype": "OpenAI Prompt Log",
            "user": frappe.session.user,
            "timestamp": now(),
            "prompt_message": prompt,
            "response_message": response,
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return True


@frappe.whitelist()
def get_chat_history():
    # Fetch saved chat messages for current user
    chats = frappe.get_all(
        "OpenAI Prompt Log",
        filters={"user": frappe.session.user},
        fields=["name", "prompt_message", "response_message", "timestamp"],
        order_by="creation asc",
        limit_page_length=10,
    )
    return chats


@frappe.whitelist()
def clear_chat_history():
    chats = frappe.get_all(
        "OpenAI Prompt Log", filters={"user": frappe.session.user}, fields=["name"]
    )
    for chat in chats:
        frappe.delete_doc("OpenAI Prompt Log", chat.name, force=True)
    return "success"
