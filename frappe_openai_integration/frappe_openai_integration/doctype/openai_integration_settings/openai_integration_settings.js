// Copyright (c) 2025, Manav Mandli and contributors
// For license information, please see license.txt

frappe.ui.form.on("OpenAI Integration Settings", {
    refresh: function(frm) {
        // Trigger the llm_provider function on load to set initial field visibility
        frm.trigger("llm_provider");
    },
    llm_provider: function(frm) {
        // Default to hiding all provider-specific fields
        frm.set_df_property("ollama_api_url", "hidden", 1);
        frm.set_df_property("api_key", "hidden", 1);

        // Show fields based on selected provider
        if (frm.doc.llm_provider === "ollama") {
            frm.set_df_property("ollama_api_url", "hidden", 0);
            // Potentially filter or set models available for Ollama
            // Example: frm.set_query("model", function() { return { filters: { "provider": "ollama" } }; });
        } else if (frm.doc.llm_provider === "openai") {
            frm.set_df_property("api_key", "hidden", 0);
            // Potentially filter or set models available for OpenAI
            // Example: frm.set_query("model", function() { return { filters: { "provider": "openai" } }; });
        }

        // Refresh the fields to apply visibility changes
        frm.refresh_field("ollama_api_url");
        frm.refresh_field("api_key");
        // frm.refresh_field("model"); // Refresh if model options are changed dynamically
    }
});
