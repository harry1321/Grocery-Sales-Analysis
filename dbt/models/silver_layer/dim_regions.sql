SELECT 
    city.CityID,
    city.CityName,
    countryCountryName
FROM {{ref("cities")}} AS city
JOIN {{ref("countries")}} AS country
    ON city.CountryID = country.CountryID