import boto3
from boto3.dynamodb.conditions import Key, Attr

client = boto3.client('dynamodb')

ddb = boto3.resource('dynamodb', aws_access_key_id='', aws_secret_access_key='')
#ddb = boto3.resource('dynamodb')

loc_table = ddb.Table('locations')
people_table = ddb.Table('people')

def setLocation(city):
	loc_table.update_item(Key={'location':'current'}, UpdateExpression='SET city = :val1', ExpressionAttributeValues={':val1': city})

def getLocation():
	return loc_table.get_item(Key={'location':'current'})['Item']['city']

def getPerson(name):
	person = people_table.query(KeyConditionExpression=Key('person').eq(name.lower()))['Items']
	if len(person) == 0: return {}
	else: return person[0]

def addAttr(name, attr, toAdd):
	name = name.lower()
	person = getPerson(name)
	if not attr in person:
		people_table.update_item(Key={'person':name}, UpdateExpression='SET #ri = :vals', ExpressionAttributeValues={':vals': [toAdd]}, ExpressionAttributeNames={'#ri': attr})
	else:
		people_table.update_item(Key={'person':name}, UpdateExpression='SET #ri = list_append(#ri, :vals)', ExpressionAttributeValues={':vals': [toAdd]}, ExpressionAttributeNames={'#ri': attr})

def getAttr(name, attr):
	person = getPerson(name.lower())
	if attr in person: return person[attr]
	else: return []	

def removeAttr(name, attr):
	people_table.update_item(Key={'person':name}, UpdateExpression='remove #ri', ExpressionAttributeNames={'#ri': attr})

def addLikedRestaurants(name, restaurant):
	addAttr(name.lower(), 'liked', restaurant)

def getLikedRestaurants(name):
	return getAttr(name.lower(), 'liked')

def addDislikedRestaurants(name, restaurant):
	addAttr(name.lower(), 'disliked', restaurant)

def getDislikedRestaurants(name):
	return getAttr(name.lower(), 'disliked')

def addVisitedRestaurants(name, restaurant):
	addAttr(name.lower(), 'visited', restaurant)

def getVisitedRestaurants(name):
	return getAttr(name.lower(), 'visited')

def addDietaryReq(name, req):
	addAttr(name.lower(), 'dietary_req', req)

def getDietaryReq(name):
	return getAttr(name.lower(), 'dietary_req')

def addLastRestaurant(name, restaurant):
	people_table.update_item(Key={'person':name}, UpdateExpression='SET last_restaurant = :vals', ExpressionAttributeValues={':vals': [restaurant]})

def getLastRestaurant(name, restaurant):
	return getAttr(name.lower(), 'last_restaurant')






