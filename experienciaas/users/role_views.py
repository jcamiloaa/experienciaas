from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import RoleApplication, SupplierProfile, OrganizerProfile, User
from .role_forms import (
    RoleApplicationForm, 
    OrganizerApplicationForm, 
    SupplierApplicationForm,
    SupplierProfileForm,
    OrganizerProfileForm
)


# User Role Application Views
@login_required
def apply_for_role(request):
    """View for users to apply for organizer or supplier roles."""
    # Check if user can apply for any role
    can_apply_organizer = request.user.can_apply_for_organizer
    can_apply_supplier = request.user.can_apply_for_supplier
    
    if not can_apply_organizer and not can_apply_supplier:
        messages.warning(request, _('No tienes roles disponibles para aplicar en este momento.'))
        return redirect('users:detail', pk=request.user.id)
    
    if request.method == 'POST':
        form = RoleApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            messages.success(
                request, 
                _('Tu aplicación para el rol de {} ha sido enviada. '
                  'Te notificaremos cuando sea revisada.').format(
                    application.get_role_display()
                )
            )
            return redirect('users:detail', pk=request.user.id)
    else:
        form = RoleApplicationForm(user=request.user)
    
    return render(request, 'users/apply_for_role.html', {
        'form': form,
        'can_apply_organizer': can_apply_organizer,
        'can_apply_supplier': can_apply_supplier,
    })


@login_required
def apply_for_organizer(request):
    """Specific view for organizer applications."""
    if not request.user.can_apply_for_organizer:
        messages.warning(request, _('No puedes aplicar para el rol de organizador en este momento.'))
        return redirect('users:detail', pk=request.user.id)
    
    if request.method == 'POST':
        form = OrganizerApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            messages.success(
                request, 
                _('Tu aplicación para organizador ha sido enviada. '
                  'Te notificaremos cuando sea revisada.')
            )
            return redirect('users:detail', pk=request.user.id)
    else:
        form = OrganizerApplicationForm(user=request.user)
    
    return render(request, 'users/apply_for_organizer.html', {'form': form})


@login_required
def apply_for_supplier(request):
    """Specific view for supplier applications."""
    if not request.user.can_apply_for_supplier:
        messages.warning(request, _('No puedes aplicar para el rol de proveedor en este momento.'))
        return redirect('users:detail', pk=request.user.id)
    
    if request.method == 'POST':
        form = SupplierApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            messages.success(
                request, 
                _('Tu aplicación para proveedor ha sido enviada. '
                  'Te notificaremos cuando sea revisada.')
            )
            return redirect('users:detail', pk=request.user.id)
    else:
        form = SupplierApplicationForm(user=request.user)
    
    return render(request, 'users/apply_for_supplier.html', {'form': form})


# User Profile Management Views
@login_required
def manage_organizer_profile(request):
    """View for users to manage their organizer profile."""
    if not request.user.is_organizer:
        messages.error(request, _('No tienes permisos de organizador.'))
        return redirect('users:detail', pk=request.user.id)
    
    profile = request.user.organizer_profile
    
    if request.method == 'POST':
        form = OrganizerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil de organizador actualizado correctamente.'))
            return redirect('users:organizer_profile', slug=profile.slug)
    else:
        form = OrganizerProfileForm(instance=profile)
    
    return render(request, 'users/manage_organizer_profile.html', {
        'form': form,
        'profile': profile
    })


@login_required
def manage_supplier_profile(request):
    """View for users to manage their supplier profile."""
    if not request.user.is_supplier:
        messages.error(request, _('No tienes permisos de proveedor.'))
        return redirect('users:detail', pk=request.user.id)
    
    profile = request.user.supplier_profile
    
    if request.method == 'POST':
        form = SupplierProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil de proveedor actualizado correctamente.'))
            return redirect('users:supplier_profile', slug=profile.slug)
    else:
        form = SupplierProfileForm(instance=profile)
    
    return render(request, 'users/manage_supplier_profile.html', {
        'form': form,
        'profile': profile
    })


# Public Profile Views
def supplier_profile(request, slug):
    """Public view for supplier profiles."""
    profile = get_object_or_404(SupplierProfile, slug=slug, is_public=True, status='approved')
    
    return render(request, 'users/supplier_profile.html', {
        'profile': profile,
        'user': profile.user
    })


def suppliers_list(request):
    """Public view listing all approved suppliers."""
    suppliers = SupplierProfile.objects.filter(
        status='approved',
        is_public=True
    ).order_by('company_name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(company_name__icontains=search) |
            Q(company_description__icontains=search) |
            Q(industry__icontains=search)
        )
    
    # Industry filter
    industry = request.GET.get('industry')
    if industry:
        suppliers = suppliers.filter(industry=industry)
    
    # Pagination
    paginator = Paginator(suppliers, 12)
    page_number = request.GET.get('page')
    suppliers_page = paginator.get_page(page_number)
    
    # Get all industries for filter
    industries = SupplierProfile.INDUSTRY_CHOICES
    
    return render(request, 'users/suppliers_list.html', {
        'suppliers': suppliers_page,
        'industries': industries,
        'current_search': search,
        'current_industry': industry,
    })


