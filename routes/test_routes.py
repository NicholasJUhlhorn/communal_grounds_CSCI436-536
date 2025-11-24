# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint, render_template, current_app
from extensions import db
from services import user_service, project_service, reaction_service # Import your service modules
from models.user import User
from models.project import Project, ProjectMember
from models.friend import FriendRequest
from models.reaction import Reaction
from werkzeug.security import generate_password_hash

test_bp = Blueprint('test', __name__, url_prefix='/')

# List of classes we want to inspect for primary keys
SQLA_MODELS = (User, Project, ProjectMember, FriendRequest, Reaction)

def get_pk_info(result_object):
    """Helper to dynamically get primary key information (UID/PID) from a model instance."""
    if hasattr(result_object, 'uid'):
        return 'UID', getattr(result_object, 'uid')
    elif hasattr(result_object, 'pid'):
        return 'PID', getattr(result_object, 'pid')
    else:
        return 'PK', 'N/A'

def get_result_type_name(result):
    """Generates a concise name for the result type for the new column."""
    if result is None:
        return 'None'
    if isinstance(result, int):
        return 'Integer (Count)'
    if isinstance(result, list):
        if not result:
            return 'List (Empty)'
        if isinstance(result[0], SQLA_MODELS):
            # Example: List<User> (3)
            return f'List<{result[0].__class__.__name__}> ({len(result)})'
        return f'List<Other> ({len(result)})'
    if isinstance(result, SQLA_MODELS):
        return f'Model: {result.__class__.__name__}'
    return str(type(result).__name__)


def format_result_message(result):
    """Generates a useful string message based on the result type."""
    if isinstance(result, int):
        return f"Count: {result}"

    if isinstance(result, list):
        if not result:
            return "List is empty (Count: 0)"

        # Check if the list contains SQLAlchemy objects
        if isinstance(result[0], SQLA_MODELS):
            pk_name, pk_val = get_pk_info(result[0])
            first_item_class = result[0].__class__.__name__
            # Output the count and detailed info for the first item
            return f"List of {len(result)} {first_item_class} objects. Example: ({pk_name}:{pk_val}) {str(result[0])}"
        else:
            # Fallback for list of non-SQLA items (e.g., tuples from bare SQL execution)
            return f"List of {len(result)} items. Example: {str(result[0])}"

    if isinstance(result, SQLA_MODELS):
        # Detailed output for a single SQLAlchemy object
        pk_name, pk_val = get_pk_info(result)
        return f"Created/Retrieved {result.__class__.__name__}: ({pk_name}:{pk_val}) {str(result)}"

    # Explicit check for None return
    if result is None:
        return "Function returned None (Check test status for error!)"

    # Default fallback for None, strings, or other types
    return str(result) if result is not None else "Operation returned None (Success expected)"


