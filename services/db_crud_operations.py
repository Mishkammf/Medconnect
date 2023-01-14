
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from exceptions.custom_exceptions import DatabaseException, \
    ItemNotFoundException, ItemsNotFoundException, DatabaseIntegrityException

created_date_col = "created_datetime"
modified_date_col = "modified_datetime"


NO_PERMISSION_FOR_TENANT_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="No permission to modify data in this tenant",
    headers={"WWW-Authenticate": "Bearer"},
)

UNABLE_TO_DELETE_ITEMS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot delete data due to referencing objects",
    headers={"WWW-Authenticate": "Bearer"},
)


def create(db, db_model, item_data):
    """
    Creates a new record in the database
    Args:
        db: database session
        db_model: ORM model of database table
        item_data: values of attributes for new record

    Returns:
        primary key value of the newly created record
    """
    try:
        item = db_model()
        for attr in item_data.__dict__:
            setattr(item, attr, getattr(item_data, attr))
        setattr(item, created_date_col, datetime.utcnow())
        setattr(item, modified_date_col, datetime.utcnow())
        db.add(item)
        db.commit()
        return item
    except IntegrityError as e:
        db.rollback()
        raise DatabaseIntegrityException(str(e), db_model=db_model)
    except IndexError as e:
        raise DatabaseException(str(e))


def bulk_create(db, db_model, item_data_list):
    """
    Creates new records in the database
    Args:
        db: database session
        db_model: ORM model of database table
        item_data_list: values of attributes for new records

    Returns:
        primary key value of the newly created record
    """
    try:

        objects_to_add = []
        for item_data in item_data_list:
            item = db_model()
            for attr in item_data.__dict__:
                setattr(item, attr, getattr(item_data, attr))
            if created_date_col not in item_data.__dict__:
                setattr(item, created_date_col, datetime.utcnow())
            if modified_date_col not in item_data.__dict__:
                setattr(item, modified_date_col, datetime.utcnow())
            objects_to_add.append(item)
        db.add_all(objects_to_add)
        db.commit()
        return objects_to_add
    except IntegrityError as e:
        db.rollback()
        raise DatabaseIntegrityException(str(e))
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def retrieve(db, db_model, query, filters, select_fields, joins=None, join_type="outerjoin", row_number=False):
    """
    Retrieves record from database table
    Args:
        db: database session
        db_model: ORM model of database table
        filters: database filters to apply
        query: Query object to determine sorting and pagination
        select_fields: Fields to select
        joins: join attributes
        join_type: join type to use. Can be one of ["outerjoin", "join"]

    Returns:
        List of records, total number of database records
    """
    if joins is None:
        joins = []
    try:
        if not query:  # no pagination or sorting
            item_list = db.query(*select_fields)
            for join_args in joins:
                item_list = getattr(item_list, join_type)(*join_args)
            item_list = item_list.filter(filters).all()
            record_count = len(item_list)
        else:
            if row_number:
                select_fields.append(func.row_number().over(order_by=
                getattr(getattr(db_model, query.sort_param), query.sort_order)()).label("row_number"))
            item_list = db.query(*select_fields)
            for join_args in joins:
                item_list = getattr(item_list, join_type)(*join_args)
            temp_query = item_list
            item_list = item_list.filter(filters).order_by(
                getattr(getattr(db_model, query.sort_param), query.sort_order)()).limit(query.limit).offset(
                query.offset).all()
            record_count = len(temp_query.filter(filters).all())

        return item_list, record_count
    except IndexError as e:
        raise DatabaseException(str(e))


