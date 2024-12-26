def get_customer_data(customer_id):
    """Retrieve mock CRM data for a given customer ID."""
    crm_data = {
        "123": {"name": "John Doe", "history": ["Bought laptop", "Inquired about warranty"]},
        "456": {"name": "Jane Smith", "history": ["Requested quote for software", "Negotiated price"]},
    }
    return crm_data.get(customer_id, {})
