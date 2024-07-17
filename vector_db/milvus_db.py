from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

class MilvusDB:
    def __init__(self, host='localhost', port='19530'):
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        connections.connect("default", host=self.host, port=self.port)

    def create_collection(self, collection_name, dim):
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=35535),
            FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500)
        ]
        schema = CollectionSchema(fields, "CUDA documentation chunks")
        collection = Collection(collection_name, schema)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 1024}
        }
        collection.create_index("embedding", index_params)
        return collection

    def insert_data(self, collection, embeddings, chunks):
        entities = [
            [i for i in range(len(embeddings))],
            embeddings,
            [chunk.page_content for chunk in chunks],
            [chunk.metadata['source'] for chunk in chunks]
        ]
        collection.insert(entities)
        collection.flush()
        print(f"Inserted {len(embeddings)} entities into Milvus")