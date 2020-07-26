from flask import Flask
from flask import request, jsonify

# Elastic Beanstalk looks for an 'application' that is callable by default
app = Flask(__name__)

# Add a rule for the index page
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    content = request.json
    print(content['mytext'])
    return jsonify({"uuid":uuid})


# Run the application
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    app.debug = True
    app.run(host="0.0.0.0")
