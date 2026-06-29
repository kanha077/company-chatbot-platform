def parse_form_data(form_data: dict) -> str:
    """
    Converts a structured form dictionary into a readable text document for embedding.
    """
    parts = []
    
    # Company Details
    parts.append(f"Company Name: {form_data.get('company_name', '')}")
    parts.append(f"Industry: {form_data.get('industry', '')}")
    parts.append(f"Founded Year: {form_data.get('founded_year', '')}")
    parts.append(f"Headquarters: {form_data.get('headquarters', '')}")
    parts.append(f"Website: {form_data.get('website', '')}")
    
    # About
    parts.append(f"\nAbout the Company:\n{form_data.get('description', '')}")
    parts.append(f"Mission: {form_data.get('mission', '')}")
    parts.append(f"Vision: {form_data.get('vision', '')}")
    parts.append(f"Core Values: {form_data.get('core_values', '')}")
    
    # Products & Services
    parts.append("\nProducts and Services:")
    for prod in form_data.get('products', []):
        parts.append(f"- {prod.get('name')}: {prod.get('description')} (Price: {prod.get('price')}). Features: {prod.get('features')}")
        
    # Support
    parts.append(f"\nSupport Email: {form_data.get('support_email', '')}")
    parts.append(f"Support Phone: {form_data.get('support_phone', '')}")
    parts.append(f"Support Hours: {form_data.get('support_hours', '')}")
    
    # Policies
    parts.append(f"\nRefund Policy: {form_data.get('refund_policy', '')}")
    parts.append(f"Privacy Policy: {form_data.get('privacy_policy', '')}")
    parts.append(f"Terms of Service: {form_data.get('terms_of_service', '')}")
    
    # FAQs
    parts.append("\nFrequently Asked Questions (FAQs):")
    for faq in form_data.get('faqs', []):
        parts.append(f"Q: {faq.get('question')}\nA: {faq.get('answer')}")
        
    return "\n".join(parts)
