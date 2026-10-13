from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.connection import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title_fa = Column(Text, nullable=True)
    rate = Column(Float, default=0.0)
    rate_cnt = Column(Integer, default=0)
    category1 = Column(String(255), index=True)
    category2 = Column(String(255), index=True)
    brand = Column(String(255), index=True)
    price = Column(Float, default=0.0)
    seller = Column(String(255))
    is_fake = Column(Boolean, default=False)
    min_price_last_month = Column(Float, default=0.0)
    sub_category = Column(String(255))

    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    sentences = relationship("ReviewSentence", back_populates="product", cascade="all, delete-orphan")
    sentiments = relationship("SentimentResult", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", uselist=False, cascade="all, delete-orphan")
    cluster = relationship("ProductCluster", back_populates="product", uselist=False, cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    title = Column(Text)
    body = Column(Text)
    created_at = Column(DateTime, nullable=True)
    rate = Column(Float, default=0.0)
    recommendation_status = Column(String(100))
    is_buyer = Column(Boolean, default=False)
    advantages = Column(Text)
    disadvantages = Column(Text)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    seller_title = Column(String(255))

    product = relationship("Product", back_populates="reviews")
    sentences = relationship("ReviewSentence", back_populates="review", cascade="all, delete-orphan")
    sentiments = relationship("SentimentResult", back_populates="review", cascade="all, delete-orphan")


class ReviewSentence(Base):
    __tablename__ = "review_sentences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sentence_id = Column(Integer, nullable=False)
    sentence_text = Column(Text, nullable=False)

    review = relationship("Review", back_populates="sentences")
    product = relationship("Product", back_populates="sentences")


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sentiment = Column(String(50), nullable=False)
    sentiment_score = Column(Float, default=0.0)

    review = relationship("Review", back_populates="sentiments")
    product = relationship("Product", back_populates="sentiments")


class ProductFeature(Base):
    __tablename__ = "product_features"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True, index=True)

    # Product baseline features
    price = Column(Float, default=0.0)
    rate = Column(Float, default=0.0)
    rate_cnt = Column(Integer, default=0)
    category = Column(String(255))
    subcategory = Column(String(255))
    brand = Column(String(255))
    seller = Column(String(255))
    is_fake = Column(Boolean, default=False)

    # Review-derived features
    review_count = Column(Integer, default=0)
    average_review_rating = Column(Float, default=0.0)
    positive_ratio = Column(Float, default=0.0)
    negative_ratio = Column(Float, default=0.0)
    neutral_ratio = Column(Float, default=0.0)
    conflicted_ratio = Column(Float, default=0.0)
    average_sentiment_score = Column(Float, default=0.0)
    recommendation_ratio = Column(Float, default=0.0)

    product = relationship("Product", back_populates="features")


class ProductCluster(Base):
    __tablename__ = "product_clusters"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True, index=True)
    cluster_id = Column(Integer, nullable=False, index=True)

    product = relationship("Product", back_populates="cluster")
