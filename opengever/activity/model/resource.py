from opengever.activity.model.watcher import Watcher
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship


class ResourceQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        return self.filter_by(oguid=oguid).first()


resource_watchers = Table(
    'resource_watchers', Base.metadata,
    Column('resource_id', Integer,
           ForeignKey('resources.id'), primary_key=True),
    Column('watcher_id', Integer,
           ForeignKey('watchers.id'), primary_key=True))


class Resource(Base):

    query_cls = ResourceQuery

    __tablename__ = 'resources'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    resource_id = Column('id', Integer, primary_key=True)

    admin_unit_id = Column(String(30), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)

    watchers = relationship("Watcher", secondary=resource_watchers,
                            backref="resources", collection_class=set)

    def __repr__(self):
        return '<Resource {}:{}>'.format(self.admin_unit_id, self.int_id)

    def add_watcher(self, user_id):
        watcher = Watcher.query.get_by_userid(user_id)
        if not watcher:
            watcher = Watcher(user_id=user_id)
            create_session().add(watcher)

        self.watchers.add(watcher)
        return watcher

    def remove_watcher(self, watcher):
        self.watchers.remove(watcher)