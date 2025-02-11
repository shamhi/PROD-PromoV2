import uuid
from datetime import date, datetime

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database.postgres.base import Base
from app.schemas.enums import PromoModeEnum


class BusinessCompanyModel(Base):
    __tablename__ = "business_companies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    promos = relationship("PromoModel", back_populates="company", cascade="all, delete-orphan")


user_promo_likes = Table(
    "user_promo_likes",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("promo_id", UUID(as_uuid=True), ForeignKey("promos.id"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    name = Column(String(100), nullable=False)
    surname = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    avatar_url = Column(String(350), nullable=True)
    age = Column(Integer, nullable=False)
    country = Column(String(2), nullable=False)

    comments = relationship("CommentModel", back_populates="author", cascade="all, delete-orphan")
    liked_promos = relationship("PromoModel", secondary=user_promo_likes, back_populates="liked_by_users")
    activated_promos = relationship("UserPromoActivationModel", back_populates="user", cascade="all, delete-orphan")


class UserPromoActivationModel(Base):
    __tablename__ = "user_promo_activations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    promo_id = Column(UUID(as_uuid=True), ForeignKey("promos.id"), nullable=False)
    activated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="activated_promos")
    promo = relationship("PromoModel", back_populates="activations")


class PromoModel(Base):
    __tablename__ = "promos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    description = Column(String(300), nullable=False)
    image_url = Column(String(350), nullable=True)
    max_count = Column(Integer, nullable=False)
    used_count = Column(Integer, nullable=False, default=0)
    active_from = Column(Date, nullable=True)
    active_until = Column(Date, nullable=True)
    mode = Column(Enum(PromoModeEnum), nullable=False)
    promo_common = Column(String(30), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    company_id = Column(UUID(as_uuid=True), ForeignKey("business_companies.id"), nullable=False)

    company = relationship("BusinessCompanyModel", back_populates="promos")
    comments = relationship("CommentModel", back_populates="promo", cascade="all, delete-orphan")
    liked_by_users = relationship("UserModel", secondary=user_promo_likes, back_populates="liked_promos")
    activations = relationship("UserPromoActivationModel", back_populates="promo", cascade="all, delete-orphan")
    unique_values = relationship("PromoUniqueValueModel", cascade="all, delete-orphan", back_populates="promo")
    targets = relationship("PromoTargetModel", back_populates="promo", cascade="all, delete-orphan")

    @hybrid_property
    def is_active(self):
        now_date = date.today()
        date_cond = (self.active_from is None or self.active_from <= now_date) and (
            self.active_until is None or self.active_until >= now_date
        )

        if self.mode == PromoModeEnum.COMMON:
            return date_cond and (self.used_count < self.max_count)
        elif self.mode == PromoModeEnum.UNIQUE:
            is_has_unique_values = any(not unique.is_used for unique in self.unique_values)
            return date_cond and is_has_unique_values

        return False


class PromoUniqueValueModel(Base):
    __tablename__ = "promo_unique_values"

    promo_id = Column(UUID(as_uuid=True), ForeignKey("promos.id"), primary_key=True, nullable=False)
    unique_code = Column(String(30), primary_key=True)
    is_used = Column(Boolean, nullable=False, default=False)

    promo = relationship("PromoModel", back_populates="unique_values")


class PromoTargetModel(Base):
    __tablename__ = "promo_targets"

    promo_id = Column(UUID(as_uuid=True), ForeignKey("promos.id"), primary_key=True, nullable=False)
    age_from = Column(Integer, nullable=True)
    age_until = Column(Integer, nullable=True)
    country = Column(String(2), nullable=True)
    categories = Column(ARRAY(String), nullable=True)

    promo = relationship("PromoModel", back_populates="targets")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    text = Column(String(1000), nullable=False)
    date = Column(DateTime, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    promo_id = Column(UUID(as_uuid=True), ForeignKey("promos.id"), nullable=False)

    author = relationship("UserModel", back_populates="comments")
    promo = relationship("PromoModel", back_populates="comments")
