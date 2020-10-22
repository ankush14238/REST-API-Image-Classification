from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json


app = Flask(__name__)

api = Api(app)  #initialising new api


client = MongoClient('mongodb://db:27017')  #connect to the mongodb located at docker-compose file in db directory 

db = client.ImageRecognitionAPI

users = db['Users']


#fucntion to check if the username already exists

def UserExist(username):
	if users.find({'Username':username}).count() == 0:
		return False
	else:
		return True



#creating class for user to register

class Register(Resource):
	def post(self):
		postedData = request.get_json()


		#getting username and password from the posted data on the api
		username = postedData['Username']
		password = postedData['Password']

		#checking for the validity of the posted data
		if UserExist(username):
			retJSON = {
				'status':301,
				'msg': 'Invalid Username'
			}

			return jsonify(retJSON)



		#hashing the password for security of the user
		hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

		#storing the username and hashed password of the user in the database and assigning tokens to new registered user
		users.insert({
				'Username': username,
				'Password': hashed_pw,
				'Tokens': 10
			})

		retJSON = {
			'status':200,
			'msg':'You successfully signed up for the API'
		}
		return jsonify(retJSON)


#function to check if the password entered by a particular user is right or not

def verify_pw(username, password):
	if not UserExist(username):
		return False


	hashed_pw = users.find({
		'Username':username
		})[0]['Password']

	if bcrypt.hashpw(password.encode('utf8'), hashed_pw)==hashed_pw:
		return True
	else:
		return False

#this is the JSON response created confirming the registration of the user
def generateReturnDictionary(status, msg):
	retJSON = {
	'status':status,
	'msg': msg
	}

	return retJSON


#this function checks and verifies the credentials of the registered user

def verifyCredentials(username, password):
	if not UserExist(username):
		return generateReturnDictionary(301, 'Invalid Username'), True


	correct_pw = verify_pw(username, password)

	if not correct_pw:
		return generateReturnDictionary(302, 'Invalid Password'), True

	return None, False



#class for classifying which will take a post request from the user and return a response of what kind of image did the user post.
class Classify(Resource):
	def post(self):
		postedData = request.get_json()


		username = postedData['Username']
		password = postedData['Password']

		url = postedData['url']


		retJSON, error = verifyCredentials(username, password)
		
		if error:
			return jsonify(retJSON)

		#checking if the user has enough tokens for sending a post request to the api.

		tokens = users.find({
				'Username':username
			})[0]['Tokens']


		if tokens <= 0:
			return jsonify(generateReturnDictionary(303, 'Not Enough Tokens!'))


		r = requests.get(url)
		retJSON = {}

		#in this loop we create a temp where we store the content of the posted url(image)
		#and create a subprocess to run the classifier for the particular image and return the results in text.txt

		with open('temp.jpg', 'wb') as f:
			f.write(r.content)
			proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True)
			proc.communicate()[0]
			proc.wait()

			with open('text.txt') as g:
				retJSON = json.load(g)


		#updating the number of tokens after the use of the api
		users.update({
			'Username':username
		}, {
			'$set':{
				'Tokens': tokens-1
			}
		})

		return retJSON



#this class is used if the user wants to refill the tokens once they are out of it.

class Refill(Resource):

	def post(self):
		postedData = request.get_json()


		username = postedData['Username']
		password = postedData['admin_pw']  #the user should know the admin password so that we know they are someone who have registered already
		amount = postedData['amount']


		if not UserExist(username):
			return jsonify(generateReturnDictionary(301, 'Invalid Username'))

		correct_pw = 'abc123'


		if not password == correct_pw:
			return jsonify( generateReturnDictionary(304, 'Invalid Admin Password'))


		users.update({
			'Username': username
		},{
			'$set':{
				'Tokens': amount
			}
		})


		return jsonify( generateReturnDictionary(200, 'Refill successfully done!'))


#adding the classes as a resource
api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/Refill')

#calling the main function

if __name__ == "__main__":
	app.run(host='0.0.0.0')





















