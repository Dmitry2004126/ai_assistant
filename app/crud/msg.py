from app.crud.base import CRUDBase
from app.models.msg import Msg


class CRUDMsg(CRUDBase[Msg]):...


msg_crud = CRUDMsg(Msg)
