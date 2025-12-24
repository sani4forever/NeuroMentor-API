"""
Routes for API version 1.
"""
import logging
from fastapi import APIRouter, Response, status, HTTPException
from . import crud, models, version_constants
from src.ai_api.deepseek import DeepSeekAPI

main_router = APIRouter()

db = crud.DatabaseManager()
ai_client = DeepSeekAPI()
logger = logging.getLogger('uvicorn.error')

@main_router.get('', include_in_schema=False)
async def root():
    return {'message': f'NeuroMentor API {version_constants.API_VERSION} active'}

@main_router.post('/user', response_model=models.UserResponse, responses={
    500: {'model': models.Error}
})
async def register_user(
        response: Response,
        user_data: models.UserCreateRequest
):
    try:
        new_user = db.create_user_from_front(
            name=user_data.name,
            gender=user_data.gender,
            age=user_data.age
        )
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return models.Error(error=str(e))


@main_router.post('/chat', response_model=models.AIResponse)
async def chat_with_ai(req: models.ChatRequest):
    try:
        user = db.get_user(req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        current_session_id = req.session_id

        if not current_session_id or current_session_id == 0:
            current_session_id = db.get_user_last_session(req.user_id)

            if not current_session_id:
                current_session_id = db.create_new_session(req.user_id)
        else:
            db.get_or_create_session(current_session_id, req.user_id)

        history = db.get_session_history(current_session_id)

        db.save_message(current_session_id, sender="user", text=req.message)

        user_info = {
            "name": user.first_name,
            "age": user.age,
            "gender": user.gender
        }

        ai_data = await ai_client.get_chat_response(user_info, history, req.message)
        ai_text = ai_data["text"]
        tokens = ai_data["tokens"]

        db.save_message(current_session_id, sender="ai", text=ai_text, tokens=tokens)

        print(f"\n[AI LOG] User: {user.first_name} | Msg: {req.message}")
        print(f"[AI LOG] Response: {ai_text}\n")

        return {"answer": ai_text, "session_id": current_session_id}

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))