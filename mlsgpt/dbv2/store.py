import os
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from mlsgpt.dbv2 import schema
from mlsgpt.db import models

DSN = "postgresql://{}:{}@{}:{}/{}"


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

    def get_properties(self, limit: int = 20, offset: int = 0):
        return (
            self.session.query(schema.Property)
            .limit(min(limit, 20))
            .offset(offset)
            .all()
        )

    def search(self, limit: int = 20, offset: int = 0, **kwargs):
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
                    condition = schema.Property.StreetAddress.ilike(f"%{value}%")
                case "City":
                    condition = schema.Property.City.ilike(f"%{value}%")
                case "PostalCode":
                    condition = schema.Property.PostalCode.ilike(f"%{value}%")
                case "Province":
                    condition = schema.Property.Province.ilike(f"%{value}%")
                case "Type":
                    condition = schema.Property.Type.ilike(f"%{value}%")
                case "BedroomsTotal":
                    condition = schema.Property.BedroomsTotal == value
                case "BathroomTotal":
                    condition = schema.Property.BathroomTotal == value

            query = query.filter(condition)

        return (
            query.order_by(schema.Property.LastUpdated.desc())
            .limit(min(limit, 20))
            .offset(offset)
            .all()
        )

    def semantic_search(
        self, query: str, limit: int = 20, offset: int = 0, threshold: float = 0.45
    ):
        vector = self.embed(query)
        return (
            self.session.query(schema.Property)
            .join(schema.Embedding)
            .filter(
                1.0 - schema.Embedding.Embedding.cosine_distance(vector) >= threshold
            )
            .order_by(schema.Property.LastUpdated.desc())
            .limit(min(limit, 20))
            .offset(offset)
            .all()
        )

    def get_stats_info(self):
        return self.session.query(schema.StatsInfo).all()

    def get_city_stats(self, city: list[str]):
        return (
            self.session.query(schema.CityStats)
            .filter(schema.CityStats.City.in_(city))
            .all()
        )

    def get_city_type_stats(self, city: list[str], type: list[str]):
        return (
            self.session.query(schema.CityTypeStats)
            .filter(schema.CityTypeStats.City.in_(city))
            .filter(schema.CityTypeStats.Type.in_(type))
            .all()
        )

    def get_city_property_type_stats(self, city: list[str], property_type: list[str]):
        return (
            self.session.query(schema.CityPropertyTypeStats)
            .filter(schema.CityPropertyTypeStats.City.in_(city))
            .filter(schema.CityPropertyTypeStats.PropertyType.in_(property_type))
            .all()
        )

    def get_city_bedrooms_stats(self, city: list[str], bedrooms: list[str]):
        return (
            self.session.query(schema.CityBedroomsStats)
            .filter(schema.CityBedroomsStats.City.in_(city))
            .filter(schema.CityBedroomsStats.BedroomsTotal.in_(bedrooms))
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
