def business_profile(request):
    """Context processor to provide business info globally across templates."""
    try:
        from apps.authentication.models import BusinessProfile
        profile = BusinessProfile.objects.first()
        if not profile:
            profile = BusinessProfile.objects.create(
                shop_name="SHAMBHU GIFT HOUSE",
                tagline="Gifts, Toys, Stationeries, Xerox & Printing Center",
                owner_name="Shambhu Nath",
                phone="+91 9876543210",
                email="contact@shambhugifthouse.com",
                gstin="10AAAAA0000A1Z5",
                address="Main Road, Market Complex, City Center",
                receipt_header="Thank you for shopping at SHAMBHU GIFT HOUSE!",
                receipt_footer="Goods once sold can be exchanged within 7 days. No Cash Refund."
            )
    except Exception:
        profile = {
            "shop_name": "SHAMBHU GIFT HOUSE",
            "tagline": "Gifts, Toys, Stationeries, Xerox & Printing Center",
            "owner_name": "Shambhu Nath",
            "phone": "+91 9876543210",
            "email": "contact@shambhugifthouse.com",
            "gstin": "10AAAAA0000A1Z5",
            "address": "Main Road, Market Complex, City Center",
            "receipt_header": "Thank you for shopping at SHAMBHU GIFT HOUSE!",
            "receipt_footer": "Goods once sold can be exchanged within 7 days. No Cash Refund."
        }
    
    return {
        'shop': profile
    }
