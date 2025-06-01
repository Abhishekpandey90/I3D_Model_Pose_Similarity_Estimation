from fastapi import FastAPI, HTTPException #type: ignore
import os
import json
import cv2
import torch
import boto3 #type: ignore
from botocore.exceptions import NoCredentialsError, ClientError #type: ignore
import mediapipe as mp
import numpy as np
from torchvision import transforms
from database import SessionLocal, init_db

from torchvision.models.video import r3d_18
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv #type: ignore
load_dotenv()

# Load Pretrained ResNet-3D 18 model
model = r3d_18(pretrained=True)
model.eval()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

def download_video_from_s3(bucket_name, object_key):
    """Download a video file from S3 to a local temporary directory."""
    
    print("\n\n -----------------> Downloading video from S3...")
    local_filename = object_key.split('/')[-1]
    local_filepath = f"/tmp/{local_filename}"  # Store in temporary directory
    
    # Delete the existing file before downloading a new one
    if os.path.exists(local_filepath):
        os.remove(local_filepath)
    
    try:
        s3_client.download_file(Bucket=bucket_name, Key=object_key, Filename=local_filepath)
        return local_filepath
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise HTTPException(status_code=404, detail="S3 object not found")
        elif error_code == '403':
            raise HTTPException(status_code=403, detail="Access to the S3 object is forbidden. Check IAM permissions.")
        else:
            raise HTTPException(status_code=500, detail=f"S3 Client Error: {str(e)}")
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available. Check environment variables.")


# Initialize MediaPipe Pose for person detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

 
def detect_person_movement(video_path, static_threshold=0.0015):
    print("\n\n -----------------> Detecting person movement...")
    try:
        cap = cv2.VideoCapture(video_path)
        motion_scores = []
        prev_landmarks = None
        person_detected = False

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                person_detected = True
                landmarks = np.array([[lm.x, lm.y] for lm in results.pose_landmarks.landmark])

                if prev_landmarks is not None:
                    movement = np.linalg.norm(landmarks - prev_landmarks, axis=1).mean()
                    motion_scores.append(movement)

                prev_landmarks = landmarks

        cap.release()

        if not person_detected:
            return False, False, False

        avg_motion = np.mean(motion_scores) if motion_scores else 0
        return person_detected, avg_motion >= static_threshold, "Success"
    
    except Exception as e:
        return "Failed"

def extract_video_clips(video_path, clip_length=16):
    print("\n\n ------------------> Extract video Clips...")
    cap = cv2.VideoCapture(video_path)
    frames, clips = [], []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (112, 112))
        frame = np.array(frame, dtype=np.float32) / 255.0
        frames.append(frame)

        if len(frames) == clip_length:
            clips.append(np.array(frames))
            frames = []

    if len(frames) > 0:
        while len(frames) < clip_length:
            frames.append(frames[-1])
        clips.append(np.array(frames))

    cap.release()
    return np.array(clips)

def get_video_embedding(video_path):
    print("\n\n ------------------> Get video embedding...")
    clips = extract_video_clips(video_path)
    if len(clips.shape) != 5:
        raise ValueError(f"Expected shape (num_clips, 16, 112, 112, 3), but got {clips.shape}")

    embeddings = []
    transform = transforms.Compose([transforms.Normalize(mean=[0.5], std=[0.5])])

    for clip in clips:
        clip_tensor = torch.tensor(clip, dtype=torch.float32)
        clip_tensor = clip_tensor.permute(3, 0, 1, 2).unsqueeze(0)
        clip_tensor = transform(clip_tensor)

        with torch.no_grad():
            emb = model(clip_tensor)
            embeddings.append(emb.cpu().numpy())

    return np.mean(embeddings, axis=0)

def compare_videos(video1_path, video2_path):
    print("\n\n ------------------> Compare videos...")
    emb1 = get_video_embedding(video1_path).flatten()
    emb2 = get_video_embedding(video2_path).flatten()

    emb1, emb2 = np.tanh(emb1), np.tanh(emb2)
    emb1, emb2 = normalize([emb1])[0], normalize([emb2])[0]

    return cosine_similarity([emb1], [emb2])[0][0]

