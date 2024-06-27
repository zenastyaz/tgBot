from sqlalchemy import BigInteger, String, Text, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    # email = Column(String(100), nullable=False, unique=True)


class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class Cocktail(Base):
    __tablename__ = 'cocktails'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    compound: Mapped[str] = mapped_column(String(255),  nullable=False)
    price: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)

    category: Mapped['Category'] = relationship(backref='cocktails')


class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    cocktail_id: Mapped[int] = mapped_column(ForeignKey('cocktails.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='cart')
    cocktail: Mapped['Cocktail'] = relationship(backref='cart')


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_number: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    cocktail_id: Mapped[int] = mapped_column(ForeignKey('cocktails.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='orders')
    cocktail: Mapped['Cocktail'] = relationship(backref='orders')


class Table(Base):
    __tablename__ = 'table'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_number: Mapped[int] = mapped_column(nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)

    bookings: Mapped['Booking'] = relationship(backref='table')


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id', ondelete='CASCADE'), nullable=False)
    booking_date: Mapped[str] = mapped_column(DateTime, nullable=False)

    user: Mapped['User'] = relationship(backref='bookings')



