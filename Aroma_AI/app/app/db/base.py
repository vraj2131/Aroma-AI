# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User, Customer # noqa
from app.models.address import Address # noqa
from app.models.delivery import Delivery # noqa
from app.models.feedback import Feedback # noqa
from app.models.notification import Notification # noqa
from app.models.order import Order,OrderItem, MenuItem # noqa
from app.models.reward import Reward # noqa
from app.models.table import Table # noqa
from app.models.waitingList import WaitingList #noqa
from app.models.chat import ChatData #noqa
from app.models.document import Document #noqa