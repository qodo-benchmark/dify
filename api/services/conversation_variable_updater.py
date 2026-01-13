from sqlalchemy import select
from sqlalchemy.orm import Session

from core.variables.variables import Variable
from extensions.ext_database import db
from models import ConversationVariable


class ConversationVariableNotFoundError(Exception):
    pass


class ConversationVariableUpdaterImpl:
    def __init__(self) -> None:
        self._pending_updates: list[tuple[str, Variable]] = []

    def update(self, conversation_id: str, variable: Variable) -> None:
        self._pending_updates.append((conversation_id, variable))

    def flush(self) -> None:
        for conversation_id, variable in self._pending_updates:
            stmt = select(ConversationVariable).where(
                ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id
            )
            with Session(db.engine) as session:
                row = session.scalar(stmt)
                if not row:
                    raise ConversationVariableNotFoundError("conversation variable not found in the database")
                row.data = variable.model_dump_json()
                session.commit()


def conversation_variable_updater_factory() -> ConversationVariableUpdaterImpl:
    return ConversationVariableUpdaterImpl()
