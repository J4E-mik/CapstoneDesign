from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)


class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True, autoincrement=False)
    weight = Column(Integer, nullable=False)
    start = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    end = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    heuristic = Column(Float, nullable=True)
    type = Column(Integer, nullable=True)

    start_node = relationship("Node", foreign_keys=[start])
    end_node = relationship("Node", foreign_keys=[end])

class Routing(Base):
    __tablename__ = 'routing'

    prev_node = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=True)
    current_node = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    next_node = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=True)
    goal = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    direct = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)

    prev_node_rel = relationship('Node', foreign_keys=[prev_node])
    current_node_rel = relationship('Node', foreign_keys=[current_node])
    next_node_rel = relationship('Node', foreign_keys=[next_node])
    goal_rel = relationship('Node', foreign_keys=[goal])

'''
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
'''