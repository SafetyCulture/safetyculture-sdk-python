import SafetyPy as sp

api_token = ''
scClient = sp.sc_client(api_token)

lastSuccessful = scClient.get_last_successful()
results = scClient.discover_audits(modified_after = lastSuccessful)

print results['total']

for audit in results['audits']:
    audit_id = audit['audit_id']
    print audit_id
    pdf_doc = scClient.get_pdf(audit_id)
    scClient.write_pdf(pdf_doc, audit_id)
    scClient.set_last_successful(audit['modified_at'])
