from datetime import datetime

from sqlalchemy import and_

import common.global_variables
from apimodel.request_models import Struct, UserGroupInfo, UserInfo
from common.database.admin_role_map import AdminRolesAdminGroupMap
from common.database.admin_roles import AdminRole
from common.database.member import Member
from common.database.member_projects import MemberProject
from common.database.member_titles import MemberTitle
from common.database.tenant import Tenant
from common.database.tenant_es_index import TenantEsIndex
from common.database.user import User
from common.database.user_group import UserGroup
from common.database.user_group_project_scopes import UserGroupProjectScope
from common.database.user_group_scopes import UserGroupScope
from common.database.user_group_title_scopes import UserGroupTitleScope
from common.database.user_role_map import UserRolesUserGroupMap
from common.database.user_roles import UserRole
from common.string_constants import  user_title_attr, user_project_attr, \
    modified_date_col, created_date_col, user_key_string
from exceptions.custom_exceptions import ItemNotFoundException
from security.authentication_service import get_password_hash
from services.db_crud_operations import retrieve, bulk_create, update_bulk

project_keys_scope = "project_keys"
title_keys_scope = "title_keys"

def update_roles(application_roles, role_type, current_application_roles, current_role_groups, current_role_keys, role):
    objects_to_edit = []
    objects_to_add = []
    for role_group in application_roles:
        roles = application_roles[role_group]["roles"]
        for description in roles:
            script_role = roles[description]
            if script_role in current_application_roles:
                if current_application_roles[script_role] != current_role_groups[role_group]:
                    # user role is in db, but user role group is incorrect, so update
                    item_edit_data = {"role_group_key": current_role_groups[role_group],
                                      "user_role_key": current_role_keys[script_role],
                                      modified_date_col: datetime.utcnow()}
                    objects_to_edit.append(item_edit_data)
            else:
                # user role is not in the db, so create in the db
                item_data = Struct()
                setattr(item_data, role, script_role)
                item_data.role_type = role_type
                item_data.role_group_key = current_role_groups[role_group]
                item_data.role_description = description
                objects_to_add.append(item_data)
    return objects_to_edit, objects_to_add


def sync_application_roles(db, role_model, role_group_model, backend_roles, frontend_roles, role_key, role):
    """
    Updates database with application role and role group values in project file
    :param role_model: UserRole or AdminRole
    :param role_group_model: UserRoleGroup or AdminRolGroup
    :param backend_roles: user or admin roles
    :param frontend_roles: user or admin roles
    :param db: db session
    :return:
    """
    # load role groups from DB and store in memory
    select_fields = [role_group_model.role_group,
                     role_group_model.role_group_key]
    user_role_groups, _ = retrieve(db, role_group_model, None, True, select_fields)
    current_role_groups = {}
    for user_role_group in user_role_groups:
        if user_role_group.role_group not in current_role_groups:
            current_role_groups[user_role_group.role_group] = user_role_group.role_group_key

    # load application roles from DB and store in memory
    select_fields = [getattr(role_model, role_key), getattr(role_model, role), role_model.role_description,
                     role_group_model.role_group,
                     role_group_model.role_group_key, role_model.role_type]
    filters = role_model.role_group_key == role_group_model.role_group_key
    current_roles, _ = retrieve(db, role_model, None, filters, select_fields)

    current_backend_application_roles = {}
    current_backend_role_keys = {}
    current_frontend_application_roles = {}
    current_frontend_role_keys = {}
    for current_role in current_roles:
        if current_role.role_type == "B":
            current_backend_application_roles[getattr(current_role, role)] = current_role.role_group_key
            current_backend_role_keys[getattr(current_role, role)] = getattr(current_role, role_key)
        if current_role.role_type == "F":
            current_frontend_application_roles[getattr(current_role, role)] = current_role.role_group_key
            current_frontend_role_keys[getattr(current_role, role)] = getattr(current_role, role_key)
    objects_to_add = []

    # Find missing role groups that need to be added
    for role_group in {**backend_roles, **frontend_roles}:
        if role_group not in current_role_groups:
            item_data = Struct()
            item_data.role_group = role_group
            objects_to_add.append(item_data)
    objects_added = bulk_create(db, role_group_model, objects_to_add)
    for new_group in objects_added:
        current_role_groups[new_group.role_group] = new_group.role_group_key

    # Find DB entries that need to be added/ modified for backend roles
    objects_to_edit, objects_to_add = update_roles(backend_roles, "B", current_backend_application_roles,
                                                   current_role_groups, current_backend_role_keys, role)
    bulk_create(db, role_model, objects_to_add)
    update_bulk(db, role_model, objects_to_edit)

    # Find DB entries that need to be added/ modified for frontend roles
    objects_to_edit, objects_to_add = update_roles(frontend_roles, "F", current_frontend_application_roles,
                                                   current_role_groups, current_frontend_role_keys, role)

    bulk_create(db, role_model, objects_to_add)
    update_bulk(db, role_model, objects_to_edit)


