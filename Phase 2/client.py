from rpyc import connect
from time import time
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-id", required=True, type=int)
id = parser.parse_args().id

if __name__ == "__main__":
    server_ip = "nginx"  # Let docker handle IP addresses and such
    server_port = 4200

    # Establish connection (allowing server to initialise cache)
    conn = connect(server_ip, server_port)
    stocks = [["GOOGL", "Google"], ["MSFT", "Microsoft"], ["AMZN", "Amazon"], ["AAPL", "Apple"], ["META", "Meta"], ["IBM", "IBM"], ["TSLA", "Tesla"], ["WMT", "Walmart"], ["AHODF", "Ahold Delhaize"], ["DIS", "Walt Disney Co"]]
    response_times = np.array([])
    for stock_ticker_name in stocks:
        start_time = time()
        stock_price, server_id = conn.root.get_price(stock_ticker_name[0])
        response_times = np.append(response_times, ((time() - start_time) * 1000))
        print("Stock Price for {}: ${}\n\t From server: {}, From client: {}\n\trequest answered in {} milliseconds".format(stock_ticker_name[1], stock_price, server_id, id, round(response_times[len(response_times) - 1], 3)))

    print("Average response time: {} milliseconds".format(round(np.average(response_times)), 3))
    # Close server gracefully such that it can save the cache and catch the thrown EOFError
    # try:
    #     conn.root.stop_server()
    # except EOFError:
    #     pass
