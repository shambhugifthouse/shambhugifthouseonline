from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import UserProfile, AuditLog, log_action

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.set_expiry(2592000)  # 30 days active session persistence
            log_action(user, "User Login", "Authentication", f"User {username} logged in successfully", request)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'dashboard:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            log_action(None, "Failed Login Attempt", "Authentication", f"Attempted username: {username}", request)

    return render(request, 'login.html')


@login_required
def logout_view(request):
    username = request.user.username
    log_action(request.user, "User Logout", "Authentication", f"User {username} logged out", request)
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('auth:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'change_password':
            old_pass = request.POST.get('old_password')
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')

            if not request.user.check_password(old_pass):
                messages.error(request, "Current password is incorrect.")
            elif new_pass != confirm_pass:
                messages.error(request, "New passwords do not match.")
            elif len(new_pass) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
            else:
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)
                log_action(request.user, "Password Change", "Authentication", "Password changed successfully", request)
                messages.success(request, "Password updated successfully!")
                return redirect('auth:profile')

    return render(request, 'settings.html', {'active_tab': 'profile'})


from shambhu_pos.email_utils import send_password_reset_email

def password_reset_request_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    # Directly find the primary admin user or account with email 'thepranit.19@gmail.com'
    user = User.objects.filter(Q(email__iexact='thepranit.19@gmail.com') | Q(username='admin')).first()
    if not user:
        user = User.objects.filter(is_superuser=True).first()

    if user:
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        host_domain = request.get_host()
        reset_url = f"https://{host_domain}/auth/reset-password/{uid}/{token}/"

        target_email = "thepranit.19@gmail.com"

        # Dispatch non-blocking template-driven email via email_utils
        send_password_reset_email(user, reset_url)

        log_action(user, "Password Reset Link Sent", "Authentication", f"Initiated password reset for {target_email}", request)
        messages.success(request, f"🔑 Password reset link sent to {target_email}! Please check your email inbox.")
    else:
        messages.error(request, "Admin account not found.")

    return redirect('auth:login')


def password_reset_confirm_view(request, uidb64, token):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_pass = request.POST.get('new_password', '').strip()
            confirm_pass = request.POST.get('confirm_password', '').strip()

            if len(new_pass) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
            elif new_pass != confirm_pass:
                messages.error(request, "Passwords do not match.")
            else:
                user.set_password(new_pass)
                user.save()
                log_action(user, "Password Reset Success", "Authentication", f"Password reset completed for user {user.username}", request)
                messages.success(request, f"Password for '{user.username}' reset successfully! Please log in with your new password.")
                return redirect('auth:login')

        return render(request, 'password_reset_confirm.html', {'valid_link': True, 'user_obj': user})
    else:
        return render(request, 'password_reset_confirm.html', {'valid_link': False})

