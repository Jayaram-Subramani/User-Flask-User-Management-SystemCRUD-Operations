from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_marshmallow import Marshmallow
import uuid
import secrets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'Email'
app.config['MAIL_PASSWORD'] = 'Password'

db = SQLAlchemy(app)
mail = Mail(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    phonenumber = db.Column(db.String(20))
    country = db.Column(db.String(20))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
with app.app_context():
    db.create_all()

class userSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'phonenumber', 'country', 'email')

user_schema = userSchema()
users_schema = userSchema(many=True)

def send_verification_email(user):
    token = str(uuid.uuid4())  
    user.reset_token = token
    db.session.commit()

    msg = Message('Email Verification',
                  sender='ramjaya852@gmail.com',
                  recipients=[user.email])
    verification_link = f"http://127.0.0.1:5000/verify_email?token={token}"
    msg.body = f"Hello {user.firstname},\n\nPlease click the following link to verify your email address:\n\n{verification_link}"

    mail.send(msg)

def send_password_reset_email(user):
    token = str(uuid.uuid4())  
    user.reset_token = token
    db.session.commit()

    msg = Message('Password Reset',
                  sender='ramjaya852@gmail.com',
                  recipients=[user.email])
    reset_link = f"http://127.0.0.1:5000/reset_password?token={token}"
    msg.body = f"Hello {user.firstname},\n\nPlease click the following link to reset your password:\n\n{reset_link}"

    mail.send(msg)

@app.route('/home')
def home():
    return jsonify({'message':'Welcome to home page'})

@app.route('/register', methods=['POST'])
def register():
    try:
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        phonenumber = request.json.get('phonenumber')
        country = request.json.get('country')
        email = request.json.get('email')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')

        if not firstname or not lastname or not phonenumber or not country or not email or not password or not confirm_password:
            return jsonify({'error': 'Missing Fields'})

        if password != confirm_password:
            return jsonify({'error': 'Passwords Do Not Match'})

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User Already Exists'})

        new_user = User(firstname=firstname, lastname=lastname, phonenumber=phonenumber, country=country, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        send_verification_email(new_user)

        return jsonify({'message': 'An email has been sent with instructions to verify your email address.'})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/verify_email', methods=['GET'])
def verify_email():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Token is missing in the URL'})

        user = User.query.filter_by(reset_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid token'})
        
        user.email_verified = True
        user.reset_token = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully. You can now complete the registration.'})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user or user.password != password or user.email_verified = False:
            return jsonify({'error': 'Invalid Email or Password'})
        
        else:
            return jsonify({'message': 'Login Successfully'})
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/logout')
def logout():
    return jsonify({'message': 'Logout Successfully'})

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        email = request.json.get('email')
        current_password = request.json.get('current_password')
        new_password = request.json.get('new_password')
        confirm_new_password = request.json.get('confirm_new_password')

        if not email or not current_password or not new_password or not confirm_new_password:
            return jsonify({'error': 'Missing Fields'})

        user = User.query.filter_by(email=email).first()
        if not user or user.password != current_password:
            return jsonify({'error': 'Email or Password Does Not Match'})

        if new_password != confirm_new_password:
            return jsonify({'error': 'New Passwords Do Not Match'})

        user.password = new_password
        db.session.commit()
        
        return jsonify({'message': 'Password Changed Successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/user', methods=['GET'])
def getall():
    try:
        users = User.query.all()
        result = users_schema.dump(users)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/user/<int:id>', methods=['GET'])
def get_user_by_id(id):
    try:
        user = User.query.get(id)

        if user:
            return user_schema.jsonify(user)
        else:
            return jsonify({"message": "User not found"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User Not Found'})

        
        firstname = request.json.get('firstname', None)
        lastname = request.json.get('lastname', None)
        phonenumber = request.json.get('phonenumber', None)
        country = request.json.get('country', None)
        email = request.json.get('email', None)

        
        if firstname is not None:
            user.firstname = firstname
        if lastname is not None:
            user.lastname = lastname
        if phonenumber is not None:
            user.phonenumber = phonenumber
        if country is not None:
            user.country = country
        if email is not None:
            user.email = email

        db.session.commit()
        return jsonify({'message': 'User data has been updated successfully.'})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        email = request.json.get('email')
        
        if not email:
            return jsonify({'error': 'Missing Email Field'})

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User Not Found'})

        send_password_reset_email(user)
        
        return jsonify({'message': 'An email has been sent with instructions to reset your password.'})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    try:
        if request.method == 'GET':
            token = request.args.get('token')
            return jsonify({'message': f'This is the password reset page. Token: {token}'})
        
        if request.method == 'POST':
            token = request.json.get('token')
            new_password = request.json.get('new_password')

            if not token or not new_password:
                return jsonify({'error': 'Token or New password is missing'})

            user = User.query.filter_by(reset_token=token).first() 
            user.password = new_password
            user.reset_token = None
            db.session.commit()
            return jsonify({'message': 'Password has been reset successfully.'})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/admin/change_user_data', methods=['PUT'])
def change_user_data():
    try:
        admin_key = request.json.get('admin_key')
        if not admin_key or not admin_key == app.config['ADMIN_KEY']:
            return jsonify({'error': 'Unauthorized'})

        user_id = request.json.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User Not Found'})
        firstname = request.json.get('firstname', None)
        lastname = request.json.get('lastname', None)
        phonenumber = request.json.get('phonenumber', None)
        country = request.json.get('country', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        
        if firstname is not None:
            user.firstname = firstname
        if lastname is not None:
            user.lastname = lastname
        if phonenumber is not None:
            user.phonenumber = phonenumber
        if country is not None:
            user.country = country
        if email is not None:
            user.email = email
        if password is not None:
            user.password = password

        db.session.commit()
        return jsonify({'message': 'User data has been updated successfully.'})

        

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.get(id)

        if not user:
            return jsonify({"message": "User not found!"})
            

        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.config['ADMIN_KEY'] = secrets.token_urlsafe(16)
    print("Admin Key:", app.config['ADMIN_KEY'])
    app.run(debug=True)
