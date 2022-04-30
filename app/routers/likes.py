from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY
from starlette.responses import StreamingResponse, Response

from ..schemas import profile_schema, song_schema, likes_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text, and_
from typing import List, Optional
from ..models import *
from ..security import auth
import io

router = APIRouter(
    prefix="/likes",
    tags=["Likes"],
)


@router.post("/", status_code=HTTP_201_CREATED, response_model=likes_schema.LikeSong,
             summary="Likes a song.",
             responses={404: {"description": "Song was not found."}})
def like_song(like: likes_schema.LikeSongIn,
                    db: Session = Depends(create_connection),
                    user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.user_id == user.user_id)
    current_user = query.first()

    if current_user.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    liked_song = LikedSongs(user_id=user.user_id, **like.dict())

    db.add(liked_song)  # 3 essential methods that post new values into database
    db.commit()
    db.refresh(liked_song)

    return liked_song


@router.get("/getall/", response_model=List[song_schema.GetAllSongs], status_code=HTTP_200_OK,
            summary="Retrieves all songs.",
            responses={404: {"description": "Songs were not found."}})
def get_all_songs(db: Session = Depends(create_connection),
                  user: User = Depends(auth.get_current_user)):
    result = db.query(
        Song.song_id,
        Song.name,
        Song.author,
        Song.uploaded_at
    )

    join_query = result.join(LikedSongs, Song.song_id == LikedSongs.song_id) \
        .filter(LikedSongs.user_id == user.user_id).all()

    if len(join_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You have no liked songs."
        )

    return join_query


@router.delete("/unlike/", status_code=HTTP_200_OK,
               summary="Unlikes a song.",
               responses={404: {"description": "Song was not found."}})
def delete_song(db: Session = Depends(create_connection),
                song_id: Optional[int] = 0,
                user: User = Depends(auth.get_current_user)):

    result = db.query(LikedSongs).filter(and_(LikedSongs.song_id == song_id, LikedSongs.user_id == user.user_id))
    filter_query = result.first()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song was not found."
        )

    db.delete(filter_query)
    db.commit()
