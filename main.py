from datetime import datetime
from fastapi import FastAPI, Response # fastAPI on dokumentaatiosovellus
from pydantic import BaseModel
import sqlite3

con = sqlite3.connect("todos.sqlite", check_same_thread=False)

sql_create_todo_table = "CREATE TABLE IF NOT EXISTS todo(id INTEGER PRIMARY KEY, title VARCHAR, description VARCHAR, done INTEGER)"

with con:
    con.execute(sql_create_todo_table)

class TodoItem(BaseModel):
    id: int
    title: str
    done: bool
    description: str

class NewTodoItem(BaseModel):
    title: str
    description: str

app = FastAPI()

@app.on_event("shutdown")
def database_disconnect():
    con.close()

@app.get('/todos')  # tämän endpoint linkittyy siis fastapiin app:n kautta
def get_todos(done: bool | None = None):
    if done != None:
        return f"Tässä palautetaan myöhemmin todot, joiden done-status on: {done}"
    return "Tässä palautetaan myöhemmin todo-lista"

'''done: bool | None = None, tällä kerrotaan FastAPI:lle että done on tyyppiä boolean ja 
sen antaminen on vapaavalintaista. Oletusarvona done:lle asetetaan None. '''

@app.get('/todos/{id}')
def get_todo_by_id(id:int):
    todo_item = TodoItem(id=id, title="testi", done=False)
    return todo_item

''' Tämä aiemmin: 
@app.post('/todos')
def create_todo(todo_item: TodoItem):
    return todo_item'''

@app.post('/todos')
def create_todo(todo_item: NewTodoItem, response: Response):
    try:
        with con:
            dt = datetime.now()
            ts = int(datetime.timestamp(dt))
    
            cur = con.execute("INSERT INTO todo(title, description, done) VALUES (?, ?, ?)", (todo_item.title, todo_item.description, int(False),))
            response.status_code = 201
            return TodoItem(id=cur.lastrowid, title=todo_item.title, done=False, description=todo_item.description)
        
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


@app.put('/todos/{id}')
def update_todo(id: int, todo_item: TodoItem):
    return f"Myöhemmin tässä korvataan tietokannassa oleva todoitem uudella, jonka id on {id}"

@app.patch('/todos/{id}')
def update_todo_status(id: int, todo_item: TodoItem):
    return f"Myöhemmin tässä muokataan tietokannassa olevaa todoitemiä, jonka id on {id}"

@app.delete('/todos/{id}')
def delete_todo(id: int):
    return f"Myöhemmin tässä poistetaan tietokannasta todoitem, jonka id on {id}"

#testi