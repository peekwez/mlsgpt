from typing import List
from pydantic import BaseModel, Field, ConfigDict


class PropertyRooms(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ListingID: int | None = Field(..., description="Listing ID")
    Type: str | None = Field(..., description="Type")
    Width: str | None = Field(..., description="Width")
    Length: str | None = Field(..., description="Length")
    Level: str | None = Field(..., description="Level")
    Dimension: str | None = Field(..., description="Dimension")
    CustomRoom: int | None = Field(..., description="Custom Room")


class Property(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    PostID: int | None = Field(..., description="Post ID")
    ListingID: int | None = Field(..., description="Listing ID")
    LastUpdated: str | None = Field(..., description="Last Updated")
    Latitude: str | None = Field(..., description="Latitude")
    Longitude: str | None = Field(..., description="Longitude")
    AmenitiesNearBy: str | None = Field(
        ..., description="The amenities near the property"
    )
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
    ConstructionStyleAttachment: str | None = Field(
        ..., description="Construction Style Attachment"
    )
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
    Rooms: List[PropertyRooms] | None = Field(..., description="Rooms")


class CityStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class CityTypeStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    Type: str = Field(..., description="The type in lower case")
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class CityPropertyTypeStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    PropertyType: str = Field(
        ...,
        description="The property type in lower case",
    )
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class CityBedroomsStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    BedroomsTotal: int = Field(..., description="The total number of bedrooms")
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class CityOwnershipTypeStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    OwnershipType: str = Field(..., description="The ownership type in lower case")
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class CityConstructionStyleAttachmentStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    City: str = Field(..., description="The city in lower case")
    ConstructionStyleAttachment: str = Field(
        ..., description="The construction style attachment in lower case"
    )
    InventoryCount: int = Field(..., description="The inventory count")
    AveragePrice: float = Field(..., description="The average price")
    MedianPrice: float = Field(..., description="The median price")
    MinimumPrice: float = Field(..., description="The minimum price")
    MaximumPrice: float = Field(..., description="The maximum price")
    AverageDaysOnMarket: float = Field(..., description="The average days on market")
    MedianDaysOnMarket: float = Field(..., description="The median days on market")
    MinimumDaysOnMarket: float = Field(..., description="The minimum days on market")
    MaximumDaysOnMarket: float = Field(..., description="The maximum days on market")
    AveragePricePerSqft: float | None = Field(
        ..., description="The average price per square foot"
    )


class StatsInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    Attribute: str = Field(..., description="Name")
    Values: list[str | None] = Field(..., description="Values")


class BaseSearchFilters(BaseModel):
    limit: int = Field(
        30,
        description="The number of listings to return. The maximum is 30 listings. You can use the offset to control the page to show",
    )
    offset: int = Field(
        0,
        description="The offset for paginating the results. Default is 0. Use this to paginate the results.",
    )


class BaseSearchFieldFilters(BaseSearchFilters):
    type: list[str] = Field(
        None,
        description="A list of unit types to filter by (e.g. condo apt, condo townhouse, detached)",
        json_schema_extra={
            "examples": [
                "apartment",
                "commercial apartment",
                "duplex",
                "fourplex",
                "house",
                "mobile home",
                "modular",
                "multi-family",
                "other",
                "row / townhouse",
                "triplex",
            ]
        },
    )

    property_type: list[str] = Field(
        None,
        description="A list of property types to filter by",
        json_schema_extra={"examples": ["multi-family", "single family"]},
    )

    ownership_type: list[str] = Field(
        None,
        description="A list of ownership types to filter by",
        json_schema_extra={
            "examples": [
                "condominium",
                "condominium/strata",
                "cooperative",
                "freehold",
                "leasehold",
                "leasehold condo/strata",
                "life lease",
                "other, see remarks",
                "shares in co-operative",
                "timeshare/fractional",
                "undivided co-ownership",
            ]
        },
    )

    construction_style_attachment: list[str] = Field(
        None,
        description="A list of construction style attachments to filter by",
        json_schema_extra={
            "examples": ["attached", "detached", "link", "semi-detached", "up and down"]
        },
    )

    bedrooms: list[int] = Field(
        None, description="A list of number of bedrooms to filter by"
    )
    washrooms: list[int] = Field(
        None, description="A list of number of washrooms to filter by"
    )
    min_price: float = Field(None, description="Minimum price to filter by")
    max_price: float = Field(None, description="Maximum price to filter by")
    min_lease: float = Field(None, description="Minimum lease to filter by")
    max_lease: float = Field(None, description="Maximum lease to filter by")


class ListingSearchFilters(BaseSearchFieldFilters):
    address: list[str] = Field(
        None, description="A list of addresses to use for filtering"
    )
    city: list[str] = Field(None, description="A list of cities to use for filtering")
    postal_code: list[str] = Field(
        None,
        description="A list of postal codes to use for filtering (use FSA in most cases)",
    )
    province: list[str] = Field(
        None, description="A list of provinces to use for filtering"
    )


class SearchNearbyListings(BaseSearchFieldFilters):
    address: str = Field(
        None, description="The address to use for searching nearby listings"
    )
    resolution: int = Field(
        10,
        description="The resolution for the H3 hexagons. Default is 10. Higher narrow downs the search area but and is likely to return nothing.",
    )
    distance: int = Field(
        10,
        description="The H3 distance. Default is 10. Higher expands the search area and is slower. Increase this if you want more listings or nothing is returned after a call",
    )


class ListingNaturalLanguageSearch(BaseSearchFilters):
    query: str = Field(..., description="Natural language search query")
    threshold: float = Field(
        0.3,
        description="The similarity threshold for the search. Default is 0.3",
    )


class ListingsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[Property] = Field(..., description="List of listings returned")
    offset: int = Field(..., description="The offset for paginating the results")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error name")
    message: str = Field(..., description="Error message")


class CityStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")


class CityStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityStats] = Field(..., description="List of city statistics returned")


class CityTypeStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")
    type: list[str] = Field(
        ...,
        description="A list of types to fetch statistics for",
        json_schema_extra={
            "examples": [
                "apartment",
                "commercial apartment",
                "duplex",
                "fourplex",
                "house",
                "mobile home",
                "modular",
                "multi-family",
                "other",
                "row / townhouse",
                "triplex",
            ]
        },
    )


class CityTypeStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityTypeStats] = Field(
        ...,
        description="List of city type statistics returned",
    )


class CityPropertyTypeStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")
    property_type: list[str] = Field(
        ...,
        description="A list of property types to fetch statistics for",
        json_schema_extra={"examples": ["multi-family", "single family"]},
    )


class CityPropertyTypeStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityPropertyTypeStats] = Field(
        ..., description="List of city property type statistics returned"
    )


class CityBedroomsStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")
    bedrooms: list[int] = Field(
        ..., description="A list of bedrooms to fetch statistics for"
    )


class CityBedroomsStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityBedroomsStats] = Field(
        ..., description="List of city bedrooms statistics returned"
    )


class StatsInfoResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[StatsInfo] = Field(..., description="List of stats info returned")


class CityOwnershipTypeStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")
    ownership_type: list[str] = Field(
        ...,
        description="A list of ownership types to fetch statistics for",
        json_schema_extra={
            "examples": [
                "condominium",
                "condominium/strata",
                "cooperative",
                "freehold",
                "leasehold",
                "leasehold condo/strata",
                "life lease",
                "other, see remarks",
                "shares in co-operative",
                "timeshare/fractional",
                "undivided co-ownership",
            ]
        },
    )


class CityOwnershipTypeStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityOwnershipTypeStats] = Field(
        ..., description="List of city ownership type statistics returned"
    )


class CityConstructionStyleAttachmentStatsRequest(BaseModel):
    city: list[str] = Field(..., description="A list of cities to fetch statistics for")
    construction_style_attachment: list[str] = Field(
        ...,
        description="A list of construction style attachments to fetch statistics for",
        json_schema_extra={
            "examples": ["attached", "detached", "link", "semi-detached", "up and down"]
        },
    )


class CityConstructionStyleAttachmentStatsResponse(BaseModel):
    num_items: int = Field(..., description="Number of items returned")
    items: list[CityConstructionStyleAttachmentStats] = Field(
        ...,
        description="List of city construction style attachment statistics returned",
    )
