import os
import h3
import googlemaps
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_, text

from mlsgpt.dbv2 import schema
from mlsgpt.dbv2 import filters
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
        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def geocode(self, address: str):
        geo = self.gmaps.geocode(address)
        return geo[0]["geometry"]["location"]

    def h3(self, lat: float, lng: float, resolution: int = 9):
        return h3.geo_to_h3(lat, lng, resolution)

    def k_ring(self, address: str, resolution: int = 10, distance: int = 4):
        lat, lng = self.geocode(address).values()
        index = h3.geo_to_h3(lat, lng, resolution)
        values = h3.k_ring(h3.geo_to_h3(lat, lng, resolution), distance)
        return values, index

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
            query = query.filter(filters.filter_props(key, value))

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

    def search_nearby(
        self,
        address: str,
        limit: int = LIMIT,
        offset: int = 0,
        resolution: int = 10,
        distance: int = 4,
        **kwargs,
    ):

        # get nearby properties first
        values, address_h3_index = self.k_ring(address, resolution, distance)
        condition = filters.filter_nearby(resolution, values)
        query = (
            self.session.query(schema.Property).join(schema.H3Index).filter(condition)
        )

        # filter by other conditions
        for key, value in kwargs.items():
            if value is None:
                continue
            query = query.filter(filters.filter_props(key, value))

        # compute the h3 distance for each property and sort by it
        def compute_distance(property):
            property_h3_index = getattr(
                property.H3Indexes[0], f"H3IndexR{resolution:02}"
            )
            return h3.h3_distance(address_h3_index, property_h3_index)

        properties = query.all()
        properties_sorted = sorted(properties, key=compute_distance)
        properties_sorted = properties_sorted[offset : offset + limit]
        return properties_sorted

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

    def get_city_owner_type_stats(self, city: list[str], ownership_type: list[str]):
        city_condition = or_(
            *[schema.CityOwnershipTypeStats.City.ilike(f"%{city}%") for city in city]
        )
        ownership_type_condition = or_(
            *[
                schema.CityOwnershipTypeStats.OwnershipType.ilike(f"%{type}%")
                for type in ownership_type
            ]
        )
        return (
            self.session.query(schema.CityOwnershipTypeStats)
            .filter(city_condition)
            .filter(ownership_type_condition)
            .all()
        )

    def get_city_construction_style_stats(
        self, city: list[str], construction_style_attachment: list[str]
    ):
        city_condition = or_(
            *[
                schema.CityConstructionStyleStats.City.ilike(f"%{city}%")
                for city in city
            ]
        )
        construction_style_condition = or_(
            *[
                schema.CityConstructionStyleStats.ConstructionStyleAttachment.ilike(
                    f"%{type}%"
                )
                for type in construction_style_attachment
            ]
        )
        return (
            self.session.query(schema.CityConstructionStyleStats)
            .filter(city_condition)
            .filter(construction_style_condition)
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
