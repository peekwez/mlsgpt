select 
a."ListingID" as listing_id,
lower(a."StreetAddress") as street_address,
a."City" as city,
b."H3IndexR09" as h3_r09,
b."H3IndexR10" as h3_r10,
cast(a."LastUpdated" as timestamp) as last_updated
from property as a
left join h3_index as b on a."ListingID" = b."ListingID"
order by cast(a."LastUpdated" as timestamp) desc
limit 10 offset 0;