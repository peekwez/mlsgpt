from sqlalchemy import or_
from mlsgpt.dbv2 import schema


def filter_props(key, value):
    condition = None
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
                *[schema.Property.Province.ilike(f"%{province}%") for province in value]
            )
        case "Type":
            condition = or_(
                *[schema.Property.Type.ilike(f"%{type}%") for type in value]
            )
        case "PropertyType":
            condition = or_(
                *[
                    schema.Property.PropertyType.ilike(f"%{property_type}%")
                    for property_type in value
                ]
            )
        case "OwnershipType":
            condition = or_(
                *[
                    schema.Property.OwnershipType.ilike(f"%{ownership_type}%")
                    for ownership_type in value
                ]
            )
        case "ConstructionStyleAttachment":
            condition = or_(
                *[
                    schema.Property.ConstructionStyleAttachment.ilike(
                        f"%{construction_style}%"
                    )
                    for construction_style in value
                ]
            )
        case "BedroomsTotal":
            condition = or_(
                *[schema.Property.BedroomsTotal == bedrooms for bedrooms in value]
            )
        case "BathroomTotal":
            condition = or_(
                *[schema.Property.BathroomTotal == bathrooms for bathrooms in value]
            )
        case _:
            raise ValueError(f"Invalid filter key :: {key}")
    return condition


def filter_nearby(resolution, values):
    match resolution:
        case 0:
            condition = schema.H3Index.H3IndexR00.in_(values)
        case 1:
            condition = schema.H3Index.H3IndexR01.in_(values)
        case 2:
            condition = schema.H3Index.H3IndexR02.in_(values)
        case 3:
            condition = schema.H3Index.H3IndexR03.in_(values)
        case 4:
            condition = schema.H3Index.H3IndexR04.in_(values)
        case 5:
            condition = schema.H3Index.H3IndexR05.in_(values)
        case 6:
            condition = schema.H3Index.H3IndexR06.in_(values)
        case 7:
            condition = schema.H3Index.H3IndexR07.in_(values)
        case 8:
            condition = schema.H3Index.H3IndexR08.in_(values)
        case 9:
            condition = schema.H3Index.H3IndexR09.in_(values)
        case 10:
            condition = schema.H3Index.H3IndexR10.in_(values)
        case 11:
            condition = schema.H3Index.H3IndexR11.in_(values)
        case 12:
            condition = schema.H3Index.H3IndexR12.in_(values)
        case 13:
            condition = schema.H3Index.H3IndexR13.in_(values)
        case 14:
            condition = schema.H3Index.H3IndexR14.in_(values)
        case 15:
            condition = schema.H3Index.H3IndexR15.in_(values)
        case _:
            raise ValueError(f"Invalid resolution :: {resolution}")
    return condition
