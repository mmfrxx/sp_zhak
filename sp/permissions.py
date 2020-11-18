from rest_framework import permissions
from ourplatform.models import Project

class AdminOnly(permissions.BasePermission):
    def has_permissions(self, request):
        return (
            self.request.user.status == "admin"
            or self.request.user.is_superuser
        )

class IsActive(permissions.BasePermission):
    def has_object_permission(self, request, *args,**kwargs):
        return self.request.user.is_active 
        
class IsManagerOwnerAdminTeamLead(permissions.BasePermission):
    def has_object_permission(self, request):
        project_pk = request.data.get('pk')
        user = request.user
        if project_pk:
            project = Project.objects.get(pk=project_pk)
            return (
                user.is_manager
                or user.is_organizationOwner 
                or user.is_admin 
                or user.id == project.team_lead.id
            )
        return False