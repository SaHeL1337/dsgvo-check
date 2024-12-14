from sqlalchemy import Column, Integer, String
from database import Base

class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    baseUrl = Column(String)
    crawledUrl = Column(String)
    externalResources = Column(String)

    def __init__(self, baseUrl, crawledUrl, externalResources):
        self.baseUrl = baseUrl
        self.crawledUrl = crawledUrl
        self.externalResources = externalResources

    def __repr__(self):
        return '[{0}][{1}]: {2} \n'. format(self.baseUrl, self.crawledUrl, self.externalResources)