from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
from rpyc import Service
from requests import get
from json import load, dump, JSONDecodeError
from datetime import datetime
import argparse


class FinanceService(Service):
    def __init__(self, args):
        super().__init__()
        self.id = args.id
        self.api_key = args.apikey
        self.cache_loc = "/mnt/cache/{}.json".format(self.id)

    def exposed_get_price(self, stock: str):  # Returns the stock price of the given stock
        # Raw URL endpoint query is enough for our use case. API Key in the code is not necessarily good practice
        # but no need to over-engineer it right now. As soon as we get to multiple servers we should use multiple keys,
        # probably provided via environmental variables, config file or command line arguments

        # Try to read cache, reset it in case of reading errors or if it simply does not exist yet
        try:
            with open(self.cache_loc) as c:
                cache = load(c)
        except (JSONDecodeError, FileNotFoundError):
            cache = {}

        # First check if price is in cache already and price is up-to-date, if so return it from cache
        if stock in cache.keys() and cache[stock]["date"] == datetime.now().date().isoformat():
            return cache[stock]["price"], self.id
        else:
            # Otherwise query the api for the current price
            url = ("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}"
                   .format(stock, self.api_key))
            request = get(url)
            result = request.json()

            # Try catch block in case of API errors
            try:
                # Store result in cache before returning result
                cache[stock] = {
                    "price": float(result["Global Quote"]["05. price"]),
                    "date": datetime.now().date().isoformat()
                }
            except KeyError:
                print("Could not parse result, likely unknown stock or API limit. \n Result: {} \n Stock: {}"
                      .format(result, stock))
                return "-1", self.id

            # Write updated cache to disk before returning
            with open(self.cache_loc, "w") as c:
                dump(cache, c)
            return str(cache[stock]["price"]), self.id

    def exposed_stop_server(self):
        # Closes the server connection
        server.close()

parser = argparse.ArgumentParser()
parser.add_argument("-id", required=True, type=int)
parser.add_argument("-apikey", required=True)
args = parser.parse_args()

service = classpartial(FinanceService, args)
server = ThreadedServer(service, port=4242 + args.id - 1)

if __name__ == "__main__":
    server.start()
