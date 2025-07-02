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


import re # Import re for regex operations

def get_llm_response(prompt):
    settings = get_llm_settings()

    # Attempt to extract item context if query seems related to stock
    erp_context_str = ""
    # Basic keyword detection and item extraction
    # This is a simplified approach and can be significantly improved with proper NLU
    stock_keywords = ["stock", "inventory", "how many", "available", "quantity", "count of"]
    # Regex to find potential item codes (alphanumeric, dashes, dots) or quoted names
    item_pattern = r"([A-Za-z0-9\-\.]+)|(\"[^\"]+\")|(\'[^\']+\')"

    prompt_lower = prompt.lower()
    found_item_identifier = None

    if any(keyword in prompt_lower for keyword in stock_keywords):
        matches = re.findall(item_pattern, prompt)
        for match_group in matches:
            # match_group is a tuple, e.g., ('ITEM-001', '', '') or ('', '"Item Name"', '')
            # Iterate through the tuple to find the non-empty match
            for potential_identifier in match_group:
                if potential_identifier:
                    # Remove quotes if present
                    found_item_identifier = potential_identifier.strip("\"'")
                    break
            if found_item_identifier:
                break # Found the first likely item identifier

        if found_item_identifier:
            erp_data = get_item_stock_context(found_item_identifier)
            if erp_data and not erp_data.startswith("Item '") and not erp_data.startswith("No stock found") and not erp_data.startswith("No item identifier"):
                erp_context_str = f"ERPNext Data Context:\n{erp_data}\n\nUser Query:\n"
            elif erp_data: # Item not found or no stock, pass this info to LLM
                 erp_context_str = f"ERPNext Data Context:\n{erp_data}\n\nUser Query:\n"


    # Prepend context to the original prompt if available
    final_prompt = erp_context_str + prompt

    try:
        if settings.llm_provider == "ollama":
            if 'ollama' not in globals():
                frappe.throw(_("Ollama library is not installed. Please install it using: pip install ollama"))

            client = ollama.Client(host=settings.ollama_api_url)
            response = client.chat(
                model=settings.model if settings.model != "Auto" else "llama2", # Default to llama2 if Auto for ollama
                messages=[{"role": "user", "content": final_prompt}]
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
                model=model_to_use, messages=[{"role": "user", "content": final_prompt}]
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

# --- ERPNext Data Integration Functions ---
def get_item_stock_context(item_identifier):
    """
    Fetches stock context for a given item identifier (code or name).
    Returns a formatted string with stock details or an error message.
    """
    if not item_identifier:
        return "No item identifier provided."

    # Check if identifier is an item code or item name
    item_filter_field = "name" if frappe.db.exists("Item", item_identifier) else "item_name"

    item = frappe.db.get_value("Item", {item_filter_field: item_identifier}, ["name", "item_name", "stock_uom"], as_dict=True)

    if not item:
        return f"Item '{item_identifier}' not found."

    item_code = item.get("name")
    item_name = item.get("item_name")
    stock_uom = item.get("stock_uom")

    bin_entries = frappe.get_all(
        "Bin",
        filters={"item_code": item_code, "actual_qty": [">", 0]},
        fields=["warehouse", "actual_qty"]
    )

    if not bin_entries:
        return f"No stock found for item: {item_name} ({item_code})."

    context_parts = [f"Stock for {item_name} ({item_code}) - UOM: {stock_uom}:"]
    for entry in bin_entries:
        context_parts.append(f"- {entry.actual_qty} units in Warehouse '{entry.warehouse}'.")

    return "\n".join(context_parts)
# --- End ERPNext Data Integration Functions ---

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
