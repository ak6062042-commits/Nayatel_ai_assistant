import rag.ingest as obj

ingest = obj.Ingenstion()
cleaned = ingest.runCleaning(force = True)
chunks = ingest.runChunking(force = True)