from classes.api import Api
from dotenv import load_dotenv

def run():
    api = Api()
    api.check_invoices()

if __name__ == "__main__":
    load_dotenv()
    run()