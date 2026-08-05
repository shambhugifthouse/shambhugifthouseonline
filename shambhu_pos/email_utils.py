import logging
import threading
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_email_async(
    subject: str,
    template_name: str,
    context: dict,
    recipient_list: list,
    from_email: str = None,
    reply_to: list = None
):
    """
    Spawns a non-blocking background daemon thread to render HTML/text templates
    and dispatch email with anti-spam deliverability headers.
    """
    sender = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
    host_user = getattr(settings, 'EMAIL_HOST_USER', '')

    # Clean subject line (remove emojis / unexpected linebreaks for transactional compliance)
    clean_subject = "".join(c for c in subject if ord(c) < 0x10000 and c not in ('\r', '\n')).strip()

    # Silently skip if recipient or host configuration is missing
    if not recipient_list or not host_user:
        logger.warning("Skipping email dispatch: recipient list or EMAIL_HOST_USER is not configured.")
        return

    def _worker():
        try:
            # 1. Render HTML template and construct clear text fallback containing links
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)
            if 'reset_url' in context and context['reset_url'] not in text_content:
                text_content += f"\n\nDirect Reset Link: {context['reset_url']}"

            # 2. Extract reply-to address
            reply_to_addresses = reply_to or [host_user]

            # 3. Anti-spam & deliverability headers
            headers = {
                'Reply-To': reply_to_addresses[0],
                'X-Auto-Response-Suppress': 'OOF, AutoReply',
                'Precedence': 'bulk',
            }

            # 4. Construct EmailMultiAlternatives object
            msg = EmailMultiAlternatives(
                subject=clean_subject,
                body=text_content,
                from_email=sender,
                to=recipient_list,
                headers=headers,
            )
            msg.attach_alternative(html_content, "text/html")

            # 5. Send email via SMTP
            sent_count = msg.send(fail_silently=False)
            logger.info("Email '%s' sent successfully to %s (sent count: %d)", clean_subject, recipient_list, sent_count)
        except Exception as exc:
            logger.error("Failed to send email '%s' to %s: %s", clean_subject, recipient_list, str(exc), exc_info=True)

    # Spawn daemon thread for instant non-blocking return
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


import time

def send_password_reset_email(user, reset_url: str):
    """
    Helper utility to dispatch transactional Password Reset email.
    """
    target_email = getattr(user, 'email', '') or 'thepranit.19@gmail.com'
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'Shambhu Gift House POS',
    }
    # Unique subject reference to prevent Gmail conversation thread collapsing
    ref_id = int(time.time()) % 100000
    subject = f"Reset Your Password - Shambhu Gift House [Ref #{ref_id}]"
    send_email_async(
        subject=subject,
        template_name='password_reset_email.html',
        context=context,
        recipient_list=[target_email],
    )