def update(db, db_model, item_edit_data, primary_key_attribute, id_value):
    """
    Updates record in database
    Args:
        db: database session
        db_model: ORM model of database table
        item_edit_data: updating values of existing record
        primary_key_attribute: primary key attribute of database table
        id_value: primary key value of record to be updated

    """
    try:

        item = db.query(db_model).filter(getattr(db_model, primary_key_attribute) == id_value).first()
        try:
            if item is None:
                raise ItemNotFoundException(db_id=id_value, db_model=db_model)
            for attr in item_edit_data.__dict__:
                new_value = getattr(item_edit_data, attr)
                if new_value is not None:
                    setattr(item, attr, new_value)
            setattr(item, modified_date_col, datetime.utcnow())
            db.commit()
            return item
        except IntegrityError as ex:
            raise DatabaseIntegrityException(str(ex))
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def update_bulk_common(db, db_model, item_edit_data, primary_key_attribute, id_values):
    """
    Bulk updates record in database. Does the same change to all rows
    Args:
        db: database session
        db_model: ORM model of database table
        item_edit_data: updating values of existing record
        primary_key_attribute: primary key attribute of database table
        id_values: primary key values of records to be updated

    """
    try:
        try:
            updated_mappings = {}
            for attr in item_edit_data.__dict__:
                updated_mappings[attr] = getattr(item_edit_data, attr)
            mappings = []
            for id_value in id_values:
                record = updated_mappings
                record[primary_key_attribute] = id_value
                record[modified_date_col] = datetime.utcnow()
                mappings.append(record.copy())
            db.bulk_update_mappings(db_model, mappings)
            db.commit()
            return True
        except IntegrityError as ex:
            raise DatabaseIntegrityException(str(ex))
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def update_bulk(db, db_model, updated_mappings):
    """
    Bulk updates record in database
    Args:
        db: database session
        db_model: ORM model of database table
        updated_mappings: updating values of existing record

    """
    try:
        try:
            db.bulk_update_mappings(db_model, updated_mappings)
            db.commit()
            return True
        except IntegrityError as ex:
            raise DatabaseIntegrityException(str(ex))
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def delete(db, db_model, primary_key_attribute, id_value, tenant_key=None):
    """
    Deletes record from database
    Args:
        db: database session
        db_model: ORM model of database table
        primary_key_attribute: primary key attribute of database table
        id_value: primary key value of record to be deleted
        tenant_key: tenant key

    Returns:
        Member id if member db_model==Member else None
    """
    try:
        item = db.query(db_model).filter(getattr(db_model, primary_key_attribute) == id_value).first()
        if item is None:
            raise ItemNotFoundException(db_id=id_value, db_model=db_model)
        else:
            db.delete(item)
            db.commit()
            return item
    except IntegrityError as e:
        raise DatabaseIntegrityException(str(e), delete=True)
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def delete_multiple(db, db_model, primary_key_attribute, id_values, tenant_key=None):
    """
    Deletes multiple items from database
    Args:
        db: database session
        db_model: ORM model of database table
        primary_key_attribute: primary key attribute of database table
        id_values: primary key values of records to be deleted
        tenant_key: tenant_key

    Returns:
        List of ids of deleted records
    """
    if not id_values:
        return
    try:
        deleted_ids = []
        items = db.query(db_model).filter(getattr(db_model, primary_key_attribute).in_(id_values)).all()
        if not items:
            raise ItemsNotFoundException(id_values)
        for item in items:
            if not tenant_key or tenant_key and item.tenant_key == tenant_key:
                try:
                    db.delete(item)
                    db.commit()
                    deleted_ids.append(getattr(item, primary_key_attribute))
                except IntegrityError:
                    continue
                except SQLAlchemyError:
                    continue
        if not deleted_ids:
            raise UNABLE_TO_DELETE_ITEMS
        return deleted_ids
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))


def replace_items_in_db(db, db_model, items_data, primary_key_attribute, filters=True):
    """
    Deletes and creates set of records for given tenant in given database table
    Args:
        db: database session
        db_model: ORM model of database table
        filters: query filters to use
        items_data: list of data values of new records
        primary_key_attribute: primary key attribute of database table

    Returns:
        List of ids of added records
    """
    ids_to_delete = [getattr(item, primary_key_attribute) for item in retrieve(db, db_model, None, filters,
                                                                               [getattr(db_model,
                                                                                        primary_key_attribute)])[0]]

    if ids_to_delete:
        delete_multiple(db, db_model, primary_key_attribute, ids_to_delete)

    for item_data in items_data:
        create(db, db_model, item_data)