def map_all_roles_to_admin(db, tenant_key):
    """
    Updates database user_role_user_group_mapping
    :param tenant_key: signed in tenant's tenant key
    :param db: db session
    :return:
    """

    # load application role keys from DB and store in memory
    all_role_keys = retrieve(db, UserRole, None, True, [UserRole.user_role_key])[0]

    # Add mappings to this tenant's Admin user group for all updated roles
    try:
        user_group_key = \
            retrieve(db, User, None, and_(User.tenant_key == tenant_key, User.default == 1), [User.user_group_key])[0][
                0][0]
    except IndexError:
        user_group_key = 1
    current_user_role_maps = \
        retrieve(db, UserRolesUserGroupMap, None, UserRolesUserGroupMap.user_group_key == user_group_key,
                 [UserRolesUserGroupMap.user_role_key])[0]
    current_user_role_maps = [role[0] for role in current_user_role_maps]
    new_maps = []
    for user_role_key in [role[0] for role in all_role_keys]:
        if user_role_key not in current_user_role_maps:
            user_role_user_group_map_data = UserRolesUserGroupMap(user_group_key, user_role_key)
            new_maps.append(user_role_user_group_map_data)
    bulk_create(db, UserRolesUserGroupMap, new_maps)


def map_all_admin_roles_to_admin(db):
    """
    Updates database admin_role_admin_group_mapping
    :param db: db session
    :return:
    """

    # load application role keys from DB and store in memory
    all_role_keys = retrieve(db, AdminRole, None, True, [AdminRole.admin_role_key])[0]

    # Add mappings to admin's admin group for all updated roles
    admin_group_key = 1
    current_admin_role_maps = \
        retrieve(db, AdminRolesAdminGroupMap, None, AdminRolesAdminGroupMap.admin_group_key == admin_group_key,
                 [AdminRolesAdminGroupMap.admin_role_key])[0]
    current_admin_role_maps = [role[0] for role in current_admin_role_maps]
    new_maps = []
    for admin_role_key in [role[0] for role in all_role_keys]:
        if admin_role_key not in current_admin_role_maps:
            admin_role_admin_group_map_data = AdminRolesAdminGroupMap(admin_group_key, admin_role_key)
            new_maps.append(admin_role_admin_group_map_data)
    bulk_create(db, AdminRolesAdminGroupMap, new_maps)


def get_tenant_guest_group_keys(db, all_tenant_keys):
    tenant_guest_group_keys = {}
    guest_user_group = "Guest"
    guest_tenant_user_groups = db.query(UserGroup).filter(UserGroup.user_group == guest_user_group).all()

    guest_user_group_tenant_keys = []
    for user_group in guest_tenant_user_groups:
        tenant_key = user_group.tenant_key
        guest_user_group_tenant_keys.append(tenant_key)
    tenants_without_guest_group = [tenant_key for tenant_key in all_tenant_keys if tenant_key not
                                   in guest_user_group_tenant_keys]
    db_records_to_add = []
    for tenant_key in tenants_without_guest_group:
        user_group_data = {"user_group": guest_user_group, "tenant_key": tenant_key}
        user_group_data = UserGroupInfo(**user_group_data)
        db_records_to_add.append(user_group_data)
    bulk_create(db, UserGroup, db_records_to_add)
    guest_tenant_user_groups = db.query(UserGroup).filter(UserGroup.user_group == guest_user_group).all()
    for user_group in guest_tenant_user_groups:
        tenant_key = user_group.tenant_key
        tenant_guest_group_keys[tenant_key] = user_group.user_group_key
    return tenant_guest_group_keys


def add_members_to_users(db):
    all_tenant_keys = [tenant.tenant_key for tenant in db.query(Tenant).all()]
    tenant_guest_group_keys = get_tenant_guest_group_keys(db, all_tenant_keys)
    all_members = db.query(Member).all()
    tenant_members = {all_tenant_keys[k]: [] for k in range(len(all_tenant_keys))}
    for member in all_members:
        tenant_members[member.tenant_key].append(member)

    all_users = db.query(User).all()

    tenant_users = {all_tenant_keys[k]: [] for k in range(len(all_tenant_keys))}
    for user in all_users:
        tenant_users[user.tenant_key].append(user)
    objects_to_create = []
    objects_to_edit = []
    for tenant_key in all_tenant_keys:
        for member in tenant_members[tenant_key]:
            existing_users = tenant_users[tenant_key]
            existing_user_logins = {}
            for existing_user in existing_users:
                existing_user_logins[existing_user.user_login_id] = existing_user.user_key
            tenant_guest_group_key = tenant_guest_group_keys[member.tenant_key]
            if member.member_id in existing_user_logins.keys():
                user_data = {user_key_string: existing_user_logins[member.member_id], "first_name": member.first_name,
                             "last_name": member.last_name,
                             user_title_attr: member.title_id, "dob": member.dob, "gender": member.gender,
                             user_project_attr: member.project_id, "location_key": member.location,
                             "tenant_key": member.tenant_key, "email": member.email,
                             "mobile_number": member.mobile_number,
                             modified_date_col: member.modified_datetime,
                             "vector": member.vector}
                objects_to_edit.append(user_data)
            else:
                user_data = {"member_id": member.member_id, "first_name": member.first_name,
                             "user_password": get_password_hash(member.member_id),
                             "user_group_key": tenant_guest_group_key,
                             "last_name": member.last_name, "user_login_id": member.member_id,
                             user_title_attr: member.title_id, "dob": member.dob, "gender": member.gender,
                             user_project_attr: member.project_id, "location_key": member.location,
                             "tenant_key": member.tenant_key, "email": member.email,
                             "mobile_number": member.mobile_number,
                             created_date_col: member.created_datetime, modified_date_col: member.modified_datetime,
                             "is_active": member.is_active, "enable_login": False, "vector": member.vector}
                objects_to_create.append(UserInfo(**user_data))
    bulk_create(db, User, objects_to_create)
    update_bulk(db, User, objects_to_edit)


