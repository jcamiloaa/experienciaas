from django.urls import path

from .views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    organizer_profile_view,
    organizers_list_view,
    follow_organizer,
    profile_update_view,
    supplier_profile_update_view,
    admin_edit_supplier_profile_view,
    admin_role_applications_view,
    admin_supplier_profiles_view,
    admin_active_roles_view,
    approve_role_application,
    reject_role_application,
    approve_supplier_profile,
    reject_supplier_profile,
    suspend_organizer_role,
    suspend_supplier_role,
    reactivate_organizer_role,
    reactivate_supplier_role,
    revoke_organizer_role,
    revoke_supplier_role,
    activate_user_account,
    deactivate_user_account,
    promote_to_organizer,
    approve_as_supplier,
)

from .role_views import (
    apply_for_role,
    apply_for_organizer,
    apply_for_supplier,
    manage_organizer_profile,
    manage_supplier_profile,
    supplier_profile,
    suppliers_list,
    admin_role_applications,
    admin_review_role_application,
    admin_supplier_profiles,
    admin_manage_supplier_profile,
    check_role_availability,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~profile/", view=profile_update_view, name="profile_update"),
    path("~supplier-profile/", view=supplier_profile_update_view, name="supplier_profile_update"),
    path("admin/supplier-profile/<int:profile_id>/edit/", view=admin_edit_supplier_profile_view, name="admin_edit_supplier_profile"),
    
    # Role application URLs
    path("apply/", view=apply_for_role, name="apply_for_role"),
    path("apply/organizer/", view=apply_for_organizer, name="apply_for_organizer"),
    path("apply/supplier/", view=apply_for_supplier, name="apply_for_supplier"),
    
    # Profile management URLs
    path("manage/organizer/", view=manage_organizer_profile, name="manage_organizer_profile"),
    path("manage/supplier/", view=manage_supplier_profile, name="manage_supplier_profile"),
    
    # Public profile URLs
    path("organizers/", view=organizers_list_view, name="organizers_list"),
    path("organizer/<slug:slug>/", view=organizer_profile_view, name="organizer_profile"),
    path("organizer/<slug:slug>/follow/", view=follow_organizer, name="follow_organizer"),
    
    path("suppliers/", view=suppliers_list, name="suppliers_list"),
    path("supplier/<slug:slug>/", view=supplier_profile, name="supplier_profile"),
    
    # Admin URLs
    path("admin/applications/", view=admin_role_applications_view, name="admin_role_applications"),
    path("admin/applications/<int:application_id>/approve/", view=approve_role_application, name="approve_role_application"),
    path("admin/applications/<int:application_id>/reject/", view=reject_role_application, name="reject_role_application"),
    path("admin/suppliers/", view=admin_supplier_profiles_view, name="admin_supplier_profiles"),
    path("admin/suppliers/<int:profile_id>/approve/", view=approve_supplier_profile, name="approve_supplier_profile"),
    path("admin/suppliers/<int:profile_id>/reject/", view=reject_supplier_profile, name="reject_supplier_profile"),
    path("admin/roles/", view=admin_active_roles_view, name="admin_active_roles"),
    
    # Role management URLs
    path("admin/roles/<int:user_id>/suspend-organizer/", view=suspend_organizer_role, name="suspend_organizer_role"),
    path("admin/roles/<int:user_id>/suspend-supplier/", view=suspend_supplier_role, name="suspend_supplier_role"),
    path("admin/roles/<int:user_id>/reactivate-organizer/", view=reactivate_organizer_role, name="reactivate_organizer_role"),
    path("admin/roles/<int:user_id>/reactivate-supplier/", view=reactivate_supplier_role, name="reactivate_supplier_role"),
    path("admin/roles/<int:user_id>/revoke-organizer/", view=revoke_organizer_role, name="revoke_organizer_role"),
    path("admin/roles/<int:user_id>/revoke-supplier/", view=revoke_supplier_role, name="revoke_supplier_role"),
    
    # User account management URLs
    path("admin/roles/<int:user_id>/activate-account/", view=activate_user_account, name="activate_user_account"),
    path("admin/roles/<int:user_id>/deactivate-account/", view=deactivate_user_account, name="deactivate_user_account"),
    path("admin/roles/<int:user_id>/promote-organizer/", view=promote_to_organizer, name="promote_to_organizer"),
    path("admin/roles/<int:user_id>/approve-supplier/", view=approve_as_supplier, name="approve_as_supplier"),
    
    # API URLs
    path("api/check-roles/", view=check_role_availability, name="check_role_availability"),
    
    # Keep existing user detail at the end
    path("<int:pk>/", view=user_detail_view, name="detail"),
]
