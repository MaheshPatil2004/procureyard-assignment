import pandas as pd
from sqlalchemy import create_engine

# Matches the environment variables in your docker-compose.yml
DATABASE_URL = "postgresql://quickdrop:password@localhost:5432/quickdrop_db"
engine = create_engine(DATABASE_URL)

def seed_database():
    print("Reading CSVs...")
    riders = pd.read_csv("data/riders.csv")
    trips = pd.read_csv("data/trips.csv")
    payouts = pd.read_csv("data/payout_lines.csv")

    print("Inserting into PostgreSQL...")
    # if_exists="append" ensures it maps to your init.sql schema
    riders.to_sql("riders", engine, if_exists="append", index=False)
    trips.to_sql("trips", engine, if_exists="append", index=False)
    payouts.to_sql("payout_lines", engine, if_exists="append", index=False)
    
    print("Seeding complete.")

if __name__ == "__main__":
    seed_database()