def mark_is_active_users(db):
    objects_to_edit = []
    for user in db.query(User).all():
        user_data = {user_key_string: user.user_key, "is_active": not user.disable}
        objects_to_edit.append(user_data)
    update_bulk(db, User, objects_to_edit)


def dissolve_db_values(db, tenant_ids):
    mappings_to_update = []
    random_string = "ABC"
    tenant_keys = [tenant.tenant_key for tenant in common.global_variables.db_tenants if tenant.tenant_id.lower() in
                   [t_id.lower() for t_id in tenant_ids.split(",")]]
    if not tenant_keys:
        raise ItemNotFoundException(db_model=Tenant)
    tenant_users = db.query(User).filter(User.tenant_key.in_(tenant_keys)).all()
    for user in tenant_users:
        mapping = {user_key_string: user.user_key}
        for attr in ("first_name", "last_name", "email", "user_login_id"):
            if getattr(user, attr):
                mapping[attr] = random_string + getattr(user, attr)
        mappings_to_update.append(mapping)
    update_bulk(db, User, mappings_to_update)

    mappings_to_update = []
    tenant_es_indices = db.query(TenantEsIndex).filter(TenantEsIndex.tenant_key.in_(tenant_keys)).all()
    for es_index in tenant_es_indices:
        mapping = {"tenant_key": es_index.tenant_key}
        for attr in ("member_logs", "api_logs", "number_plate_logs", "stranger_logs"):
            if getattr(es_index, attr):
                mapping[attr] = random_string + getattr(es_index, attr)
        mappings_to_update.append(mapping)
    update_bulk(db, TenantEsIndex, mappings_to_update)


def get_new_scopes(all_scopes, user_groups_tenant, tenant_values, scope_type, scope_class):
    scopes_to_add = []
    for scope in all_scopes:
        user_group_key = scope.user_group_key
        tenant_key = user_groups_tenant[user_group_key]
        if getattr(scope, scope_type) == "0":
            new_scope_keys = tenant_values[tenant_key]
        elif getattr(scope, scope_type) and getattr(scope, scope_type) != "-1":
            new_scope_keys = [int(key) for key in getattr(scope, scope_type).split(",")]
        else:
            continue
        for scope_key in new_scope_keys:
            scopes_to_add.append(scope_class(user_group_key, scope_key))
    return scopes_to_add


def migrate_user_group_scopes(db):
    all_scopes = retrieve(db, UserGroupScope, None, True, [UserGroupScope])[0]
    all_user_group_keys = retrieve(db, UserGroup, None, True, [UserGroup.tenant_key, UserGroup.user_group_key])[0]
    all_title_keys = retrieve(db, MemberTitle, None, True, [MemberTitle.tenant_key, MemberTitle.title_key])[0]
    all_project_keys = retrieve(db, MemberProject, None, True, [MemberProject.tenant_key, MemberProject.project_key])[
        0]
    tenant_titles = {}
    for title in all_title_keys:
        if title.tenant_key not in tenant_titles:
            tenant_titles[title.tenant_key] = [title.title_key]
        else:
            tenant_titles[title.tenant_key].append(title.title_key)
    tenant_projects = {}
    for project in all_project_keys:
        if project.tenant_key not in tenant_projects:
            tenant_projects[project.tenant_key] = [project.project_key]
        else:
            tenant_projects[project.tenant_key].append(project.project_key)
    user_groups_tenant = {}
    for user_group in all_user_group_keys:
        user_groups_tenant[user_group.user_group_key] = user_group.tenant_key

    title_scopes_to_add = get_new_scopes(all_scopes, user_groups_tenant, tenant_titles, title_keys_scope,
                                         UserGroupTitleScope)
    project_scopes_to_add = get_new_scopes(all_scopes, user_groups_tenant, tenant_projects, project_keys_scope,
                                           UserGroupProjectScope)
    bulk_create(db, UserGroupTitleScope, title_scopes_to_add)
    bulk_create(db, UserGroupProjectScope, project_scopes_to_add)
