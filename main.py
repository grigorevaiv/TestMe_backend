from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.database import Base, engine
from models.test_model import Test
from models.block_model import Block
from models.state_model import State
from models.scale_model import Scale
from models.answer_model import Answer
from models.invite_model import Invite
from models.user_model import User
from models.tag_model import Tag
from models.tag_test_model import TagTest
from models.question_model import Question
from models.weight_model import Weight
from models.norm_model import Norm
from models.interpretation_model import Interpretation
from models.result_model import TestResult, UserAnswer
from models.user_model import UserSchema, User
from models.invitation_model import Invitation, InvitationSchema


from routes.block_routes import block_routes
from routes.test_routes import test_routes
from routes.common_routes import common_routes
from routes.scale_routes import scale_routes
from routes.answer_routes import answer_routes
from routes.weight_routes import weight_routes
from routes.norm_routes import norm_routes


from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.question_routes import question_routes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(test_routes, prefix="/tests")
app.include_router(block_routes, prefix="/tests")
app.include_router(common_routes, prefix="/tests")
app.include_router(scale_routes, prefix="/tests")
app.include_router(question_routes, prefix="/tests")

app.include_router(answer_routes, prefix="/tests")
from routes.tag_routes import tag_routes
app.include_router(tag_routes, prefix="/tests")
app.include_router(weight_routes, prefix="/tests")
from routes.norm_routes import norm_routes
app.include_router(norm_routes, prefix="/tests")
from routes.interpretation_routes import interpretation_routes
app.include_router(interpretation_routes, prefix="/tests")
from routes.result_routes import result_routes
app.include_router(result_routes, prefix="/tests")

from routes.invitation_routes import invitation_routes
app.include_router(invitation_routes, prefix="/patients")

from routes.user_routes import user_routes
app.include_router(user_routes, prefix="/patients")

@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
