from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
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
