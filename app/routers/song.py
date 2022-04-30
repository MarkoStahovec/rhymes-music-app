from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY
from starlette.responses import StreamingResponse, Response

from ..schemas import profile_schema, song_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *
from ..security import auth
import io
from PIL import Image

router = APIRouter(
    prefix="/song",
    tags=["Song"],
)


def check_if_picture(file: UploadFile = File(...)):
    # check_filetype
    # supported_files = ["audio/mp3", 'audio/mpeg3', 'audio/x-mpeg-3', 'video/mpeg', 'video/x-mpeg', 'audio/mpeg']
    supported_files = ['audio/mpeg']
    if file.content_type not in supported_files:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type.",
        )
    file_bytes = file.file.read()
    size = len(file_bytes)
    if size > 6 * 1024 * 1024:  # 3MB = 3*1024 KB = 3* 1024 * 1024
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selected file is too large.",
        )
    return file_bytes


@router.post("/upload/", status_code=HTTP_200_OK,
             summary="Posts new song.",
             responses={422: {"description": "Unprocessable file."}})
async def add_song(file: UploadFile = File(...),
                   db: Session = Depends(create_connection),
                   user: User = Depends(auth.get_current_user)):
    file_bytes = check_if_picture(file)
    song = Song(name=file.filename,
                author="Marko Stahovec",
                track=file_bytes)

    db.add(song)  # 3 essential methods that post new values into database
    db.commit()
    db.refresh(song)
    return StreamingResponse(io.BytesIO(file_bytes), media_type=file.content_type)


@router.get("/get/{song_id}/", status_code=HTTP_200_OK,
            summary="Retrieves specific song.",
            responses={404: {"description": "Song was not found."}})
def get_song(db: Session = Depends(create_connection),
             song_id: Optional[int] = 0,
             user: User = Depends(auth.get_current_user)):
    result = db.query(Song).filter(Song.song_id == song_id)
    filter_query = result.filter(Song.song_id == song_id).first()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song was not found."
        )

    return Response(content=filter_query.track, media_type=f'audio/mpeg')


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
    ).all()

    if len(result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No song was found."
        )

    return result


@router.delete("/delete/{song_id}/", status_code=HTTP_200_OK,
               summary="Deletes a song.",
               responses={404: {"description": "Song was not found."}})
def delete_song(db: Session = Depends(create_connection),
                song_id: Optional[int] = 0,
                user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.user_id == user.user_id)
    current_user = query.first()

    if current_user.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    if current_user.user_id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    result = db.query(Song).filter(Song.song_id == song_id)
    filter_query = result.filter(Song.song_id == song_id).first()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song was not found."
        )

    db.delete(filter_query)
    db.commit()
