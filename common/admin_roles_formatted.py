backend_admin_roles = {
    "Admin": {
        "roles": {'View admins': 'allow-to-get-admin', 'Create admins': 'allow-to-create-admins',
                  'Delete admins': 'allow-to-delete-admins', 'Update admins': 'allow-to-update-admins',
                  'Get admin details': 'allow-to-get-admin-details',
                  'Change admin password': 'allow-to-change-admin-password'}},
    "Admin Groups": {
        "roles": {'Get admin group': 'allow-to-get-admin-group', 'Delete admin group': 'allow-to-delete-admin-group',
                  'Create admin group': 'allow-to-create-admin-group',
                  'Update admin group': 'allow-to-update-admin-group',
                  'Get admin group details': 'allow-to-get-admin-group-details'}},
    "Tenants": {"roles": {'Delete tenants': 'allow-to-delete-tenants', 'Update tenants': 'allow-to-update-tenants',
                          'Get tenants': 'allow-to-get-tenants',
                          'Get tenant details': 'allow-to-get-tenant-details'}},
    "Tenants Stats": {
        "roles": {'Get tenant feature stats': 'allow-to-get-tenant-feature-stats',
                  'Get tenant user stats': 'allow-to-get-tenant-user-stats'}},
    "Camera": {
        "roles": {'Set camera status': 'allow-to-set-camera-status'}},
    "Login History": {
        "roles": {'Log admin login': 'allow-to-log-admin-login', 'Log admin logout': 'allow-to-log-admin-logout',
                  'Get admin login history': 'allow-to-get-admin-login-history'}}}

frontend_admin_roles = {
    "Admin": {"roles": {"View admin tab": "allow-to-view-admin-tab",
                        "Add admin": "allow-to-add-admin",
                        "Edit admin": "allow-to-edit-admin",
                        "Delete admin": "allow-to-delete-admin",
                        "Reset admin password": "allow-to-reset-admin-password"
                        }},
    "Tenant": {"roles": {"View tenant tab": "allow-to-view-tenant-tab",
                         "Add tenant": "allow-to-add-tenant",
                         "Edit tenant": "allow-to-edit-tenant",
                         "Delete tenant": "allow-to-delete-tenant"
                         }},
    "Admin Groups": {"roles": {"View admin groups tab": "allow-to-view-admin-groups-tab",
                               "Add admin groups": "allow-to-add-admin-groups",
                               "Edit admin groups": "allow-to-edit-admin-groups",
                               "Delete admin groups": "allow-to-delete-admin-groups"
                               }},
    "Admin Profile": {"roles": {"View admin profile": "allow-to-view-admin-profile",
                                "Change password": "allow-to-change-admin-password",
                                "Edit admin profile details": "allow-to-edit-admin-profile-details",
                                "Change admin profile picture": "allow-to-change-profile-picture"
                                }},
    "Dashboad": {"roles": {"View dashboard tab": "allow-to-view-dashboard-tab",
                           "View tenant category chart": "allow-to-tenant-category-chart",
                           "View active tenant count": "allow-to-view-active-tenant-count",
                           "Allow to view user count chart": "allow-to-view-user-count-chart",
                           "Allow to view tenant categor features": "allow-to-view-tenant-category-features"
                           }},

    "Login History": {"roles": {"View admin login history tab": "allow-to-view-admin-login-history-tab"
                                }},
}
