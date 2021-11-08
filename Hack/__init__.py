from .config import config
import logging
import json
from datetime import date, datetime
import random
# from cosmosdb import DatabaseConnection
# from cosmosdb import getItem, getReplacedItem
import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Initialize the Cosmos client
    endpoint = config["ENDPOINT"]
    key = config["PRIMARYKEY"]

    # <create_cosmos_client>
    client = CosmosClient(endpoint, key)
    # </create_cosmos_client>

    # Create a database
    # <create_database_if_not_exists>
    database_name = config["DATABASE"]
    database = client.create_database_if_not_exists(id=database_name)
    # </create_database_if_not_exists>

    # Create a container
    # Using a good partition key improves the performance of database operations.
    # <create_container_if_not_exists>
    container_name = config["CONTAINER"]
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/pk"),
        offer_throughput=400
    )
    #  </create_container_if_not_exists>

    # Query these items using the SQL query syntax.
    # Specifying the partition key value in the query allows Cosmos DB to retrieve data only from the relevant partitions, which improves performance
    # <query_items>
    query = "SELECT * FROM cWHERE c.id = '1'"

    item = container.read_item(item="1", partition_key="1")

    request_charge = container.client_connection.last_response_headers['x-ms-request-charge']

    print('Read item with airvolume {0}. Operation consumed {1} request units'.format(
        item['airvolume'], (request_charge)))
    # </query_items>

    # TODO CosmosDBへ接続
    datetime1 = datetime(2021, 11, 11, 12, 00).isoformat()
    airVolume = "middle"

    num = random.randint(1, 10)
    if num > 7:
        airVolume = "strong"
    elif num > 3:
        airVolume = "normal"
    else:
        airVolume = "weak"

    res = {
        "dateTime": datetime1,
        "airVolume": airVolume
    }

    return func.HttpResponse(
        body=json.dumps(res),
        mimetype="application/json",
        charset="utf-8",
        status_code=200
    )
