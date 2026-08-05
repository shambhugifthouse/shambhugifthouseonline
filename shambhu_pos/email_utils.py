import logging
import threading
import time
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_email_async(
    subject: str,
    template_name: str,
    context: dict,
    recipient_list: list,
    from_email: str = None,
    reply_to: list = None,
    attachments: list = None  # List of tuples: (filename, content_bytes, mimetype)
):
    """
    Spawns a non-blocking background daemon thread to render HTML/text templates,
    attach files (PDFs, receipts), and dispatch email with deliverability headers.
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

            # 3. Deliverability headers
            headers = {
                'Reply-To': reply_to_addresses[0],
                'X-Auto-Response-Suppress': 'OOF, AutoReply',
            }

            # 4. Dispatch to each recipient individually for 100% fault-tolerant delivery
            for recipient in recipient_list:
                try:
                    msg = EmailMultiAlternatives(
                        subject=clean_subject,
                        body=text_content,
                        from_email=sender,
                        to=[recipient],
                        headers=headers,
                    )
                    msg.attach_alternative(html_content, "text/html")

                    # Attach files if provided (e.g. PDF Financial Reports)
                    if attachments:
                        for attachment in attachments:
                            filename, content_bytes, mimetype = attachment
                            msg.attach(filename, content_bytes, mimetype)

                    sent_count = msg.send(fail_silently=False)
                    logger.info("Email '%s' sent successfully to %s", clean_subject, recipient)
                except Exception as exc:
                    logger.error("Failed to send email '%s' to %s: %s", clean_subject, recipient, str(exc), exc_info=True)
        except Exception as main_exc:
            logger.error("Error in email worker process: %s", str(main_exc), exc_info=True)

    # Spawn daemon thread for instant non-blocking return
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


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


def send_profit_report_pdf_email(pdf_bytes: bytes, recipient_list=None):
    """
    Helper utility to dispatch Overall Profit & Personal Services PDF Report to shambhugifthouse1@gmail.com.
    """
    if not recipient_list:
        recipient_list = ['shambhugifthouse1@gmail.com', 'thepranit.19@gmail.com']

    ref_id = int(time.time()) % 100000
    subject = f"Overall Profit & Personal Services PDF Report - Shambhu Gift House [Ref #{ref_id}]"
    now_str = timezone.now().strftime("%B %d, %Y - %I:%M %p")
    filename = f"Shambhu_Gift_House_Profit_Report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    context = {
        'site_name': 'Shambhu Gift House POS',
        'generated_at': now_str,
    }

    send_email_async(
        subject=subject,
        template_name='pdf_report_email.html',
        context=context,
        recipient_list=recipient_list,
        attachments=[(filename, pdf_bytes, 'application/pdf')],
    )
