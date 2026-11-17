import os, tempfile, unittest
fd, path = tempfile.mkstemp(suffix=".db"); os.close(fd)
os.environ["DB_PATH"] = path
from app import app, init_db

class Tests(unittest.TestCase):
    def setUp(self): init_db(); self.client=app.test_client()
    def test_health(self): self.assertEqual(self.client.get("/health").status_code,200)
    def test_create_and_list(self):
        r=self.client.post("/api/tickets",json={"title":"Wi-Fi","description":"No connection","requester":"Tester"})
        self.assertEqual(r.status_code,201)
        self.assertEqual(len(self.client.get("/api/tickets").get_json()),1)
    def test_validation(self): self.assertEqual(self.client.post("/api/tickets",json={"title":"Incomplete"}).status_code,400)
    def test_update(self):
        x=self.client.post("/api/tickets",json={"title":"VPN","description":"Issue","requester":"Tester"}).get_json()
        self.assertEqual(self.client.patch("/api/tickets/"+str(x["id"]),json={"status":"Resolved"}).status_code,200)
if __name__=="__main__": unittest.main()