@test_bp.route('/service_test')
def run_service_tests():
    """
    Runs a comprehensive test suite for all service methods.
    It clears the database, seeds new data, and verifies logic.
    """
    # Use Flask's context manager to ensure DB operations are valid
    with current_app.app_context():

        test_results = []

        # NOTE: We are removing 'result_type' from the dict as it's not displayed in the final HTML,
        # and instead focusing on making the 'result' field useful.
        def run_test(test_name, func, *args, **kwargs):
            """Helper function to run and record a single test."""
            try:
                result = func(*args, **kwargs)
                test_results.append({
                    'name': test_name,
                    'status': 'PASS',
                    'result': format_result_message(result), # Descriptive message
                    'result_type': get_result_type_name(result) # NEW: Concise type
                })
                return result # Must return the original result for subsequent tests
            except Exception as e:
                db.session.rollback() # Rollback transaction on failure
                # LOG THE ACTUAL ERROR MESSAGE HERE
                error_msg = str(e)
                test_results.append({
                    'name': test_name,
                    'status': 'FAIL',
                    'error': f'Function raised Exception: {error_msg}',
                    'result_type': 'Exception' # Type for failed tests
                })
                # Critical failure flag to prevent subsequent operations using a broken object
                return None

        # --- STEP 0: CLEANUP ---
        test_results.append({'name': 'SETUP: Clearing Database', 'status': 'INFO', 'result': 'Starting database cleanup.', 'result_type': 'Info'})
        try:
            db.drop_all()
            db.create_all()
            test_results.append({'name': 'SETUP: DB Reset', 'status': 'PASS', 'result': 'Database schema created successfully.', 'result_type': 'Info'})
        except Exception as e:
            test_results.append({'name': 'SETUP: DB Reset', 'status': 'FATAL ERROR', 'error': str(e), 'result_type': 'Exception'})
            return render_results(test_results)

        # --- STEP 1: USER AND PROJECT CREATION ---
        test_results.append({'name': 'SECTION: User and Project CRUD', 'status': 'HEADER', 'result': 'Testing basic User and Project creation.', 'result_type': 'Header'})

        # 1. Create Users
        # u1, u2, u3 will be None if the function call in run_test failed (i.e. raised an exception)
        alice_pw = "alice_password"
        u1 = run_test('User: Create User (Alice)', user_service.create_new_user,
                      email='alice@test.com', username='Alice', password_hash=generate_password_hash(alice_pw))
        bob_pw = "bob_password"
        u2 = run_test('User: Create User (Bob)', user_service.create_new_user,
                      email='bob@test.com', username='Bob', password_hash=generate_password_hash(bob_pw))
        charlie_pw = "charlie_password"
        u3 = run_test('User: Create User (Charlie)', user_service.create_new_user,
                      email='charlie@test.com', username='Charlie', password_hash=generate_password_hash(charlie_pw))

        # --- CRITICAL CHECK: Fetch the users independently to get IDs/confirm commit status ---
        # The subsequent service functions rely on these UIDs, so we must be able to fetch them.
        alice = User.query.filter_by(username='Alice').first()
        bob = User.query.filter_by(username='Bob').first()
        charlie = User.query.filter_by(username='Charlie').first()

        if not all([alice, bob, charlie]):
            test_results.append({
                'name': 'SETUP: Critical User Fetch/UID Check',
                'status': 'FATAL ERROR',
                'error': f'Could not retrieve all test users after creation. Alice:{alice is not None}, Bob:{bob is not None}, Charlie:{charlie is not None}. Stopping. (Check creation step above for FAIL status and error message)',
                'result_type': 'Failure Check'
            })
            return render_results(test_results)

        # Optional: Add an explicit check that the objects have a UID now that they are fetched
        run_test('CHECK: Alice UID is available', lambda: alice.uid)
        run_test('CHECK: Bob UID is available', lambda: bob.uid)


        # 2. Create Projects
        p1_result = run_test('Project: Create Project (Alice\'s)', project_service.create_new_project,
                      owner_uid=alice.uid, name='Alice\'s Public Project', description='Public Project')
        p2_result = run_test('Project: Create Project (Bob\'s)', project_service.create_new_project,
                      owner_uid=bob.uid, name='Bob\'s Draft Project', description='Draft Project')

        alice_project = Project.query.filter_by(owner_uid=alice.uid).first()

        # 3. Read Operations
        run_test('User: Get All Users (Count 3)', lambda: user_service.get_all_users())
        run_test('Project: Get Project Details (Alice\'s)', project_service.get_project_details, alice_project.pid)

        # --- STEP 2: MEMBERSHIP AND RELATIONSHIP TESTS ---
        test_results.append({'name': 'SECTION: Project Membership Tests', 'status': 'HEADER', 'result': 'Testing ProjectMember creation and eager loading.', 'result_type': 'Header'})

        # 4. Add Member
        run_test('Member: Bob joins Alice\'s Project (EDITOR)', project_service.add_project_member,
                 pid=alice_project.pid, uid=bob.uid, role='EDITOR')

        # 5. Check Eager Load
        p_data = project_service.get_project_with_related_data(alice_project.pid)
        print(p_data.members, flush=True)
        member_count = len(p_data.members) if p_data else 0

        # Custom verification step
        if p_data and hasattr(p_data, 'members') and member_count == 2:
             test_results.append({'name': 'VERIFY: Member count after join (Alice & Bob)', 'status': 'PASS', 'result': f"Eager loading successful. Found {member_count} members (Owner + Bob).", 'result_type': 'Verification'})
        else:
             test_results.append({'name': 'VERIFY: Member count after join (Alice & Bob)', 'status': 'FAIL', 'error': f'Expected 2 members, found {member_count}.', 'result_type': 'Verification'})


        # --- STEP 3: REACTION TESTS ---
        test_results.append({'name': 'SECTION: Reaction Counting Tests', 'status': 'HEADER', 'result': 'Testing Reaction CRUD and aggregation functions.', 'result_type': 'Header'})

        # 6. Add Reactions
        run_test('Reaction: Alice UPVOTES P1', reaction_service.add_reaction, alice_project.pid, alice.uid, 'UPVOTE')
        run_test('Reaction: Bob UPVOTES P1', reaction_service.add_reaction, alice_project.pid, bob.uid, 'UPVOTE')
        run_test('Reaction: Charlie LIKES P1', reaction_service.add_reaction, alice_project.pid, charlie.uid, 'LIKE')

        # 7. Count Reactions
        run_test('Reaction: Count UPVOTES (Expected 2)', reaction_service.get_reaction_count_by_type, alice_project.pid, 'UPVOTE')
        run_test('Reaction: Count Total Reactions (Expected 3)', reaction_service.get_total_reactions, alice_project.pid)

        # 8. Update Reaction
        run_test('Reaction: Alice changes UPVOTE -> LIKE', reaction_service.add_reaction, alice_project.pid, alice.uid, 'LIKE')

        # 9. Verify updated counts (Expected UPVOTES: 1, LIKES: 2, Total: 3)
        run_test('Reaction: Count UPVOTES (Expected 1)', reaction_service.get_reaction_count_by_type, alice_project.pid, 'UPVOTE')
        run_test('Reaction: Count LIKES (Expected 2)', reaction_service.get_reaction_count_by_type, alice_project.pid, 'LIKE')


        # --- STEP 4: FRIENDSHIP TESTS ---
        test_results.append({'name': 'SECTION: Friendship Logic Tests', 'status': 'HEADER', 'result': 'Testing FriendRequest lifecycle and friend list retrieval.', 'result_type': 'Header'})

        # 10. Send Request (Alice -> Bob)
        run_test('Friend: Alice sends Bob request', user_service.send_friend_request, alice.uid, bob.uid)

        # 11. Accept Request (Bob -> Alice)
        run_test('Friend: Bob accepts request', user_service.accept_friend_request, alice.uid, bob.uid)

        # 12. Get Friends List
        friends = user_service.get_friends_list(alice.uid)
        friend_test_result = format_result_message(friends)

        if friends and len(friends) == 1 and friends[0].username == 'Bob':
            test_results.append({'name': 'VERIFY: Alice has Bob as friend', 'status': 'PASS', 'result': f"Friendship verified. {friend_test_result}", 'result_type': 'Verification'})
        else:
             test_results.append({'name': 'VERIFY: Alice has Bob as friend', 'status': 'FAIL', 'error': f'Friends list incorrect. Found: {friend_test_result}', 'result_type': 'Verification'})

    # Render results to the user
    return render_results(test_results)

