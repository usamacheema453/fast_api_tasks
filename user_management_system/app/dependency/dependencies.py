from fastapi import Query
def pagination_params(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, ls=100)
):
    offset= (page - 1) * limit
    return{
        "page": page,
        "limit": limit,
        "offset": offset
    }