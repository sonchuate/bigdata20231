# # # # Import the necessary modules

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from pyspark.sql.functions import explode, col
from confluent_kafka import Consumer, KafkaException

import time
import json
from pymongo import MongoClient
def convertJson2DF(spark, data):
    # Sử dụng spark.read.json để chuyển đổi chuỗi JSON thành DataFrame
    df = spark.read.json(spark.sparkContext.parallelize(data))

    try:
        # Sử dụng explode để chuyển đổi mảng thành các hàng mới và chọn các cột cần thiết
        result_df = df.select(
            explode("data").alias("data")
        ).select(
            col("data.c"),
            col("data.p"),
            col("data.s"),
            col("data.t"),
            col("data.v")
        )
    except:
        print('not exits data')

    # Hiển thị DataFrame mới
    result_df.show(truncate=False)
    return result_df


# from pymongo import MongoClient
spark = SparkSession.builder.appName("KafkaStreamToDataFrame").getOrCreate()
schema = StructType([
    StructField("c", StringType(), True),
    StructField("p", StringType(), True),
    StructField("s", StringType(), True),
    StructField("t", StringType(), True),
    StructField("v", StringType(), True)
])
schema1 = StructType([
    StructField("data", StructType([
        StructField("c", StringType()),
        StructField("p", StringType()),
        StructField("s", StringType()),
        StructField("t", StringType()),
        StructField("v", StringType())
    ])),
    StructField("type", StringType())
])
mongo_username = 'root'
mongo_password = '123456'
mongo_host = 'mongoDB-Cont'
# mongo_host = 'localhost'
mongo_port = 27017
mongo_database = 'admin'  # Replace with your actual database name
empty_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)
bootstrap_servers = 'kafka'  # Replace with the actual IP address or hostname
topic = 'websocket_messages-stock'
mongo_uri = f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}'
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}')
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}')
# mongo_client = MongoClient('localhost', 27018)
# MongoDB connection setup

db = mongo_client['db_stock']  # Replace with your actual database name
collection = db['stock_collection']  # Replace with your actual collection name

try:
    # Check if the script can connect to the MongoDB database
    mongo_client.server_info()
    print('connect successfully')
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

print('hêhee')



consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'stock_group_id',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(consumer_config)
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                continue
            else:
                print('Error: {}'.format(msg.error()))
                break

        received_message = msg.value().decode('utf-8')
        print('Received message: {}'.format(received_message))

        # Parse the JSON message
        data = json.loads(received_message)


        # Insert the data into MongoDB
        # if 'data' in data and isinstance(data['data'], list):
        #     # Insert each element of the 'data' array as a separate document
        #     for element in data['data']:
        #         collection.insert_one(element)
        # new_data = []
        # # try:
        # for d in data['data']:
        #     print(d['s'],str(d['v']))
        #     new_data.append((d['c'], d['p'], d['s'], d['t'], d['v']))
        #     # data = [(msg.key(), msg.value())]
        # print(new_data)
        # new_df = spark.createDataFrame(new_data, schema)
        # combined_df = empty_df.union(new_df)
        # combined_df = spark.read.json(spark.sparkContext.parallelize([received_message]), schema=schema)
        df = convertJson2DF(spark=spark, data=[received_message])
        records = df.collect()
        for record in records:
            record_dict = record.asDict()
            collection.insert_one(record_dict)
        # combined_df.show()
        # except:
        #     pass
        # time.sleep(1)  # Adjust the interval as needed

except KeyboardInterrupt:
    pass
finally:
    consumer.close()


# # # # Import the necessary modules

# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType, StructField, StringType
# from confluent_kafka import Consumer, KafkaException
# import time
# import json
# # from pymongo import MongoClient
# spark = SparkSession.builder.appName("KafkaStreamToDataFrame").getOrCreate()
# schema = StructType([
#     StructField("c", StringType(), True),
#     StructField("p", StringType(), True),
#     StructField("s", StringType(), True),
#     StructField("t", StringType(), True),
#     StructField("v", StringType(), True)
# ])

# # {"c":null,"p":41713.98,"s":"BINANCE:BTCUSDT","t":1703927224751,"v":0.00014}
# empty_df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)
# bootstrap_servers = 'kafka'  # Replace with the actual IP address or hostname
# topic = 'websocket_messages-stock'


# consumer_config = {
#     'bootstrap.servers': bootstrap_servers,
#     'group.id': 'stock_group_id',
#     'auto.offset.reset': 'earliest',
# }

# consumer = Consumer(consumer_config)
# consumer.subscribe([topic])

# try:
#     while True:
#         msg = consumer.poll(1.0)

#         if msg is None:
#             continue
#         if msg.error():
#             if msg.error().code() == KafkaException._PARTITION_EOF:
#                 continue
#             else:
#                 print('Error: {}'.format(msg.error()))
#                 break

#         received_message = msg.value().decode('utf-8')
#         print('Received message: {}'.format(received_message))

#         # Parse the JSON message
#         data = json.loads(received_message)
#         new_data = []
#         # try:
#         for d in data['data']:
#             print(d['s'],str(d['v']))
#             new_data.append((d['c'], d['p'], d['s'], d['t'], d['v']))
#             # data = [(msg.key(), msg.value())]
#             print(new_data)
#             new_df = spark.createDataFrame(new_data, schema)
#             combined_df = empty_df.union(new_df)
#             combined_df.show()
#         # except:
#         #     pass
#         # time.sleep(1)  # Adjust the interval as needed

# except KeyboardInterrupt:
#     pass
# finally:
#     consumer.close()

# docker-compose exec spark-master spark-submit --master spark://172.18.0.8:7077 anyfilename.py

# from pyspark.sql import SparkSession
# from pyspark.sql.functions import explode, col

# # Tạo Spark session
# spark = SparkSession.builder.appName("example").getOrCreate()

# # Dữ liệu JSON dưới dạng chuỗi
# json_string = '''
# {
#     "data": [
#         {"c": null, "p": 42418.72, "s": "BINANCE:BTCUSDT", "t": 1704011100006, "v": 0.00135},
#         {"c": null, "p": 42418.72, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00132},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00083},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00223},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100008, "v": 0.00194},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100008, "v": 0.00071},
#         {"c": null, "p": 42418.72, "s": "BINANCE:BTCUSDT", "t": 1704011100009, "v": 0.0005}
#     ],
#     "type": "trade"
# }
# '''
# json_string1 = '''
# {
#     "data": [
#         {"c": null, "p": 42418.72, "s": "hehe", "t": 1704011100006, "v": 0.00135},
#         {"c": null, "p": 42418.72, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00132},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00083},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100007, "v": 0.00223},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100008, "v": 0.00194},
#         {"c": null, "p": 42418.71, "s": "BINANCE:BTCUSDT", "t": 1704011100008, "v": 0.00071},
#         {"c": null, "p": 42418.72, "s": "BINANCE:BTCUSDT", "t": 1704011100009, "v": 0.0005}
#     ],
#     "type": "trade"
# }
# '''

# convertJson2DF(spark=spark, data=[json_string,json_string1])


