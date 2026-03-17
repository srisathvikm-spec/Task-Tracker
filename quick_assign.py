#!/usr/bin/env python3
"""Quick script to assign tasks to read-only user for testing."""

from sqlalchemy import create_engine, text

# LOCAL Database connection (same as backend config)
engine = create_engine('postgresql://postgres:9411@localhost:5432/task_tracker')

with engine.begin() as conn:
    # Get read-only user
    result = conn.execute(text("SELECT id, name, email FROM users WHERE email LIKE '%readonly%' OR email LIKE '%garikapatini%'"))
    users = result.fetchall()
    print('Read-only users found:')
    readonly_user_id = None
    for user in users:
        print(f'  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}')
        readonly_user_id = user[0]
    
    if not readonly_user_id:
        print("❌ No read-only user found!")
        exit(1)
    
    print(f'\n✅ Using read-only user ID: {readonly_user_id}')
    
    # Get tasks to assign
    result = conn.execute(text('SELECT id, title FROM tasks LIMIT 5'))
    tasks = result.fetchall()
    print(f'\nTasks to assign ({len(tasks)} tasks):')
    task_ids = []
    for task in tasks:
        print(f'  ID: {task[0]}, Title: {task[1]}')
        task_ids.append(task[0])
    
    # Assign tasks to read-only user
    if task_ids:
        for task_id in task_ids:
            conn.execute(text(f"UPDATE tasks SET assigned_to = '{readonly_user_id}' WHERE id = '{task_id}'"))
        print(f'\n✅ Assigned {len(task_ids)} tasks to read-only user!')
    else:
        print('\n⚠️  No tasks found to assign!')

print('\nDone!')

