from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products")
