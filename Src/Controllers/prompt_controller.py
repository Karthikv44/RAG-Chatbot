from fastapi import APIRouter, Depends

from Src.Middleware.auth_middleware import get_current_user_id
from Src.Service.prompts.prompt_registry import ACTIVE_VERSION, list_versions, load_prompt

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.get("/")
async def get_prompt_versions(_: str = Depends(get_current_user_id)):
    """List all available prompt versions and the active one."""
    return {
        "active_version": ACTIVE_VERSION,
        "versions": list_versions(),
    }


@router.get("/{version}")
async def get_prompt_by_version(version: str, _: str = Depends(get_current_user_id)):
    """Get the content of a specific prompt version."""
    try:
        return {"version": version, "content": load_prompt(version)}
    except FileNotFoundError:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Prompt version '{version}' not found")
