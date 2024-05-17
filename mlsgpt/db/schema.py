from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, LargeBinary, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Property(Base):
    __table_args__ = {'schema': 'rsbr'}
    __tablename__ = 'property'

    property_id = Column(Integer, primary_key=True)
    PostID = Column(Integer)
    ListingID = Column(Integer, index=True)
    LastUpdated = Column(String)
    Latitude = Column(String)
    Longitude = Column(String)
    AmenitiesNearBy = Column(String, name="AmmenitiesNearBy")
    CommunityFeatures = Column(String)
    Features = Column(String)
    Lease = Column(Numeric(38, 2))
    ListingContractDate = Column(String)
    LocationDescription = Column(String)
    MaintenanceFee = Column(String)
    ManagementCompany = Column(String)
    OwnershipType = Column(String)
    ParkingSpaceTotal = Column(String)
    PoolType = Column(String)
    Price = Column(Numeric(38, 2))
    PropertyType = Column(String)
    PublicRemarks = Column(String)
    TransactionType = Column(String)
    ZoningDescription = Column(String)
    MoreInformationLink = Column(String)
    BathroomTotal = Column(Integer, index=True)
    BedroomsAboveGround = Column(Integer)
    BedroomsBelowGround = Column(Integer)
    BedroomsTotal = Column(Integer, index=True)
    Amenities = Column(String)
    Appliances = Column(String)
    ArchitecturalStyle = Column(String)
    BasementDevelopment = Column(String)
    BasementFeatures = Column(String)
    BasementType = Column(String)
    ConstructedDate = Column(String)
    ConstructionStyleAttachment = Column(String)
    CoolingType = Column(String)
    ExteriorFinish = Column(String)
    FireplacePresent = Column(String)
    FoundationType = Column(String)
    HalfBathTotal = Column(Integer)
    HeatingFuel = Column(String)
    HeatingType = Column(String)
    StoriesTotal = Column(Integer)
    SizeInterior = Column(String)
    Type = Column(String)
    SizeTotalText = Column(String)
    SizeFrontage = Column(String)
    AccessType = Column(String)
    Acreage = Column(String)
    LandAmenities = Column(String)
    SizeDepth = Column(String)
    SizeIrregular = Column(String)
    StreetAddress = Column(String)
    AddressLine1 = Column(String)
    City = Column(String, index=True)
    Province = Column(String, index=True)
    PostalCode = Column(String)
    Country = Column(String)
    CommunityName = Column(String, index=True)
    CustomListing = Column(Integer)
    Sold = Column(Integer)
    AlternateURL = Column(LargeBinary)
    Rooms = relationship("PropertyRooms", back_populates="Property")
    # Embedding = relationship("Embedding", back_populates="Property")
    # Offices = Column(String, index=True)
    # Agents = Column(String, index=True)
    # Board = Column(String, index=True)

class PropertyRooms(Base):
    __table_args__ = {'schema': 'rsbr'}
    __tablename__ = 'property_rooms'

    room_id = Column(Integer, primary_key=True)
    ListingID = Column(Integer, ForeignKey('rsbr.property.ListingID'))
    Type = Column(String)
    Width = Column(String)
    Length = Column(String)
    Level = Column(String)
    Dimension = Column(String)
    CustomRoom = Column(Integer)
    Property = relationship("Property", back_populates="Rooms")


class Embedding(Base):
    __table_args__ = {'schema': 'rsbr'}
    __tablename__ = 'embedding'

    id = Column(Integer, primary_key=True)
    ListingID = Column(Integer, ForeignKey('rsbr.property.ListingID'))
    PublicRemarks = Column(String)
    Embedding = Column(Vector(1536))
    CreatedAt = Column(DateTime)
    Property = relationship("Property")


# class Board(Base):
#     __table_args__ = {'schema': 'rsbr'}
#     __tablename__ = 'board'
#     id = Column(Integer, primary_key=True)
#     OrganizationID = Column(Integer)
#     ShortName = Column(String)
#     LongName = Column(String)

# class Office(Base):
#     __table_args__ = {'schema': 'rsbr'}
#     __tablename__ = 'offices'

#     office_id = Column(Integer, primary_key=True)
#     OfficeID = Column(Integer)
#     Name = Column(String)
#     ID = Column(Integer)
#     OrganizationType = Column(String)
#     Designation = Column(String)
#     Address = Column(String)
#     Franchisor = Column(String)
#     StreetAddress = Column(String)
#     AddressLine1 = Column(String)
#     AddressLine2 = Column(String)
#     City = Column(String)
#     Province = Column(String)
#     PostalCode = Column(String)
#     Country = Column(String)
#     AdditionalStreetInfo = Column(String)
#     CommunityName = Column(String)
#     Neighbourhood = Column(String)
#     Subdivision = Column(String)
#     Phones = Column(LargeBinary)
#     Websites = Column(LargeBinary)
#     CustomOffice = Column(Integer)
#     Agents = relationship("Agent", back_populates="Office")

# class Agent(Base):
#     __table_args__ = {'schema': 'rsbr'}
#     __tablename__ = 'agent'

#     agent_id = Column(Integer, primary_key=True)
#     AgentID = Column(Integer)
#     OfficeID = Column(Integer)
#     Name = Column(String)
#     ID = Column(String)
#     LastUpdated = Column(String)
#     Position = Column(String)
#     EducationCredentials = Column(String)
#     Specialties = Column(String)
#     Specialty = Column(String)
#     Languages = Column(String)
#     Language = Column(String)
#     TradingAreas = Column(String)
#     TradingArea = Column(String)
#     Phones = Column(LargeBinary)
#     Websites = Column(LargeBinary)
#     Designations = Column(LargeBinary)
#     CustomAgent = Column(Integer)
#     Office = relationship("Office", back_populates="Agent")