from typing import List
from pydantic import BaseModel, Field, ConfigDict

class PropertyRooms(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    room_id: int | None = Field(..., description="Room ID")
    ListingID: int | None = Field(..., description="Listing ID")
    Type: str | None = Field(..., description="Type")
    Width: str | None = Field(..., description="Width")
    Length: str | None = Field(..., description="Length")
    Level: str | None = Field(..., description="Level")
    Dimension: str | None = Field(..., description="Dimension")
    CustomRoom: int | None = Field(..., description="Custom Room")


class Property(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    property_id: int | None = Field(..., description="Property ID")
    PostID: int | None = Field(..., description="Post ID")
    ListingID: int | None = Field(..., description="Listing ID")
    LastUpdated: str | None = Field(..., description="Last Updated")
    Latitude: str | None = Field(..., description="Latitude")
    Longitude: str | None = Field(..., description="Longitude")
    AmenitiesNearBy: str | None = Field(..., description="The amenities near the property")
    CommunityFeatures: str | None = Field(..., description="Community Features")
    Features: str | None = Field(..., description="Features")
    Lease: float | None = Field(..., description="Lease")
    ListingContractDate: str | None = Field(..., description="Listing Contract Date")
    LocationDescription: str | None = Field(..., description="Location Description")
    MaintenanceFee: str | None = Field(..., description="Maintenance Fee")
    ManagementCompany: str | None = Field(..., description="Management Company")
    OwnershipType: str | None = Field(..., description="Ownership Type")
    ParkingSpaceTotal: str | None = Field(..., description="Parking Space Total")
    PoolType: str | None = Field(..., description="Pool Type")
    Price: float | None = Field(..., description="Price")
    PropertyType: str | None = Field(..., description="Property Type")
    PublicRemarks: str | None = Field(..., description="Public Remarks")
    TransactionType: str | None = Field(..., description="Transaction Type")
    ZoningDescription: str | None = Field(..., description="Zoning Description")
    MoreInformationLink: str | None = Field(..., description="More Information Link")
    BathroomTotal: int | None = Field(..., description="Bathroom Total")
    BedroomsAboveGround: int | None = Field(..., description="Bedrooms Above Ground")
    BedroomsBelowGround: int | None = Field(..., description="Bedrooms Below Ground")
    BedroomsTotal: int | None = Field(..., description="Bedrooms Total")
    Amenities: str | None = Field(..., description="Amenities")
    Appliances: str | None = Field(..., description="Appliances")
    ArchitecturalStyle: str | None = Field(..., description="Architectural Style")
    BasementDevelopment: str | None = Field(..., description="Basement Development")
    BasementFeatures: str | None = Field(..., description="Basement Features")
    BasementType: str | None = Field(..., description="Basement Type")
    ConstructedDate: str | None = Field(..., description="Constructed Date")
    ConstructionStyleAttachment: str | None = Field(..., description="Construction Style Attachment")
    CoolingType: str | None = Field(..., description="Cooling Type")
    ExteriorFinish: str | None = Field(..., description="Exterior Finish")
    FireplacePresent: str | None = Field(..., description="Fireplace Present")
    FoundationType: str | None = Field(..., description="Foundation Type")
    HalfBathTotal: int | None = Field(..., description="Half Bath Total")
    HeatingFuel: str | None = Field(..., description="Heating Fuel")
    HeatingType: str | None = Field(..., description="Heating Type")
    StoriesTotal: int | None = Field(..., description="Stories Total")
    SizeInterior: str | None = Field(..., description="Size Interior")
    Type: str | None = Field(..., description="Type")
    SizeTotalText: str | None = Field(..., description="Size Total Text")
    SizeFrontage: str | None = Field(..., description="Size Frontage")
    AccessType: str | None = Field(..., description="Access Type")
    Acreage: str | None = Field(..., description="Acreage")
    LandAmenities: str | None = Field(..., description="Land Amenities")
    SizeDepth: str | None = Field(..., description="Size Depth")
    SizeIrregular: str | None = Field(..., description="Size Irregular")
    StreetAddress: str | None = Field(..., description="Street Address")
    AddressLine1: str | None = Field(..., description="Address Line 1")
    City: str | None = Field(..., description="City")
    Province: str | None = Field(..., description="Province")
    PostalCode: str | None = Field(..., description="Postal Code")
    Country: str | None = Field(..., description="Country")
    CommunityName: str | None = Field(..., description="Community Name")
    CustomListing: int | None = Field(..., description="Custom Listing")
    Sold: int | None = Field(..., description="Sold")
    AlternateURL: bytes | None = Field(..., description="Alternate URL")
    Rooms: List[PropertyRooms] = Field(..., description="Rooms")