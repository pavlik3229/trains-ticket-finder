from .runner import BeljdTicketCheckerApp
from .logger import setup_logging



def main():
    setup_logging()
    app = BeljdTicketCheckerApp()
    app.start()

if __name__ == "__main__":
    main()