def render_results(results):
    """Renders the test results in a simple HTML table."""
    html = """
    <html>
    <head>
        <title>Service Test Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #6a0dad; color: white; }
            .PASS { background-color: #d4edda; color: #155724; font-weight: bold; }
            .FAIL { background-color: #f8d7da; color: #721c24; font-weight: bold; }
            .INFO { background-color: #cce5ff; color: #004085; }
            .HEADER { background-color: #e0e0e0; color: #333; font-weight: bold; }
            .FATAL { background-color: #ffcccc; color: #cc0000; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Service Test Report</h1>
        <p>This report validates the Model Layer and Service Layer functionality by performing CRUD and business logic tests.</p>
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Result Type</th>
                    <th>Result / Error</th>
                </tr>
            </thead>
            <tbody>
    """

    for result in results:
        status_class = result.get('status')
        name = result.get('name', 'N/A')
        # Use 'result' for PASS/INFO/HEADER, and 'error' for FAIL/FATAL
        message = result.get('result', result.get('error', 'No message'))
        result_type = result.get('result_type', '') # Fetch the new type

        html += f"""
        <tr>
            <td>{name}</td>
            <td class="{status_class}">{status_class}</td>
            <td>{result_type}</td>
            <td>{message}</td>
        </tr>
        """

    html += """
            </tbody>
        </table>
        <p>Note: A FATAL ERROR means the database setup failed and subsequent tests could not run.</p>
    </body>
    </html>
    """
    return html
