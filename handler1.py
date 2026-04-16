#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import boto3
import os
import subprocess

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    print(f"Received Event: {event}")
    # Extract bucket and key from the event triggered by S3
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(f"Bucket name: {source_bucket}, Key {key}")

    # Define paths and folder names
    local_video_path = f"/tmp/{key}"
    video_name = os.path.splitext(os.path.basename(key))[0]
    output_folder = f"/tmp/{video_name}"
    
    # Create output directory for storing frames
    os.makedirs(output_folder, exist_ok=True)
    
    # Download the video from the input S3 bucket
    s3_client.download_file(source_bucket, key, local_video_path)
    print(f"Video File downloaded from S3 bucket")

    # Use ffmpeg to split the video into frames
    ffmpeg_command = [
        "ffmpeg",
        "-ss", "0",
        "-r", "1",
        "-i", local_video_path,
        "-vf", "fps=2",
        "-start_number", "0",
        "-vframes", "10",
        f"{output_folder}/output-%02d.jpg",
        "-y"
    ]
    split_cmd = 'ffmpeg -i ' + local_video_path + ' -vframes 10 ' + f"{output_folder}/output-%02d.jpg"
    
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        return {"status": "Error", "message": str(e)}
    print(f"Video File splitted into images")

    # Upload each frame to the output S3 bucket
    destination_bucket = source_bucket.replace("-input", "-stage-1")
    for frame in os.listdir(output_folder):
        print(f"Frame:{frame}")
        frame_path = os.path.join(output_folder, frame)
        s3_client.upload_file(
            frame_path,
            destination_bucket,
            f"{video_name}/{frame}"
        )
    print(f"Images uploaded to stage1 bucket")

    # Cleanup
    os.remove(local_video_path)
    for frame in os.listdir(output_folder):
        os.remove(os.path.join(output_folder, frame))
    
    print("Video splitting and uploading completed.")
    return {"status": "Success"}

