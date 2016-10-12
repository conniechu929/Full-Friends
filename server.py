from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'SecretKey'
mysql = MySQLConnector(app, 'friends')

@app.route('/', methods=['POST','GET'])
def index():
	query = "SELECT * FROM friends"
	friends = mysql.query_db(query)
	return render_template('index.html', all_friends=friends)

@app.route('/friends', methods=['POST'])
def created():

	count = 0
	if len(request.form['email']) < 1:
		flash('Email cannot be blank')
		count += 1
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Email is not valid!")
		count += 1
	if len(request.form['first_name'])<1:
		flash("First Name cannot be blank!")
		count+=1
	elif not NAME_REGEX.match(request.form['first_name']):
		flash("First Name cannot contain characters!")
		count+=1
	if len(request.form['last_name'])<1:
		flash("Last Name cannot be blank!")
		count+=1
	elif not NAME_REGEX.match(request.form['last_name']):
		flash("Last Name cannot contain characters!")
		count+=1
	if count > 0:
		return redirect('/')

	query = "INSERT INTO friends (first_name, last_name, email, created_at, updated_at) VALUES (:first_name, :last_name, :email, NOW(), NOW())"
	data = {
			'first_name': request.form['first_name'],
			'last_name': request.form['last_name'],
			'email': request.form['email']
			}
	mysql.query_db(query, data)
	return redirect('/')

@app.route('/friends/<friend_id>', methods=['POST'])
def update(friend_id):
	query1 = "SELECT * FROM friends WHERE id = :specific_id"
	data1 = {
		'specific_id': friend_id
	}
	original = mysql.query_db(query1, data1)
	if request.form['first_name']>0:
		fname = original[0]['first_name']
	else:
		fname = request.form['first_name']

	if request.form['last_name']>0:
		lname = original[0]['last_name']
	else:
		lname = request.form['last_name']
	if request.form['email']>0 and not EMAIL_REGEX.match(request.form['email']):
		mail = original[0]['email']

	else:
		mail = request.form['email']

	query2 = "UPDATE friends SET first_name = :first_name, last_name = :last_name, email = :email, updated_at = NOW() WHERE id = :specific_id"
	data2 = {
		'first_name': fname,
		'last_name': lname,
		'email': mail,
		'specific_id': friend_id
	}
	friends = mysql.query_db(query2, data2)
	return redirect('/')

@app.route('/friend/<friend_id>/edit')
def edit(friend_id):
	data = {'specific_id': friend_id}
	query = "SELECT * FROM friends WHERE id = :specific_id"
	friends = mysql.query_db(query, data)
	return render_template('edit.html', all_friends=friends)

@app.route('/friends/<friend_id>/delete', methods=['POST'])
def delete(friend_id):
	query="SELECT * FROM friends WHERE id=:id"
	data={'id': friend_id}
	friends=mysql.query_db(query,data)
	if request.form['delete']=='Yes':
		query = "DELETE FROM friends WHERE id = :id"
		data = {'id': int(friend_id)}
		mysql.query_db(query, data)
		return redirect('/')
	else:
		return render_template('delete.html', friend=friends[0])


app.run(debug=True)
