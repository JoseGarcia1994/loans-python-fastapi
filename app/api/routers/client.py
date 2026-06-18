# 🌐 Third-party
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Client
from ...schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
)

router = APIRouter(tags=["client"])


@router.get(
    "/",
    response_model=list[ClientResponse],
    status_code=status.HTTP_200_OK,
)
async def get_clients(
    user: user_dependency,
    db: db_dependency,
):

    return (
        db.query(Client)
        .filter(
            Client.owner_id == user.get("id")
        )
        .all()
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
)
async def get_client_by_id(
    user: user_dependency,
    db: db_dependency,
    client_id: int = Path(gt=0),
):

    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    return client

@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    user: user_dependency,
    db: db_dependency,
    client_request: ClientCreate,
):
    phone = "".join(
        filter(str.isdigit, client_request.phone)
    )

    existing_client = (
        db.query(Client)
        .filter(
            Client.phone == client_request.phone,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if existing_client:

        raise HTTPException(
            status_code=400,
            detail="Phone number already exists",
        )

    try:

        client = Client(
            **client_request.model_dump(exclude={"phone"}),
            phone=phone,
            owner_id=user.get("id"),
        )

        db.add(client)

        db.commit()

        db.refresh(client)

        return client

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error creating client",
        )


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
)
async def update_client(
    user: user_dependency,
    db: db_dependency,
    client_data: ClientUpdate,
    client_id: int = Path(gt=0),
):

    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if not client:

        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    update_data = client_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(client, key, value)

    db.commit()

    db.refresh(client)

    return client


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_client(
    user: user_dependency,
    db: db_dependency,
    client_id: int = Path(gt=0),
):

    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if not client:

        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    try:

        db.delete(client)

        db.commit()

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error deleting client",
        )