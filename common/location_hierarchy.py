
from anytree import Node
from sqlalchemy import and_

import common.global_variables
from common.database.location import Location


def build_location_tree(all_locations):
    #  create tree from database objects
    all_locations.sort(key=lambda x: x.location_type)
    root_node_key = all_locations[0].location_key
    location_tree = Node(root_node_key)
    key_to_node = {root_node_key: location_tree}
    for location in all_locations[1:]:
        if location.parent_key in key_to_node:
            key_to_node[location.location_key] = Node(location.location_key, parent=key_to_node[location.parent_key])
    return location_tree, key_to_node


def get_common_parent(db, tenant_key, locations):
    lowest_boundary = 100000
    highest_boundary = 0

    for location in common.global_variables.db_locations[tenant_key]:
        if location.location_key in locations:
            if lowest_boundary > location.lower_bound:
                lowest_boundary = location.lower_bound
            if highest_boundary < location.upper_bound:
                highest_boundary = location.upper_bound
    common_parent = db.query(Location.location_key).filter(
        and_(Location.lower_bound <= lowest_boundary, Location.upper_bound >= highest_boundary)).order_by(
        Location.location_type.desc()).first()[0]
    return common_parent
