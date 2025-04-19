from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Review Service")

REVIEW_FILE = "microservices/review_service/data/reviews.xlsx"
os.makedirs(os.path.dirname(REVIEW_FILE), exist_ok=True)

class Review(BaseModel):
    stars: int
    comment: str

@app.post("/review")
def add_review(review: Review):
    try:
        if os.path.exists(REVIEW_FILE):
            df = pd.read_excel(REVIEW_FILE, engine='openpyxl')
        else:
            df = pd.DataFrame(columns=["stars", "comment"])

        df.loc[len(df)] = [review.stars, review.comment]
        df.to_excel(REVIEW_FILE, index=False, engine='openpyxl')
        return {"message": "Review saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/review")
def get_reviews():
    try:
        if os.path.exists(REVIEW_FILE):
            df = pd.read_excel(REVIEW_FILE, engine='openpyxl')
            return df.to_dict(orient="records")
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)