API: https://jsonplaceholder.typicode.com (public fake REST API; writes are faked and not persisted)
POST /todos  body {"userId": number, "title": string, "completed": boolean}  -> 201, echoes body plus "id" (201 for the next id)
GET /todos/{id} -> 200 {"userId","id","title","completed"}; unknown id (e.g. 99999) -> 404 with body {}
No auth. Content-Type: application/json.
