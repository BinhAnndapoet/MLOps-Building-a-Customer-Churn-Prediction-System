from feast import Entity
from feast.value_type import ValueType

customer = Entity(
    name="customer_id",
    description="A customer entity with unique customer ID",
    join_keys=["customer_id"],
    value_type=ValueType.STRING,
    tags = {
        "owner": "data__team",
        "domain": "customer_analytics",
        "team": "BAn"
    }
)
