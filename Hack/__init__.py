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
    try:
        logging.info('Python HTTP trigger function processed a request.')
        # CD動作確認
        # DB初期設定
        endpoint = config["ENDPOINT"]
        key = config["PRIMARYKEY"]

        client = CosmosClient(endpoint, key)

        database_name = config["DATABASE"]
        database = client.create_database_if_not_exists(id=database_name)

        container_name = config["CONTAINER"]
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        airvolumeReq = req.params.get('airvolume')
        if not airvolumeReq:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                airvolumeReq = req_body.get('airvolume')

        # レコードの最大IDを取得
        totalNum = "1"
        for id in container.query_items(
                "SELECT value COUNT(1) FROM c", enable_cross_partition_query=True):
            totalNum = str(id)

        if airvolumeReq:
            # クエリがある場合、新規で追加
            newId = int(totalNum) + 1
            container.create_item(
                body={"id": str(newId), "pk": str(newId), "airvolume": airvolumeReq})
            return func.HttpResponse(
                body=json.dumps({"messeage": "success"}),
                mimetype="application/json",
                charset="utf-8",
                status_code=200
            )
        else:
            # クエリがない場合、最新のレコードを取得
            item = container.read_item(item=totalNum, partition_key=totalNum)

            request_charge = container.client_connection.last_response_headers[
                'x-ms-request-charge']

            print('Read item with airvolume {0}. Operation consumed {1} request units'.format(
                item['airvolume'], (request_charge)))

            datetime1 = datetime.now().isoformat()
            airVolume = item['airvolume']

            res = {
                "dateTime": datetime1,
                "airVolume": airVolume  # weak,normal,strong
            }

            return func.HttpResponse(
                body=json.dumps(res),
                mimetype="application/json",
                charset="utf-8",
                status_code=200
            )

    except Exception as e:
        logging.info("エラー発生")
        logging.info(e)
        res = {
            "dateTime": datetime(2021, 11, 11, 12, 00).isoformat(),
            "airVolume": "weak"
        }

        return func.HttpResponse(
            body=json.dumps(res),
            mimetype="application/json",
            charset="utf-8",
            status_code=200
        )
