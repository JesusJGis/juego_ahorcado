from pymongo import MongoClient
try:

    client = MongoClient('mongodb://localhost:27017/') 
    db = client['AhorcadoDB']
    usuarios_collection = db['usuarios']
    print("Conexión a MongoDB establecida.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")
    usuarios_collection = None