# Admin Views for Role Management
@staff_member_required
def admin_role_applications(request):
    """Admin view to manage role applications."""
    applications = RoleApplication.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    # Filter by role
    role = request.GET.get('role')
    if role:
        applications = applications.filter(role=role)
    
    # Search
    search = request.GET.get('search')
    if search:
        applications = applications.filter(
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(motivation__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)
    
    return render(request, 'users/admin/role_applications.html', {
        'applications': applications_page,
        'status_choices': RoleApplication.STATUS_CHOICES,
        'role_choices': RoleApplication.ROLE_CHOICES,
        'current_status': status,
        'current_role': role,
        'current_search': search,
    })


@staff_member_required
def admin_review_role_application(request, application_id):
    """Admin view to review a specific role application."""
    application = get_object_or_404(RoleApplication, id=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if action == 'approve':
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_notes = admin_notes
            application.save()
            
            # Grant the role to the user
            if application.role == 'organizer':
                application.user.is_staff = True
                application.user.save()
                
                # Create organizer profile if it doesn't exist
                if not hasattr(application.user, 'organizer_profile'):
                    OrganizerProfile.objects.create(user=application.user)
                
                messages.success(request, _(
                    'Aplicación aprobada. {} ahora es organizador.'
                ).format(application.user.name or application.user.email))
            
            elif application.role == 'supplier':
                # Create supplier profile
                SupplierProfile.objects.create(
                    user=application.user,
                    company_name=application.user.name or f"Empresa de {application.user.email}",
                    status='approved',
                    approved_at=timezone.now(),
                    reviewed_by=request.user,
                    application_reason=application.motivation
                )
                
                messages.success(request, _(
                    'Aplicación aprobada. {} ahora es proveedor.'
                ).format(application.user.name or application.user.email))
        
        elif action == 'reject':
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.admin_notes = admin_notes
            application.rejection_reason = rejection_reason
            application.save()
            
            messages.success(request, _('Aplicación rechazada.'))
        
        elif action == 'under_review':
            application.status = 'under_review'
            application.admin_notes = admin_notes
            application.save()
            
            messages.success(request, _('Aplicación marcada como en revisión.'))
        
        return redirect('users:admin_role_applications')
    
    return render(request, 'users/admin/review_role_application.html', {
        'application': application
    })


@staff_member_required
def admin_supplier_profiles(request):
    """Admin view to manage supplier profiles."""
    profiles = SupplierProfile.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        profiles = profiles.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        profiles = profiles.filter(
            Q(company_name__icontains=search) |
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(profiles, 20)
    page_number = request.GET.get('page')
    profiles_page = paginator.get_page(page_number)
    
    return render(request, 'users/admin/supplier_profiles.html', {
        'profiles': profiles_page,
        'status_choices': SupplierProfile.STATUS_CHOICES,
        'current_status': status,
        'current_search': search,
    })


@staff_member_required
def admin_manage_supplier_profile(request, profile_id):
    """Admin view to manage a supplier profile."""
    profile = get_object_or_404(SupplierProfile, id=profile_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            profile.status = 'approved'
            profile.approved_at = timezone.now()
            profile.reviewed_by = request.user
            profile.admin_notes = admin_notes
            profile.save()
            
            messages.success(request, _('Perfil de proveedor aprobado.'))
        
        elif action == 'reject':
            profile.status = 'rejected'
            profile.reviewed_by = request.user
            profile.reviewed_at = timezone.now()
            profile.admin_notes = admin_notes
            profile.rejection_reason = request.POST.get('rejection_reason', '')
            profile.save()
            
            messages.success(request, _('Perfil de proveedor rechazado.'))
        
        elif action == 'suspend':
            profile.status = 'suspended'
            profile.admin_notes = admin_notes
            profile.save()
            
            messages.success(request, _('Perfil de proveedor suspendido.'))
        
        return redirect('users:admin_supplier_profiles')
    
    return render(request, 'users/admin/manage_supplier_profile.html', {
        'profile': profile
    })


# API Views for AJAX functionality
@login_required
def check_role_availability(request):
    """AJAX view to check if user can apply for specific roles."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'can_apply_organizer': request.user.can_apply_for_organizer,
            'can_apply_supplier': request.user.can_apply_for_supplier,
            'is_organizer': request.user.is_organizer,
            'is_supplier': request.user.is_supplier,
            'pending_organizer': request.user.has_pending_organizer_application,
            'pending_supplier': request.user.has_pending_supplier_application,
        }
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
