import os
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_, text

from mlsgpt.dbv2 import schema
from mlsgpt.db import models

DSN = "postgresql://{}:{}@{}:{}/{}"
LIMIT = 30


def create_session():
    db_url = DSN.format(
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_HOST"),
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_DB"),
    )
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


class DataReader(object):
    def __init__(self):
        self.session = create_session()
        self.session.expire_all()
        self.llm = OpenAI()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def embed(self, data: str):
        response = self.llm.embeddings.create(
            input=data, model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def get_property(self, listing_id: int = None):
        return (
            self.session.query(schema.Property).filter_by(ListingID=listing_id).first()
        )

    def get_properties(self, limit: int = LIMIT, offset: int = 0):
        return (
            self.session.query(schema.Property)
            .order_by(text('CAST("LastUpdated" AS TIMESTAMP) DESC'))
            .limit(min(limit, 30))
            .offset(offset)
            .all()
        )

    def search(self, limit: int = LIMIT, offset: int = 0, **kwargs):
        query = self.session.query(schema.Property)

        for key, value in kwargs.items():
            if value is None:
                continue

            match key:
                case "MaxPrice":
                    condition = schema.Property.Price <= value
                case "MinPrice":
                    condition = schema.Property.Price >= value
                case "MaxLease":
                    condition = schema.Property.Lease <= value
                case "MinLease":
                    condition = schema.Property.Lease >= value
                case "Address":
                    condition = or_(
                        *[
                            schema.Property.StreetAddress.ilike(f"%{address}%")
                            for address in value
                        ]
                    )
                case "City":
                    condition = or_(
                        *[schema.Property.City.ilike(f"%{city}%") for city in value]
                    )
                case "PostalCode":
                    condition = or_(
                        *[
                            schema.Property.PostalCode.ilike(f"%{post_code}%")
                            for post_code in value
                        ]
                    )
                case "Province":
                    condition = or_(
                        *[
                            schema.Property.Province.ilike(f"%{province}%")
                            for province in value
                        ]
                    )
                case "Type":
                    condition = or_(
                        *[schema.Property.Type.ilike(f"%{type}%") for type in value]
                    )
                case "BedroomsTotal":
                    condition = or_(
                        *[
                            schema.Property.BedroomsTotal == bedrooms
                            for bedrooms in value
                        ]
                    )
                case "BathroomTotal":
                    condition = or_(
                        *[
                            schema.Property.BathroomTotal == bathrooms
                            for bathrooms in value
                        ]
                    )

            query = query.filter(condition)
        return (
            query.order_by(text('CAST("LastUpdated" AS TIMESTAMP) DESC'))
            .limit(min(limit, LIMIT))
            .offset(offset)
            .all()
        )

    def semantic_search(
        self, query: str, limit: int = LIMIT, offset: int = 0, threshold: float = 0.45
    ):
        vector = self.embed(query)
        return (
            self.session.query(schema.Property)
            .join(schema.Embedding)
            .filter(
                1.0 - schema.Embedding.Embedding.cosine_distance(vector) >= threshold
            )
            .order_by(text('CAST("LastUpdated" AS TIMESTAMP) DESC'))
            .limit(min(limit, 20))
            .offset(offset)
            .all()
        )

    def get_stats_info(self):
        return self.session.query(schema.StatsInfo).all()

    def get_city_stats(self, city: list[str]):
        city_condition = or_(
            *[schema.CityStats.City.ilike(f"%{city}%") for city in city]
        )
        return self.session.query(schema.CityStats).filter(city_condition).all()

    def get_city_type_stats(self, city: list[str], type: list[str]):
        city_condition = or_(
            *[schema.CityTypeStats.City.ilike(f"%{city}%") for city in city]
        )
        type_condition = or_(
            *[schema.CityTypeStats.Type.ilike(f"%{type}%") for type in type]
        )
        return (
            self.session.query(schema.CityTypeStats)
            .filter(city_condition)
            .filter(type_condition)
            .all()
        )

    def get_city_property_type_stats(self, city: list[str], property_type: list[str]):
        city_condition = or_(
            *[schema.CityPropertyTypeStats.City.ilike(f"%{city}%") for city in city]
        )
        property_type_condition = or_(
            *[
                schema.CityPropertyTypeStats.PropertyType.ilike(f"%{type}%")
                for type in property_type
            ]
        )
        return (
            self.session.query(schema.CityPropertyTypeStats)
            .filter(city_condition)
            .filter(property_type_condition)
            .all()
        )

    def get_city_bedrooms_stats(self, city: list[str], bedrooms: list[str]):
        city_condition = or_(
            *[schema.CityBedroomsStats.City.ilike(f"%{city}%") for city in city]
        )
        bedrooms_condition = or_(
            *[
                schema.CityBedroomsStats.BedroomsTotal == bedrooms
                for bedrooms in bedrooms
            ]
        )
        return (
            self.session.query(schema.CityBedroomsStats)
            .filter(city_condition)
            .filter(bedrooms_condition)
            .all()
        )


def add_user_to_db_function():
    db = create_session()

    def _(user: models.User):
        existing_user = (
            db.query(schema.User).filter(schema.User.Email == user.email).first()
        )
        if existing_user:
            return existing_user

        db_user = schema.User(
            Email=user.email,
            Name=user.name,
            EmailVerified=user.email_verified,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return _
