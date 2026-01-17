import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Body, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from datetime import datetime, timedelta
import json
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- FIREBASE SETUP ----------------



# ---------------- AUTH ROUTES ----------------

@app.post("/api/auth/signup")
async def signup(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")
    name = body.get("name")  # Get Name

    if not email or not password or not name:
        raise HTTPException(400, "Email, password, and name required")

    # Check if user exists
    doc = users_collection.document(email).get()
    if doc.exists:
        raise HTTPException(400, "User already exists")

    # Create user
    users_collection.document(email).set({
        "email": email,
        "name": name,  # Store Name
        "password_hash": hash_password(password),
        "created_at": datetime.utcnow().isoformat()
    })

    return {"message": "User created successfully"}


@app.post("/api/auth/login")
async def login(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(400, "Email and password required")

    doc = users_collection.document(email).get()
    if not doc.exists:
        raise HTTPException(401, "Invalid credentials")

    user_data = doc.to_dict()
    if user_data["password_hash"] != hash_password(password):
        raise HTTPException(401, "Invalid credentials")

    # Issue Token
    token = generate_token()
    expires = (datetime.utcnow() + timedelta(days=30)).isoformat()

    tokens_collection.document(token).set({
        "user_id": email,
        "expires": expires,
        "created_at": datetime.utcnow().isoformat()
    })

    return {"token": token, "email": email, "name": user_data.get("name", "User")}  # Return Name


# ---------------- NOTE ROUTES ----------------

@app.post("/api/notes/organize")
async def organize_note(body: dict, user_id: str = Depends(get_current_user)):
    note_text = body["note_text"]
    existing = []
    for doc in notes_collection.where("user_id", "==", user_id).stream():
        d = note_helper(doc)
        existing.append({"title": d["title"], "summary": d["summary"]})
    return call_ai(note_text, existing)


@app.post("/api/notes")
async def create_or_merge(
        note_text: str = Body(...),
        ai_suggestion: dict = Body(...),
        user_id: str = Depends(get_current_user)
):
    action = ai_suggestion["action"]

    if action == "merge" and ai_suggestion["merge_with"]:
        title = ai_suggestion["merge_with"]
        query = notes_collection.where("title", "==", title).where("user_id", "==", user_id).stream()
        found_doc = next(query, None)

        if found_doc:
            d = found_doc.to_dict()
            d["content"].append({
                "text": note_text,
                "added_at": datetime.utcnow().isoformat()
            })
            d["tags"] = list(set(d.get("tags", []) + ai_suggestion["tags"]))
            d["summary"] = ai_suggestion["summary"]
            d["updated_at"] = datetime.utcnow().isoformat()
            notes_collection.document(found_doc.id).set(d)
            return {"message": "merged", "note": note_helper(found_doc)}

    # Create
    new_data = {
        "title": ai_suggestion["title"],
        "summary": ai_suggestion["summary"],
        "tags": ai_suggestion["tags"],
        "content": [{"text": note_text, "added_at": datetime.utcnow().isoformat()}],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
    }
    ref = notes_collection.document()
    ref.set(new_data)
    return {"message": "created", "note": note_helper(ref.get())}


@app.get("/api/notes")
async def get_all(user_id: str = Depends(get_current_user)):
    return [note_helper(d) for d in notes_collection.where("user_id", "==", user_id).stream()]


@app.get("/api/notes/{id}")
async def get_note(id: str, user_id: str = Depends(get_current_user)):
    doc = notes_collection.document(id).get()
    if not doc.exists: raise HTTPException(404)
    if doc.to_dict().get("user_id") != user_id: raise HTTPException(403)
    return note_helper(doc)


@app.put("/api/notes/{id}")
async def update_note(id: str, data: dict, user_id: str = Depends(get_current_user)):
    doc_ref = notes_collection.document(id)
    doc = doc_ref.get()
    if not doc.exists: raise HTTPException(404)
    if doc.to_dict().get("user_id") != user_id: raise HTTPException(403)
    data["updated_at"] = datetime.utcnow().isoformat()
    data["user_id"] = user_id
    doc_ref.update(data)
    return {"note": note_helper(doc_ref.get())}


@app.delete("/api/notes/{id}")
async def delete_note(id: str, user_id: str = Depends(get_current_user)):
    doc_ref = notes_collection.document(id)
    doc = doc_ref.get()
    if not doc.exists: return {"status": "deleted"}
    if doc.to_dict().get("user_id") != user_id: raise HTTPException(403)
    doc_ref.delete()
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)