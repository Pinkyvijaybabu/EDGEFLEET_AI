import sqlite3, json, time

class EventDB:
    def __init__(self, path='edgefleet.db'):
        self.path=path
        with sqlite3.connect(path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, level TEXT, event TEXT, data TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, name TEXT, result TEXT)')

    def event(self, level, event, data=None):
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT INTO events(ts,level,event,data) VALUES(?,?,?,?)',(time.time(),level,event,json.dumps(data or {})))

    def recent(self, limit=80):
        with sqlite3.connect(self.path) as c:
            rows=c.execute('SELECT ts,level,event,data FROM events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [{'ts':r[0],'level':r[1],'event':r[2],'data':json.loads(r[3])} for r in rows]

    def experiment(self,name,result):
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT INTO experiments(ts,name,result) VALUES(?,?,?)',(time.time(),name,json.dumps(result)))
