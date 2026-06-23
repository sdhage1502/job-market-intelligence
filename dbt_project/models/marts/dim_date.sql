-- Date Dimension Model

SELECT
    date_key,
    full_date,
    month,
    quarter,
    year
FROM {{ source('raw_data', 'dim_date') }}
