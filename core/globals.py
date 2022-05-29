from datetime import datetime

from app import app
from config import Vars


@app.context_processor
def inject_globals():
    is_snowy = True if datetime.now().month in Vars.SNOWY_MONTH else False
    return dict(is_snowy=is_snowy)
