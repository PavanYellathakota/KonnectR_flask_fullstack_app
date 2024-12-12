#app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_moment import Moment
from services import UserService, PostService, MessageService, AuthService
from admin_privileges import AdminPrivileges
from datetime import timedelta, datetime
from functools import wraps
import yaml
import os
import pymysql
import time

# Load configuration first
def load_config():
    """Load configuration from Config.yaml."""
    try:
        with open('Config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Config.yaml not found")
        raise
    except yaml.YAMLError as e:
        print(f"Error reading Config.yaml: {e}")
        raise

# Load config before initializing app
config = load_config()

# Initialize Flask app
app = Flask(__name__)
moment = Moment(app)

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_TYPE='filesystem'
)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=config['db']['host'],
        user=config['db']['user'],
        password=config['db']['passwd'],
        database=config['db']['db'],
        port=config['db']['port']
    )

# Set secret key
app.secret_key = config['app']['user_secret_key']

# Initialize services
auth_service = AuthService(config)
user_service = UserService(config)
post_service = PostService(config)
message_service = MessageService(config)
admin_privileges = AdminPrivileges()

# Decorators
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            #flash('Please login first', 'warning')
            return redirect(url_for('login'))
        if session.get('user_type') == 'Admin':
            flash('Please use admin portal', 'warning')
            return redirect(url_for('admin_login'))
        # Add debug logging
        print(f"User {session['user_id']} accessing {request.path}")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            #flash('Please login first', 'warning')
            return redirect(url_for('admin_login'))
        if session.get('user_type') != 'Admin':
            flash('Admin access required', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Session handler
@app.before_request
def before_request():
    if request.endpoint and not request.endpoint.startswith('static'):
        if request.endpoint not in ['login', 'admin_login', 'register', 'index', 'about']:
            if 'user_id' in session:
                print(f"Session user_id: {session['user_id']}, Endpoint: {request.endpoint}")
                session.modified = True
                if 'last_active' in session:
                    inactive_time = datetime.now() - datetime.fromisoformat(session['last_active'])
                    if inactive_time > timedelta(minutes=30):
                        is_admin = session.get('user_type') == 'Admin'
                        session.clear()
                        flash('Session expired due to inactivity', 'info')
                        return redirect(url_for('admin_login' if is_admin else 'login'))
                session['last_active'] = datetime.now().isoformat()
                
# Context processor
@app.context_processor
def utility_processor():
    def get_unread_count():
        try:
            if 'user_id' in session and session.get('user_type') != 'Admin':
                return message_service.get_actual_unread_count(session['user_id'])
            return 0
        except Exception as e:
            print(f"Error in utility_processor: {e}")
            return 0
    return {
        'unread_count': get_unread_count(),
        'is_admin': lambda: session.get('user_type') == 'Admin'
    }

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error), 404
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal Server Error: {error}")
    return render_template('error.html', error=error), 500

