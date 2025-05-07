from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)


class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True, autoincrement=False)
    weight = Column(Float, nullable=False)
    node1 = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    node2 = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    type = Column(Integer, nullable=False, default=1)

    start_node = relationship("Node", foreign_keys=[node1])
    end_node = relationship("Node", foreign_keys=[node2])


class Routing(Base):
    __tablename__ = 'routing'

    from_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    to_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    to_node_type = Column(Integer, nullable=False)
    next_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    total_cost = Column(Float, nullable=False)

    from_node = relationship('Node', foreign_keys=[from_node_id])
    to_node = relationship('Node', foreign_keys=[to_node_id])
    next_node = relationship('Node', foreign_keys=[next_node_id])