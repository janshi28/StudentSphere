import json
import boto3
import logging
from decimal import Decimal
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('StudentProfiles')

# ─────────────────────────────────────────────
# Helper: CORS Headers (required for browser access)
# ─────────────────────────────────────────────
CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-admin-token',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
}

def build_response(status_code, body):
    """Build a standardized HTTP response."""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, default=decimal_serializer)
    }

def decimal_serializer(obj):
    """Convert Decimal types from DynamoDB to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# ─────────────────────────────────────────────
# HANDLER: Save / Update Student Profile (POST)
# ─────────────────────────────────────────────
def save_student(body):
    """Save or update a student profile in DynamoDB."""
    try:
        required_fields = ['student_id', 'full_name', 'email', 'department']
        for field in required_fields:
            if field not in body or not str(body[field]).strip():
                return build_response(400, {
                    'success': False,
                    'message': f"Missing or empty required field: '{field}'"
                })

        # Build the item to store
        item = {
            'student_id':     body['student_id'].strip(),
            'sap_id':         body.get('sap_id', '').strip(),
            'roll_number':    body.get('roll_number', '').strip(),
            'full_name':      body.get('full_name', body.get('name', '')).strip(),
            'email':          body['email'].strip().lower(),
            'department':     body.get('department', body.get('major', '')).strip(),
            'year_of_study':  body.get('year_of_study', body.get('graduation_year', '')).strip(),
            'gpa':            str(body.get('gpa', '')).strip(),
            'skills':         body.get('skills', '').strip(),
            'certifications': body.get('certifications', '').strip(),
            'projects':       body.get('projects', '').strip(),
            'linkedin_url':   body.get('linkedin_url', body.get('linkedin', '')).strip(),
            'github_url':     body.get('github_url', body.get('github', '')).strip(),
            'career_goal':    body.get('career_goal', '').strip(),
            'updated_at':     datetime.utcnow().isoformat() + 'Z'
        }

        # PutItem will create or overwrite the record
        table.put_item(Item=item)
        logger.info(f"Saved profile for student_id: {item['student_id']}")

        return build_response(200, {
            'success': True,
            'message': 'Student profile saved successfully!',
            'student_id': item['student_id']
        })

    except Exception as e:
        logger.error(f"Error saving student: {str(e)}")
        return build_response(500, {
            'success': False,
            'message': f"Internal server error: {str(e)}"
        })

# ─────────────────────────────────────────────
# HANDLER: Get Student Profile by ID (GET)
# ─────────────────────────────────────────────
def get_student(student_id):
    """Fetch a student profile — tries direct get first, then scans by sap_id/roll_number/email."""
    try:
        if not student_id:
            return build_response(400, {
                'success': False,
                'message': "Missing required query parameter: 'student_id'"
            })

        sid = student_id.strip()

        # 1. Try direct lookup by student_id (partition key — fastest)
        response = table.get_item(Key={'student_id': sid})
        item = response.get('Item')

        # 2. If not found, scan for matching sap_id, roll_number, or email
        if not item:
            from boto3.dynamodb.conditions import Attr
            scan_resp = table.scan(
                FilterExpression=(
                    Attr('sap_id').eq(sid) |
                    Attr('roll_number').eq(sid) |
                    Attr('email').eq(sid.lower())
                )
            )
            items = scan_resp.get('Items', [])
            if items:
                item = items[0]

        if not item:
            return build_response(404, {
                'success': False,
                'message': f"No student found with ID: '{student_id}'"
            })

        logger.info(f"Fetched profile for student_id: {student_id}")
        return build_response(200, {
            'success': True,
            'data': item
        })

    except Exception as e:
        logger.error(f"Error fetching student: {str(e)}")
        return build_response(500, {
            'success': False,
            'message': f"Internal server error: {str(e)}"
        })

# ─────────────────────────────────────────────
# HANDLER: Get Student by Email (GET with email param)
# ─────────────────────────────────────────────
def get_student_by_email(email):
    """Scan DynamoDB for a student by email address."""
    try:
        if not email:
            return build_response(400, {'success': False, 'message': "Missing email"})
        from boto3.dynamodb.conditions import Attr
        scan_resp = table.scan(
            FilterExpression=Attr('email').eq(email.strip().lower())
        )
        items = scan_resp.get('Items', [])
        if not items:
            return build_response(404, {'success': False, 'message': f"No student found with email: '{email}'"})
        item = items[0]
        logger.info(f"Fetched profile by email: {email}")
        return build_response(200, {'success': True, 'data': item})
    except Exception as e:
        logger.error(f"Error fetching student by email: {str(e)}")
        return build_response(500, {'success': False, 'message': f"Internal server error: {str(e)}"})

# ─────────────────────────────────────────────
# HANDLER: Admin — Get ALL Students (GET scan)
# ─────────────────────────────────────────────
def get_all_students():
    """Scan entire DynamoDB table — admin only."""
    try:
        result = table.scan()
        items = result.get('Items', [])

        # Handle DynamoDB pagination (if table has >1MB of data)
        while 'LastEvaluatedKey' in result:
            result = table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
            items.extend(result.get('Items', []))

        logger.info(f"Admin scan returned {len(items)} students")
        return build_response(200, {
            'success': True,
            'students': items,
            'count': len(items)
        })

    except Exception as e:
        logger.error(f"Error scanning students: {str(e)}")
        return build_response(500, {
            'success': False,
            'message': f"Internal server error: {str(e)}"
        })

# ─────────────────────────────────────────────
# HANDLER: Delete Student (DELETE)
# ─────────────────────────────────────────────
def delete_student(student_id):
    """Delete a student profile from DynamoDB by student_id."""
    try:
        if not student_id:
            return build_response(400, {
                'success': False,
                'message': "Missing student_id for deletion"
            })

        table.delete_item(Key={'student_id': student_id.strip()})
        logger.info(f"Deleted student_id: {student_id}")

        return build_response(200, {
            'success': True,
            'message': f"Student '{student_id}' deleted successfully"
        })

    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        return build_response(500, {
            'success': False,
            'message': f"Internal server error: {str(e)}"
        })

# ─────────────────────────────────────────────
# MAIN LAMBDA HANDLER
# ─────────────────────────────────────────────
def lambda_handler(event, context):
    """
    Main entry point. Routes requests based on HTTP method.
    POST    → save_student()
    GET     → get_student() OR get_all_students() (admin)
    DELETE  → delete_student()
    OPTIONS → CORS preflight response
    """
    logger.info(f"Received event: {json.dumps(event)}")

    http_method = event.get('httpMethod', '')
    query_params = event.get('queryStringParameters') or {}

    # ── OPTIONS: CORS Preflight ──
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight OK'})
        }

    # ── POST: Save / Update Profile OR Delete (via _action=delete) ──
    if http_method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
        except (json.JSONDecodeError, TypeError):
            return build_response(400, {
                'success': False,
                'message': 'Invalid JSON in request body.'
            })
        # Support delete via POST for API Gateway compatibility
        if body.get('_action') == 'delete':
            return delete_student(body.get('student_id', ''))
        return save_student(body)

    # ── GET: Fetch Profile or Admin Scan ──
    if http_method == 'GET':
        # Admin scan — returns ALL students
        if query_params.get('admin') == 'true':
            return get_all_students()
        # Email-based lookup (used on login)
        if query_params.get('email'):
            return get_student_by_email(query_params.get('email', ''))
        # Normal student fetch by ID
        student_id = query_params.get('student_id', '')
        return get_student(student_id)

    # ── DELETE: Remove Student (admin) ──
    if http_method == 'DELETE':
        student_id = (
            query_params.get('student_id') or
            query_params.get('email') or ''
        )
        # Also try request body
        if not student_id:
            try:
                body = json.loads(event.get('body', '{}'))
                student_id = body.get('student_id', '') or body.get('email', '')
            except Exception:
                pass
        return delete_student(student_id)

    # ── Unsupported Method ──
    return build_response(405, {
        'success': False,
        'message': f"HTTP method '{http_method}' is not supported."
    })
