# reminder_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import db
from utils.email_sender import send_email
from datetime import datetime, timezone

tasks_collection = db["tasks"]

async def send_due_reminders():
    now = datetime.now(timezone.utc)
    print(f"[Reminder Scheduler] Checking reminders at {now.isoformat()}")

    cursor = tasks_collection.find({"remind_at": {"$lte": now}})

    async for task in cursor:
        task_title = task.get("title", "Task Reminder")
        user_email = task.get("user_email")
        if user_email:
            print(f"[Reminder Scheduler] Sending reminder for task: {task_title} to {user_email}")
            try:
                send_email(
                    to_email=user_email,
                    subject=f"Reminder: {task_title}",
                    body=f"Hello! This is a reminder for your task: {task_title}"
                )
            except Exception as e:
                print(f"[Reminder Scheduler] Error sending email: {e}")

        # Remove the reminder after sending
        await tasks_collection.update_one(
            {"task_id": task["task_id"]},
            {"$unset": {"remind_at": ""}}
        )
        print(f"[Reminder Scheduler] Reminder removed for task: {task_title}")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Schedule the async function directly
    scheduler.add_job(send_due_reminders, 'interval', seconds=60, coalesce=True, misfire_grace_time=30)
    scheduler.start()
    print("[Reminder Scheduler] Scheduler started...")
