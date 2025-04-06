@app.post("/api/search_tickets")
def search_tickets(req: RequestData):
    query = req.query
    results = ticket_vector_store.search_similar_tickets(query)
    return {"results": results}
