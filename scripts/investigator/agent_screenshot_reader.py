"""User-attached-only agent access to the existing governed vision reader."""
from .onboarding import Conflict, digest


def reader(workspace, ticket_id):
    def read(image_id):
        ticket = workspace.smart_intake.tickets.get(ticket_id)['ticket']
        allowed = {c['attachment']['id'] for c in ticket.get('comments', [])
                   if c['actor'] == 'USER' and c.get('attachment')}
        review = ticket.get('evidence', {}).get('screenshot_review')
        if review and review.get('attachment'): allowed.add(review['attachment']['id'])
        if image_id not in allowed: raise Conflict('Agent screenshot is not attached by this ticket user')
        custom = getattr(workspace, 'agent_screenshot_reader', None)
        if custom is not None: return custom(image_id)
        result = workspace.screenshots.read({'attachment_id': image_id,
            'request_key': 'agent-vision:' + digest({'ticket': ticket_id, 'image': image_id})[:64]})
        if result['status'] != 'EXTRACTED': raise Conflict('Agent screenshot transcription is unavailable')
        return {'image_sha256': result['attachment']['sha256'], 'receipt_id': result['id'],
            'visible_text': result['extraction']['visible_text'], 'items': None,
            'interpretation_verified': False}
    return read
