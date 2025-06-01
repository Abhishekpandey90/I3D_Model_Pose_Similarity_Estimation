from fastapi import FastAPI
import os
from video_process import download_video_from_s3, detect_person_movement, compare_videos, get_db
from pydantic_schema import CoachVideoRequest, UserVideoRequest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession #type: ignore
from fastapi import FastAPI, Form, Depends  #type: ignore
from sqlalchemy import text #type: ignore

app = FastAPI()
load_dotenv()

@app.post("/compare-videos/")
async def compare_videos_api(coach_data: CoachVideoRequest, user_data: UserVideoRequest, 
                             db: AsyncSession = Depends(get_db),):
    
    accuracy = 0.00
    try:
        # =============== Database Queries ==========================
        fetch_ex_entry_query = text("""
            SELECT "roundId", "videoId", "type" FROM exercise 
            WHERE id = :exercise_id
        """)
        
        accuracy_update_query = text("""
                UPDATE user_data_exercise 
                SET accuracy = :accuracy
                WHERE id = :id
            """)
            
        # Fetch the existing exercise entry
        fetch_user_data_query = text("""
            SELECT "roundId", "videoId", "type", "standardPoses" FROM exercise 
            WHERE id = :coach_exercise_id
        """)
        
        coach_date_update_query = text("""
            UPDATE exercise 
            SET "standardPoses" = :standard_poses, "updatedAt" = timezone('Asia/Singapore', now())
            WHERE "id" = :exercise_id
        """)
        
        user_date_update_query = text("""
            UPDATE user_data_exercise 
            SET "updated_at" = timezone('Asia/Singapore', now())
            WHERE id = :id
        """)

        # =============== Fetching Data ==========================
        result = await db.execute(fetch_ex_entry_query, {"exercise_id": coach_data.exercise_id})
        exercise_entry = result.fetchone()

        if not exercise_entry:
            return {"status": "FAILED", "message": "No matching Coach exercise entry found."}
        
        # =============== Creating object keys for S3 =================
        coach_object_key = f"{coach_data.coach_id}/{os.path.basename(coach_data.exercise_url)}"
        user_object_key = f"{user_data.user_id}/{os.path.basename(user_data.exercise_url)}"
        
        # =============== Updating Date and Time in Database =================
        await db.execute(coach_date_update_query, {
            "standard_poses": None,
            "exercise_id": coach_data.exercise_id
        })
        await db.execute(user_date_update_query, {
            "id": user_data.user_exercise_id
        })
        await db.commit()
        
        # =============== Download videos from s3 ======================
        coach_video_path = download_video_from_s3(os.getenv("AWS_BUCKET_NAME"), coach_object_key)
        user_video_path = download_video_from_s3(os.getenv("AWS_BUCKET_NAME"), user_object_key)

        # =============== Check if videos exist ======================
        if not coach_video_path or not os.path.exists(coach_video_path):
            return {"status":"FAILED", "message":"Coach video not found"}
        
        if not user_video_path or not os.path.exists(user_video_path):
            return {"status":"FAILED", "message":"User video not found"}

        # =========== Detect persons, movements and processing status ====================
        is_person1, is_moving1, coach_video_process_status = detect_person_movement(coach_video_path)
        is_person2, is_moving2, user_video_process_status = detect_person_movement(user_video_path)
        
        if coach_video_process_status == "Failed":
            return {"status": "FAILED", "message": "Failed to process coach video file."}
        
        if user_video_process_status == "Failed":
            return {"status": "FAILED", "message": "Failed to process user video file."}

        if not is_person1 or not is_person2:
            return {"status":"FAILED", "message":"No person detected in one or both videos", "accuracy": accuracy}

        if not is_moving1 or not is_moving2:
            return {"status":"FAILED", "message":"Person detected but not moving in one or both videos", "accuracy": accuracy}
        
        # =============== Fetching the existing user exercise entry ==========================
        result = await db.execute(fetch_user_data_query, {"coach_exercise_id": user_data.coach_exercise_id})
        exercise_entry = result.fetchone()

        # Update accuracy to 0 if no matching entry is found
        if not exercise_entry:
            await db.execute(accuracy_update_query, {
            "id": user_data.user_exercise_id,
            "accuracy": accuracy
            })
            await db.commit()
            
            return {"status": "FAILED", "message": "No matching exercise entry found.", "accuracy": accuracy}

        # ============= Compare videos ==========================
        accuracy = compare_videos(coach_video_path, user_video_path)
        accuracy = round(accuracy * 100, 2)
        
        # ============= Update accuracy in the database ==========================
        await db.execute(accuracy_update_query, {
            "id": user_data.user_exercise_id,
            "accuracy": accuracy
        })
        await db.commit()
        
        return {"status":"SUCCESS", "accuracy": accuracy}
    
    except Exception as e:
        # ============= Update accuracy in the database ==========================
        await db.execute(accuracy_update_query, {
            "id": user_data.user_exercise_id,
            "accuracy": accuracy
        })
        await db.commit()
            
        return {"status":"FAILED", "message": f"Internal server error: {str(e)}"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
