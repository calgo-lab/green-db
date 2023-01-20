import pandas as pd
from sqlalchemy import func

from core.domain import Product
from database.connection import GreenDB
from database.tables import GreenDBTable


class DBConnection(GreenDB):
    def get_aggregated_unique_products(self):
        with self._session_factory() as db_session:
            query = db_session.query(func.max(self._database_class.id),
                                     func.array_agg(self._database_class.category),
                                     func.array_agg(self._database_class.gender)
                                     ).group_by(self._database_class.url).all()

            return pd.DataFrame(query, columns=["id", "categories", "genders"]).convert_dtypes()

    def get_products_with_ids(self, ids):
        with self._session_factory() as db_session:
            query = db_session.query(GreenDBTable).filter(GreenDBTable.id.in_(ids))
            return (Product.from_orm(row) for row in query.all())
