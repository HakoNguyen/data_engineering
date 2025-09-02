import pandas as pd
from sqlalchemy import create_engine, engine
from config.db_config import get_engine

def extraction(file_path: str):
    try: 
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(e)
        return pd.DataFrame()
    

def transform_listings(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    
    if "price" in df.columns:
        df['price'] = (
            df['price'].astype(int)
        )
    df = df[['id', 'name', 'host_name', 'neighbourhood', 'latitude', 'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews', 'calculated_host_df_count', 'license']]
    df = df.dropna(subset=['id', 'name', 'host_name', 'room_type', 'price'])
    df['license'] = df['license'].fillna('unknown').str.lower().str.strip()
    df['name'] = df['name'].str.replace(r"[@#]", "", regex=True)

    df['price_in_USD'] = (df['price']*(1/155)).round().astype(int)


    df['long_term'] = df['minimum_nights'] > 30
    df['price_per_night'] = (df['price']/df['minimum_nights'].replace(0, 1)).round().astype(int) # neu minimum_night = 0 thay bang 1

    return df

def transform_reviews(df: pd.DataFrame, valid_listing_ids: pd.Series) -> pd.DataFrame:
    if df.empty:
        return df
    if "listing_id" in df.columns:
        df = df[df["listing_id"].isin(valid_listing_ids)]

    return df

def load(df: pd.DataFrame, table_name: str, engine) -> None:
    if df.empty:
        return
    
    try: 
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Đã insert {len(df)} dòng vào bảng {table_name}")
    except Exception as e:
        print(e)

def run_etl():
    engine = get_engine()

    listings = extraction("../data/listings.csv")
    reviews = extraction("../data/reviews.csv")

    listing_clean = transform_listings(listings)
    load(listing_clean, "listings", engine)

    valid_ids = pd.read_sql("SELECT id FROM listings", engine)["id"]
    review_clean = transform_reviews(reviews, valid_ids)
    load(review_clean, "reviews", engine)

if __name__ == "__main__":
    run_etl()