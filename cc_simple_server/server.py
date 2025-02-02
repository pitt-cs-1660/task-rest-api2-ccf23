from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from cc_simple_server.models import TaskCreate
from cc_simple_server.models import TaskRead
from cc_simple_server.database import init_db
from cc_simple_server.database import get_db_connection


# init
init_db()

app = FastAPI()

############################################
# Edit the code below this line
############################################

@app.get("/")
async def read_root():
    """
    This is already working!!!! Welcome to the Cloud Computing!
    """
    return {"message": "Welcome to the Cloud Computing!"}

# POST ROUTE data is sent in the body of the request
@app.post("/tasks/", response_model=TaskRead)
async def create_task(task_data: TaskCreate):
    """
    Create a new task

    Args:
        task_data (TaskCreate): The task data to be created

    Returns:
        TaskRead: The created task data
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
        (task_data.title, task_data.description, task_data.completed),
        )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return TaskRead(id=task_id, title=task_data.title,
                     description=task_data.description,
                     completed=task_data.completed)

# GET ROUTE to get all tasks
@app.get("/tasks/", response_model=list[TaskRead])
async def get_tasks():
    """
    Get all tasks in the whole wide database

    Args:
        None

    Returns:
        list[TaskRead]: A list of all tasks in the database
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [TaskRead(id=row["id"], title=row["title"],
                     description=row["description"],
                     completed=bool(row["completed"])) for row in rows]


# UPDATE ROUTE data is sent in the body of the request and the task_id is in the URL
@app.put("/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskCreate):
    """
    Update a task by its ID

    Args:
        task_id (int): The ID of the task to be updated
        task_data (TaskCreate): The task data to be updated

    Returns:
        TaskRead: The updated task data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
                   "SELECT EXISTS(SELECT 1 FROM tasks WHERE id = ?)", (task_id,)
                   )
    existance = cursor.fetchone()[0]
    if existance == 1:
        for row in cursor.execute("SELECT "+ str(task_id) + " FROM tasks"):
            cursor.execute(
                           "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
                           (task_data.title, task_data.description, task_data.completed, task_id),
                           )
        conn.commit()
        conn.close()
        return TaskRead(id=task_id, title=task_data.title,
                        description=task_data.description,
                        completed=task_data.completed)
    else:
        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with ID {task_id} not found"
                            )


# DELETE ROUTE task_id is in the URL
@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    """
    Delete a task by its ID

    Args:
        task_id (int): The ID of the task to be deleted

    Returns:
        dict: A message indicating that the task was deleted successfully
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
                   "SELECT EXISTS(SELECT 1 FROM tasks WHERE id = ?)", (task_id,)
                   )
    existance = cursor.fetchone()[0]
    if existance == 1:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        print("deleted")
        return {"message": "Task" + str(task_id) + "deleted"}
    else:
        print("exception raised")
        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with ID {task_id} not found"
                            )
