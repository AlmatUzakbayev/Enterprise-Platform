import asyncio
from services.vector_store import VectorStore


async def reset():
    vs = VectorStore()
    collections = await vs.client.get_collections()
    names = [c.name for c in collections.collections]
    if vs.collection in names:
        await vs.client.delete_collection(vs.collection)
        print(f"Deleted: {vs.collection}")
    else:
        print("Not found, nothing to delete")
    print("Done. New collection will be created on first document upload.")


asyncio.run(reset())

