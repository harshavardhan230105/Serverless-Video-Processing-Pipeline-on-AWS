# 🚀 Serverless Video Processing Pipeline on AWS

An **event-driven, serverless pipeline** on AWS that automatically processes uploaded videos. When a video is uploaded to Amazon S3, a **Dockerized AWS Lambda function** is triggered, extracts frames using **FFmpeg**, and stores them in a staging bucket — ready for downstream analysis such as face recognition.

No servers to provision, automatic scaling, and pay-per-use cost.

---

## 📌 Problem Statement

Processing videos traditionally requires servers running 24/7, manual scaling, and ongoing maintenance — even when no videos are being uploaded. This project solves that by using a serverless, event-driven design that runs **only when a video arrives** and scales automatically with demand.

---

## 🏗️ Architecture

```
User uploads video
        │
        ▼
┌──────────────────────┐   S3 Event Notification    ┌─────────────────────────────────┐
│  S3: <name>-input    │ ─────(ObjectCreated)─────► │  AWS Lambda (Container Image)   │
└──────────────────────┘                            │  • Python 3.8 + FFmpeg          │
                                                    │  • Image stored in Amazon ECR   │
                                                    └───────────────┬─────────────────┘
                                                                    │ extracts frames
                                                                    ▼
                                                    ┌─────────────────────────────────┐
                                                    │  S3: <name>-stage-1             │
                                                    │  <video_name>/output-00.jpg ... │
                                                    └─────────────────────────────────┘

Logs → Amazon CloudWatch      Permissions → IAM execution role (least privilege)
```

---

## 🔄 Workflow

1. A user uploads a video (e.g. `test1.mp4`) to the **input S3 bucket**.
2. S3 sends an **ObjectCreated event** that triggers the Lambda function.
3. Lambda reads the bucket name and object key from the event and downloads the video to `/tmp`.
4. **FFmpeg** extracts up to **10 frames at 2 frames per second**.
5. Frames are uploaded to the **stage-1 bucket** under a folder named after the video:
   `<name>-stage-1/test1/output-00.jpg … output-09.jpg`
6. Temporary files are cleaned up and the function returns a status.

---

## 🧰 Tech Stack

| Category        | Technology                                   |
|-----------------|----------------------------------------------|
| Cloud           | AWS                                          |
| Storage         | Amazon S3                                    |
| Compute         | AWS Lambda (container image)                 |
| Containerization| Docker                                       |
| Image Registry  | Amazon ECR                                   |
| Video Processing| FFmpeg (static build)                        |
| Language / SDK  | Python 3.8, boto3                            |
| Monitoring      | Amazon CloudWatch Logs                       |
| Security        | AWS IAM                                      |

---

## ⚙️ Key Features

- **Fully serverless** — no servers to manage or patch
- **Event-driven** — processing starts automatically on upload
- **Containerized Lambda** — FFmpeg packaged in a Docker image (Lambda runtime does not include it)
- **Staged design** — separate input and output buckets decouple stages and prevent recursive triggers
- **Scalable & cost-efficient** — scales per upload, costs nothing when idle
- **Secure** — least-privilege IAM role, no hard-coded credentials

---

## 📂 Project Structure

```
Serverless-Video-Processing-Pipeline-on-AWS/
├── handler1.py        # Lambda function: download video, extract frames, upload to stage-1
├── Dockerfile         # Lambda container image with FFmpeg installed
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 🛠️ Deployment Steps

1. **Create S3 buckets**
   - `<name>-input` (uploads)
   - `<name>-stage-1` (extracted frames)

2. **Build the Docker image**
   ```bash
   docker build --platform linux/amd64 -t video-splitting .
   ```

3. **Push the image to Amazon ECR**
   ```bash
   aws ecr create-repository --repository-name video-splitting
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker tag video-splitting:latest <account-id>.dkr.ecr.<region>.amazonaws.com/video-splitting:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/video-splitting:latest
   ```

4. **Create the Lambda function**
   - Choose **Container image** and select the ECR image
   - Configure memory, timeout, and ephemeral storage as needed

5. **Attach an IAM execution role** with:
   - `AWSLambdaBasicExecutionRole` (CloudWatch logs)
   - `s3:GetObject` on the input bucket
   - `s3:PutObject` on the stage-1 bucket

6. **Add an S3 trigger** on the input bucket for `ObjectCreated` events (optional suffix filter: `.mp4`).

7. **Test** — upload a video to the input bucket and check the stage-1 bucket and CloudWatch logs.

---

## 🧪 Local Testing

The AWS Lambda base image includes the Runtime Interface Emulator:

```bash
docker run -p 9000:8080 video-splitting
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @sample-s3-event.json
```

---

## 📈 Learning Outcomes

- Designing **serverless, event-driven architectures**
- Packaging native binaries into **Lambda container images** with Docker and ECR
- Working with Lambda constraints (`/tmp` storage, timeout, cold starts)
- Applying **least-privilege IAM** security
- Monitoring and debugging with **CloudWatch Logs**

---

## 🔮 Future Enhancements

- **Face recognition stage:** trigger a second Lambda on the stage-1 bucket to analyze frames with **Amazon Rekognition**
- Store results in **DynamoDB** and expose them through **API Gateway**
- Error handling with **SQS dead-letter queue** and retries
- Handle URL-encoded and nested S3 keys; process all event records
- **Infrastructure as Code** using Terraform or AWS SAM
- **CI/CD pipeline** (GitHub Actions) for automated build and deployment
- **CloudWatch dashboards and alarms**
- Upgrade runtime to a newer Python version

---

## 🙏 Acknowledgment

Built as part of an academic cloud computing project, based on a template provided by VISA Lab (MIT License).

---

## 📜 License

This project is for educational and learning purposes.
