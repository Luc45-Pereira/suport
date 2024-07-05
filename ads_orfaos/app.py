from mercadolivreverifications import ProductVerification
from pprint import pprint

manager = ProductVerification('APP_USR-5417402069385811-010612-021c94173d01ab90ae5021c7dbfc1995-592589493', ["MLB3360863607"])

pprint(manager.verify_state_products(["review", "closed"]))