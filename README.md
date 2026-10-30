# 🎓 StudentSphere — A Serverless Student Career Portal

> A fully serverless web application for real-time student career profile management, built entirely on **Amazon Web Services (AWS)**.

---

## 📌 Project Info

## 🚀 Live Demo

🌐 [StudentSphere Portal](http://studentsphere-portal-aj-4821.s3-website-us-east-1.amazonaws.com)

## 📖 About the Project

StudentSphere enables students to:
- Create and manage their academic and career profiles
- View a dynamically calculated **Career Readiness Score** (0–100)
- Generate and download a **one-click resume**
- Log in securely using **Amazon Cognito** authentication

Administrators can:
- View, search, edit, and delete all student records
- Export student data as **CSV**
- Monitor overall student statistics

---

## 🏗️ AWS Architecture

```
Browser (S3) → Amazon Cognito → API Gateway → AWS Lambda (Python) → DynamoDB
```

| AWS Service | Purpose |
|---|---|
| **Amazon S3** | Static website hosting — serves HTML, CSS, JavaScript |
| **Amazon Cognito** | User authentication — signup, login, JWT token |
| **API Gateway** | REST API — receives and routes all API calls |
| **AWS Lambda** | Backend logic — Python 3.12 with boto3 |
| **Amazon DynamoDB** | NoSQL database — stores all student profiles |
| **AWS IAM** | Lambda execution role — grants DynamoDB permissions |

---

## 📊 Career Readiness Score Formula

| Parameter | Max Points |
|---|---|
| GPA | 30 |
| Skills | 25 |
| Certifications | 20 |
| Projects | 15 |
| LinkedIn Profile | 5 |
| GitHub Profile | 5 |
| **Total** | **100** |

---

## 🗂️ Project Structure

```
StudentSphere/
├── index.html            # Complete frontend (HTML + CSS + JavaScript)
├── lambda_function.py    # AWS Lambda backend (Python 3.12)
└── README.md             # Project documentation
```

---

## ⚙️ Features

- ✅ Secure Sign Up / Sign In via Amazon Cognito
- ✅ Student profile creation with SAP ID, Roll Number, GPA, Skills, Certifications, Projects
- ✅ Dynamic Career Readiness Score (0–100)
- ✅ One-click Resume Generation (browser print-to-PDF)
- ✅ Admin Panel with search, filter, view, edit, delete, CSV export
- ✅ Email-based profile lookup on login
- ✅ Fully serverless — zero server management
- ✅ Pay-per-use AWS billing — no idle cost

---

## 🔐 Authentication Flow

1. Student signs up / logs in with email and password via **Amazon Cognito**
2. Cognito returns a signed **JWT ID Token**
3. Browser attaches the token to every API request as `Authorization` header
4. **API Gateway** validates the token before forwarding to Lambda
5. Expired or invalid tokens are rejected with HTTP 401

---

## 🛠️ API Endpoints

**Base URL:** `https://hixpz8z208.execute-api.us-east-1.amazonaws.com/prod/student`

| Method | Parameters | Purpose |
|---|---|---|
| GET | `?student_id=<SAP_ID>` | Fetch profile by SAP ID |
| GET | `?email=<email>` | Fetch profile by email |
| GET | `?admin=true` | Fetch all students (admin) |
| POST | JSON body | Save / update student profile |
| POST | `_action=delete` in body | Delete student record |
| OPTIONS | — | CORS preflight response |

---

## 📦 DynamoDB Schema

**Table:** `StudentProfiles` | **Primary Key:** `student_id` (String)

| Field | Description |
|---|---|
| student_id | SAP ID (Primary Key) |
| sap_id | SAP ID |
| roll_number | e.g. D064 |
| full_name | Student name |
| email | Cognito login email |
| department | e.g. CSE-DS |
| year_of_study | e.g. 3rd Year |
| gpa | GPA on 4.0 scale |
| skills | Comma-separated |
| certifications | Comma-separated |
| projects | Project titles |
| linkedin_url | LinkedIn profile URL |
| github_url | GitHub profile URL |
| career_goal | Career objective |

---

## 🔮 Future Enhancements

- ML model for personalized career path recommendations (Amazon SageMaker)
- Job board integration with LinkedIn and Naukri APIs
- Role-based access control (RBAC) via AWS Cognito User Groups
- React Native mobile application
- Bulk student import via CSV
- Email notifications via Amazon SES

---

## 📚 References

1. AWS DynamoDB Developer Guide — https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
2. AWS Lambda Developer Guide — https://docs.aws.amazon.com/lambda/latest/dg/
3. Amazon Cognito Developer Guide — https://docs.aws.amazon.com/cognito/latest/developerguide/
4. AWS Well-Architected Framework — Serverless Lens — https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/
5. JSON Web Token (JWT) — RFC 7519 — https://datatracker.ietf.org/doc/html/rfc7519

---

## 🙏 Acknowledgements

We sincerely thank **Dr. Naresh Vurukonda** and the Department of CSE Data Science, SVKM's NMIMS University, Hyderabad Campus, for their guidance and invaluable support throughout this project.

---