@app.route('/')
@app.route('/index')
def index():
    if 'user_id' in session:
        if session.get('user_type') == 'Admin':
            return redirect(url_for('admin_dashboard_route'))
        # Add a direct render instead of redirect to prevent potential loops
        return render_template('home.html', posts=[], unread_count=0,
                             current_sort='newer')
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        result = auth_service.register_user(request.form)
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        flash(result['message'], 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('user_type') == 'Admin':
            return redirect(url_for('admin_dashboard_route'))
        return redirect(url_for('home'))
    if request.method == 'POST':
        result = auth_service.login_user(request.form)
        if result['success']:
            session.permanent = True
            session.update(result['user_data'])
            #flash('Login successful!', 'success')
            if result['user_data'].get('user_type') == 'Admin':
                return redirect(url_for('admin_dashboard_route'))
            return redirect(url_for('home'))
        flash(result['message'], 'danger')
    return render_template('login.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        result = auth_service.reset_password(request.form)
        if result['success']:
            flash('Password reset request submitted. Check your email for further instructions.', 'success')
            time.sleep(5)  # Add a 5-second delay before redirecting
            return redirect(url_for('login'))
        flash(result['message'], 'danger')
    return render_template('forgot_password.html')

#route for forget password page for resetting password  
# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         result = auth_service.reset_password(request.form)
#         if result['success']:
#             flash('Reset code has been sent to your Email', 'success')
#             return redirect(url_for('login'))
#         flash(result['message'], 'danger')
#     return render_template('forgot_password.html')

# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         result = auth_service.reset_password(request.form)
#         if result['success']:
#             flash('Password reset request submitted. Check your email for further instructions.', 'success')
#             return redirect(url_for('login'))
#         flash(result['message'], 'danger')
#     return render_template('forgot_password.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session:
        if session.get('user_type') == 'Admin':
            return redirect(url_for('admin_dashboard_route'))
        return redirect(url_for('home'))
    if request.method == 'POST':
        result = auth_service.login_user({
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'required_type': 'Admin'
        })
        if result['success']:
            session.permanent = True
            session.update(result['user_data'])
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard_route'))
        flash(result['message'], 'danger')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        was_admin = session.get('user_type') == 'Admin'
        auth_service.handle_logout(session['user_id'])
        session.clear()
        #flash('You have been logged out successfully', 'info')
        return redirect(url_for('admin_login' if was_admin else 'login'))
    return redirect(url_for('login'))

@app.route('/home')
@user_required
def home():
    try:
        posts, unread_count = post_service.get_home_feed(session['user_id'], request.args)
        return render_template('home.html', posts=posts, unread_count=unread_count,
                             current_sort=request.args.get('sort', 'newer'))
    except Exception as e:
        #print(f"Error in home route: {e}")
        #flash('Error loading posts', 'danger')
        # Change this line to prevent redirect loop
        return render_template('home.html', posts=[], unread_count=0,
                             current_sort=request.args.get('sort', 'newer'))

@app.route('/profile', methods=['GET', 'POST'])
@user_required
def profile():
    if request.method == 'POST':
        result = user_service.update_profile(session['user_id'], request.form)
        if result['success']:
            session.update(result['user_data'])
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        flash(result['message'], 'danger')     
    user_data = user_service.get_profile_data(session['user_id'])
    return render_template('profile.html', **user_data)

#route for the messages page
@app.route('/messages')
@user_required
def messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        # Mark all messages as read when viewing messages page
        message_service.mark_messages_as_read(session['user_id'])
        result = message_service.get_conversations(session['user_id'])
        return render_template('messages.html', **result)
    except Exception as e:
        print(f"Error in messages route: {e}")
        flash('Error loading messages', 'danger')
        return redirect(url_for('home'))

#route for user user conversations exchange page   
@app.route('/check_messages/<username>')
@user_required
def check_messages(username):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401  
    since = request.args.get('since')
    try:
        result = message_service.get_new_messages(session['user_id'], username, since)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

#route for Chat box/inbox page
@app.route('/chat/<username>')
@user_required
def chat(username):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        chat_data = message_service.get_chat_data_by_username(session['user_id'], username)
        if not chat_data['success']:
            flash(chat_data['message'], 'danger')
            return redirect(url_for('messages'))    
        # Mark messages from this user as read
        if chat_data['chat_user']:
            message_service.mark_messages_as_read(
                session['user_id'], 
                chat_data['chat_user']['user_id']
            )    
        return render_template('chat.html', **chat_data)
    except Exception as e:
        #flash('Error loading chat', 'danger')
        return redirect(url_for('messages'))

#route for sending messages
@app.route('/send_message', methods=['POST'])
@user_required
def send_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    return message_service.send_message_by_username(session['user_id'], request.json)

#route for sending messages by username
@app.route('/send_message_by_username', methods=['POST'])
@user_required
def send_message_by_username():
    try:
        data = request.json
        sender_id = data.get('sender_id') or session.get('user_id')
        message_data = {
            'message': data.get('message'),
            'receiver_username': data.get('receiver_username')
        }
        # Call message_service to handle sending message by username
        result = message_service.send_message_by_username(sender_id, message_data)
        if result['success']:
            return jsonify({'status': 'success', 'message': 'Message sent successfully!', 'data': result['data']}), 200
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

#route for delete messages
@app.route('/delete_message/<int:message_id>', methods=['POST'])
@user_required
def delete_message(message_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    return message_service.delete_message(message_id, session['user_id'])

#route for pinned messages
@app.route('/pin_message/<int:message_id>', methods=['POST'])
@user_required
def pin_message(message_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    return message_service.pin_message(message_id, session['user_id'])

#route for getting unread messages count
@app.route('/get_unread_count')
@user_required
def get_unread_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    try:
        count = message_service.get_actual_unread_count(session['user_id'])
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return jsonify({'count': 0})

#route for marking messages as read
@app.route('/mark_messages_read', methods=['POST'])
@user_required
def mark_messages_read():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    try:
        # Optional: specific user's messages to mark as read
        other_user_id = request.json.get('user_id')
        success = message_service.mark_messages_as_read(session['user_id'], other_user_id)
        return jsonify({'success': success})
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

#route for user user conversation delete page
@app.route('/delete_conversation/<int:conversation_id>', methods=['POST'])
@user_required
def delete_conversation(conversation_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401  
    try:
        result = message_service.delete_conversation(session['user_id'], conversation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/create_post', methods=['GET', 'POST'])
@user_required
def create_post():
    try:
        if request.method == 'POST':
            if not all(field in request.form for field in ['title', 'description', 'post_type', 'field_of_interest']):
                flash('Please fill all required fields', 'danger')
                return render_template('create_post.html')
            result = post_service.create_post(session['user_id'], request.form)
            if result['success']:
                flash('Post created successfully!', 'success')
                return redirect(url_for('home'))
            flash(result['message'], 'danger')
            return render_template('create_post.html', form_data=request.form)
        return render_template('create_post.html')
    except Exception as e:
        print(f"Error creating post: {e}")
        flash('Error creating post', 'danger')
        return redirect(url_for('home'))

@app.route('/my_posts')
@user_required
def my_posts():
    try:
        result = post_service.get_user_posts(session['user_id'])
        if not result['success']:
            flash(result['message'], 'danger')
            return render_template('my_posts.html', posts=[])
        return render_template('my_posts.html', posts=result['posts'])
    except Exception as e:
        #print(f"Error loading posts: {e}")
        #flash('Error loading posts', 'danger')
        return render_template('my_posts.html', posts=[])


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@user_required
def edit_post(post_id):
    try:
        if request.method == 'POST':
            result = post_service.update_post(post_id, session['user_id'], request.form)
            if result['success']:
                flash('Post updated successfully', 'success')
                return redirect(url_for('my_posts'))
            flash(result['message'], 'danger')
            return render_template('edit_post.html', post=request.form)
        # GET request
        result = post_service.get_post_for_edit(post_id, session['user_id'])
        if not result['success']:
            flash(result['message'], 'danger')
            return redirect(url_for('my_posts'))
        return render_template('edit_post.html', post=result['post'])
    except Exception as e:
        print(f"Error editing post: {e}")
        flash('Error editing post', 'danger')
        return redirect(url_for('my_posts'))

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@user_required
def delete_post(post_id):
    try:
        result = post_service.delete_post(post_id, session['user_id'])
        if result['success']:
            flash('Post deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'Post deleted successfully'})
        return jsonify({'success': False, 'message': result['message']})
    except Exception as e:
        print(f"Error deleting post: {e}")
        return jsonify({'success': False, 'message': 'Error deleting post'})

@app.route('/toggle_post_status/<int:post_id>', methods=['POST'])
@user_required
def toggle_post_status(post_id):
    try:
        new_status = request.json.get('status')
        result = post_service.toggle_post_status(post_id, session['user_id'], new_status)
        if result['success']:
            return jsonify({'success': True, 'message': 'Post status updated successfully'})
        return jsonify({'success': False, 'message': result['message']})
    except Exception as e:
        print(f"Error updating post status: {e}")
        return jsonify({'success': False, 'message': 'Error updating post status'})

#route for viewing posts
@app.route('/view_post/<int:post_id>')
@user_required
def view_post(post_id):
    post_service.track_interaction(session['user_id'], post_id, 'view')    
    if 'user_id' not in session:
        return redirect(url_for('login'))   
    post_data = post_service.get_post(post_id)
    if not post_data['success']:
        flash(post_data['message'], 'danger')
        return redirect(url_for('home'))
    return render_template('view_post.html', **post_data)

#route for joining/applying to posted opportunities
@app.route('/apply/<int:post_id>', methods=['POST'])
@app.route('/join/<int:post_id>', methods=['POST'])
@user_required
def apply_post(post_id):
    post_service.track_interaction(session['user_id'], post_id, 'apply')
    if 'user_id' not in session:
        return {'success': False, 'message': 'Please login first'}, 401
    return post_service.handle_application(session['user_id'], post_id)

# In app.py, add this new route:

@app.route('/track_interaction/<int:post_id>/<interaction_type>', methods=['POST'])
@user_required
def track_interaction(post_id, interaction_type):
    if interaction_type not in ['view', 'apply', 'save']:
        return jsonify({'success': False, 'message': 'Invalid interaction type'}), 400
    
    try:
        success = post_service.track_interaction(
            session['user_id'],
            post_id,
            interaction_type
        )
        return jsonify({'success': success})
    except Exception as e:
        print(f"Error tracking interaction: {e}")
        return jsonify({'success': False, 'message': 'Error tracking interaction'}), 500

#route for saving posts
@app.route('/toggle_save/<int:post_id>', methods=['POST'])
@user_required
def toggle_save_post(post_id):
    post_service.track_interaction(session['user_id'], post_id, 'save')
    if 'user_id' not in session:
        return {'success': False, 'message': 'Please login first'}, 401
    return post_service.toggle_save(session['user_id'], post_id)

#route for opening saved posts
@app.route('/saved_posts')
@user_required
def saved_posts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        posts = post_service.get_saved_posts(session['user_id'])
        return render_template('saved_posts.html', posts=posts)
    except Exception as e:
        #print(f"Error in saved_posts route: {e}") # Debug print
        flash('Error loading saved posts', 'danger')
        return redirect(url_for('home'))

#route for displaying users connections or peers
@app.route('/peers')
@user_required
def peers():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        # Validate per_page values
        if per_page not in [10, 25, 30]:
            per_page = 12
        # Get filter parameters
        filters = {
            'search_query': request.args.get('search_query', ''),
            'user_type': request.args.getlist('user_type'),
            'org_id': request.args.get('org_id'),
            'sort_by': request.args.get('sort_by', 'username'),
            'page': page,
            'per_page': per_page
        }
        # Get peers data
        result = user_service.get_peers(session['user_id'], filters)
        if not result['success']:
            raise ValueError(result['message'])
        return render_template(
            'peers.html',
            peers=result['peers'],
            organizations=result['organizations'],
            total_results=result['total_results'],
            filters=filters,
            pagination=result['pagination']
        )
    except Exception as e:
        print(f"Error in peers route: {str(e)}")
        if not request.args.get('_'):
            pass# Only show flash for non-AJAX requests
            #flash('Error loading peers', 'danger')
        return render_template(
            'peers.html',
            peers=[],
            organizations=[],
            total_results=0,
            filters=filters if 'filters' in locals() else {},
            pagination={'page': 1, 'pages': 1, 'per_page': 12}
        )

#route for following users
@app.route('/toggle_follow/<int:user_id>', methods=['POST'])
@user_required
def toggle_follow(user_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Cannot follow yourself'}), 400
    try:
        result = user_service.toggle_follow(session['user_id'], user_id)
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    except Exception as e:
        #print(f"Error in toggle_follow route: {e}") # Debug print
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

#route for searching peers of choice
@app.route('/peers/search')
@user_required
def search_peers():
    """API endpoint for typeahead search suggestions"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401   
    query = request.args.get('q', '').strip()
    try:
        results = user_service.search_peers(session['user_id'], query)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        #print(f"Error in search_peers: {e}") #Debug print
        return jsonify({'success': False, 'message': 'Error searching peers'}), 500

@app.route('/opportunities')
@user_required
def opportunities():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        if per_page not in [10, 25, 50]:
            per_page = 10
        # Get posts with pagination
        posts, total_posts = post_service.get_paginated_posts(
            session['user_id'], 
            page, 
            per_page,
            request.args
        )
        # Calculate pagination URLs based on current page
        next_url = url_for('opportunities', 
                          page=page + 1, 
                          per_page=per_page) if len(posts) == per_page else None
        prev_url = url_for('opportunities', 
                          page=page - 1, 
                          per_page=per_page) if page > 1 else None
        return render_template('opportunities.html',
                             posts=posts,
                             posts_per_page=per_page,
                             next_page_url=next_url,
                             prev_page_url=prev_url)
    except Exception as e:
        print(f"Error in opportunities route: {e}")
        flash('Error loading opportunities', 'danger')
        return render_template('opportunities.html', 
                             posts=[], 
                             posts_per_page=10,
                             next_page_url=None,
                             prev_page_url=None)

# route for viewing user profile
@app.route('/user/<username>')
@user_required
def user_profile(username):
    try:
        # Get user profile data
        result = user_service.get_user_profile(username, session['user_id'])
        if not result['success']:
            flash(result['message'], 'danger')
            return redirect(url_for('peers'))
        # Get user's posts if any
        posts = post_service.get_user_posts(result['user']['user_id'])
        return render_template('user_profile.html', 
                             user=result['user'],
                             stats=result['stats'],
                             is_following=result['is_following'],
                             posts=posts.get('posts', []))
    except Exception as e:
        print(f"Error loading user profile: {e}")
        flash('Error loading profile', 'danger')
        return redirect(url_for('peers'))

#route for deleting user account
@app.route('/delete_account', methods=['POST'])
@user_required
def delete_account():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Please login first'}, 401
    result = user_service.delete_account(session['user_id'])
    if result['success']:
        session.clear()
    return result

# Admin routes in app.py
@app.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard_route():
    try:
        stats = admin_privileges.get_dashboard_stats() or {
            'total_users': 0, 'new_users': 0, 'active_users': 0,
            'total_posts': 0, 'recent_users': [], 'recent_posts': []
        }
        return render_template('admin_dashboard.html', 
                             stats=stats,
                             recent_users=stats.get('recent_users', []),
                             recent_posts=stats.get('recent_posts', []))
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        flash('Error loading dashboard data', 'danger')
        return redirect(url_for('admin_login'))

# # Route to display password reset requests
@app.route('/admin/password-requests/<int:request_id>/<action>', methods=['POST'])
@admin_required
def handle_password_request(request_id, action):
    if action not in ['approve', 'reject']:
        return jsonify({
            'success': False,
            'message': 'Invalid action'
        }), 400
    
    result = admin_privileges.handle_password_request(request_id, action)
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/admin/password_change_requests', methods=['GET'])
@admin_required 
def password_requests_route():
    requests = admin_privileges.get_password_reset_requests()
    if isinstance(requests, dict) and not requests.get('success', True):
        flash('Error loading password requests', 'danger')
        requests = []
    return render_template('password_requests.html', requests=requests)


# Route for managing users
@app.route('/admin/users', methods=['GET'])
@admin_required
def manage_users_route():
    users = admin_privileges.get_all_users()
    return render_template('user_manage.html', users=users)

# Route for getting user
@app.route('/admin/user/<int:user_id>')
@admin_required
def get_user_route(user_id):
    user = admin_privileges.get_user(user_id)
    if user:
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'message': 'User not found'}), 404

# Route for updating user
@app.route('/admin/user/<int:user_id>/update', methods=['POST'])
@admin_required
def update_user_route(user_id):
    data = request.json
    if admin_privileges.update_user(user_id, data):
        return jsonify({'success': True, 'message': 'User updated successfully'})
    return jsonify({'success': False, 'message': 'Error updating user'}), 500

# Route for toggling user status
@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status_route(user_id):
    if admin_privileges.toggle_user_status(user_id):
        return jsonify({'success': True, 'message': 'User status updated'})
    return jsonify({'success': False, 'message': 'Error updating user status'}), 500

# Route for managing posts
@app.route('/admin/posts', methods=['GET'])
@admin_required
def manage_posts_route():
    posts = admin_privileges.get_all_posts()
    return render_template('posts_manage.html', posts=posts)

# Route for toggling post status
@app.route('/admin/post/<int:post_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_post_status_route(post_id):
    if admin_privileges.toggle_post_status(post_id):
        return jsonify({'success': True, 'message': 'Post status updated'})
    return jsonify({'success': False, 'message': 'Error updating post status'}), 500

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    analytics = post_service.get_admin_analytics()
    return render_template('admin_analytics.html', analytics=analytics)

@app.route('/api/analytics/field-stats')
@admin_required
def get_field_stats():
    analytics_result = admin_privileges.get_field_analytics()
    interaction_stats_result = admin_privileges.get_field_interaction_stats()
    result = {
        "analytics": analytics_result,
        "interaction_stats": interaction_stats_result
    }
    return jsonify(result)

@app.route('/api/analytics/post-type-stats')
@admin_required
def get_post_type_stats():
    result = admin_privileges.get_post_type_analytics()
    return jsonify(result)

@app.route('/api/analytics/growth-stats')
@admin_required
def get_growth_stats():
    result = admin_privileges.get_growth_analytics()
    return jsonify(result)

@app.route('/api/analytics/user-activity')
@admin_required
def get_user_activity():
    period = request.args.get('period', 'daily')
    result = admin_privileges.get_user_activity_analytics(period)
    return jsonify(result)

@app.route('/api/analytics/user-stats')
@admin_required
def get_user_stats():
    result = admin_privileges.get_user_type_analytics()
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
