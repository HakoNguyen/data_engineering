import os 
import pandas as pd

def save_to_csv(data, filename="books_data.csv", folder="data"):
    os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame(data)
    file_path = os.path.join(folder, filename)

    df.to_csv(file_path, index=False, encoding="utf-8-sig")

def map_rating(rating_str):
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4, 
        "Five": 5
    }
    return rating_map.get(rating_str, None)