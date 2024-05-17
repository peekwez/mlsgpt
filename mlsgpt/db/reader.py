import os
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


from mlsgpt.db.schema import Property, Embedding

DSN = "postgresql://{}:{}@{}:{}/{}"

class DataReader(object):
    def __init__(self):
        db_url = DSN.format(
            os.getenv("POSTGRES_USER"),
            os.getenv("POSTGRES_PASSWORD"),
            os.getenv("POSTGRES_HOST"),
            os.getenv("POSTGRES_PORT"),
            os.getenv("POSTGRES_DB")
        )
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.session.expire_all()
        self.llm = OpenAI()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def embed(self, text):
        response = self.llm.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
    
    def get_property(self, listing_id:int=None):  
        return self.session.query(Property).filter_by(listing_id=listing_id).first()

    def get_properties(self, limit:int=20, offset:int=0):
        return self.session.query(Property).limit(limit).offset(offset).all()
    
    def search(self, **kwargs):
        return self.session.query(Property).filter_by(**kwargs).all()
    

    def semantic_search(self, query:str, limit:int=20, offset:int=0, threshold:float=0.9):
        vector = self.embed(query)
        return (
            self.session
            .query(Property)
            .join(Embedding)   
            .filter(1.0 - Embedding.Embedding.cosine_distance(vector) >= threshold)
            .limit(limit)
            .offset(offset)
            .all()
        )
