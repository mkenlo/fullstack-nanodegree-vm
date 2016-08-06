from database_setup import Base, Category, Items
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# connect with the database
engine = create_engine('sqlite:///catalog.db')
# create a connection between the database and the class from database_setup
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


# insert data into the database
def lofOfItemsCategories(categories, items):
    print "-------Beginning insertion"
    for cat in categories:
        newCategory = Category(name=cat)
        for item in items[cat]:
            new_item = Items(
                name=item, description="not yet available", category=newCategory)
            session.add(new_item)
            session.commit()
        session.add(newCategory)
        session.commit()
    print "-------End of insertion"

# CRUD functions for Category Table
def addCategory(name):
    newCategory = Category(name=name)
    session.add(newCategory)
    session.commit()


def editCategory(category_id, name):
    cat = session.query(Category).filter_by(id=category_id).one()
    if name:
        cat.name = name
        session.add(cat)
        session.commit()
    else:
        return False


def deleteAllCategory():
    print "-------Deleting all categories from DB"
    session.query(Category).delete()
    session.commit()


def deleteCategory(category_id):
    cat = session.query(Category).filter_by(id=category_id).one()
    if cat:
        session.delete(cat)
        session.commit()


def getAllCategories():
    return session.query(Category).all()


def getCategoryById(category_id):
    return session.query(Category).filter_by(id=category_id).one()


# CRUD functions for Items Table
def getRecentItems():
    return session.query(Items).limit(12).all()


def getItemsCategory(category_id):
    cat = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id)
    session.commit()
    return cat, items


def getItemById(item_id):
    return session.query(Items).filter_by(id=item_id).one()


def addItem(name, description, category_id):
    item_cat = session.query(Category).filter_by(id=category_id).one()
    new_item = Items(name=name, description = description, category=item_cat)
    session.add(new_item)
    session.commit()


def editItem(item_id, name, description, category_id):
    item = session.query(Items).filter_by(id=item_id).one()
    item_cat = session.query(Category).filter_by(id=category_id).one()

    item.name = name
    item.description = description
    item.category = item_cat
    session.add(item)
    session.commit()


def deleteItem(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    if item:
        session.delete(item)
        session.commit()


def deleteAllItems():
    print "-------Deleting all items from DB"
    session.query(Items).delete()
    session.commit()