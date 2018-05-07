import boto3
import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
orderTable = dynamodb.Table('IronChefOrders')

def insertOrderIntoTable(meat_doneness, menu_item):
    now = datetime.datetime.utcnow()
    date = str(now.date())
    timestamp = str(now.time())
    try:
        response = orderTable.put_item(
           Item={
                'date' : date,
                'timestamp' : timestamp,
                'meat_doneness' : meat_doneness,
                'menu_item' : menu_item
                }
        )
    except Exception, e:
        print (e) 

def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)

    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)

def on_launch(event, context):
    return statement("Welcome to the Iron Chef", "This is the body")
    
def intent_router(event, context):
    intent = event['request']['intent']['name']

    # Custom Intents

    if intent == "PlaceOrderIntent":
        return place_order_intent(event, context)

    # Required Intents

    if intent == "AMAZON.CancelIntent":
        return cancel_intent()

    if intent == "AMAZON.HelpIntent":
        return help_intent()

    if intent == "AMAZON.StopIntent":
        return stop_intent()
        
def confirm_place_order(event, context):
    intent = event['request']['intent']
    meat_doneness = intent['slots']['meat_doneness']['value']
    menu_item = intent['slots']['menu_item']['value']
    insertOrderIntoTable(meat_doneness, menu_item)

    approximatetimetocompletion = ""

    if(meat_doneness == 'rare'):
    # Wait for the steak to cook
        approximatetimetocompletion = "8 minutes"
    elif(meat_doneness == 'medium rare'):
        approximatetimetocompletion = "15 minutes"
    elif(meat_doneness == 'medium'):
        approximatetimetocompletion = "20 minutes"
    elif(meat_doneness == 'medium well'):
        approximatetimetocompletion = "25 minutes"
    elif(meat_doneness == 'well done'):
        approximatetimetocompletion = "30 minutes"
    return statement("place_order_intent", "Ok, I will tell the iron chef to make you a " + meat_doneness + " " + menu_item + ". It will take approximately " + approximatetimetocompletion + ".")
    
def place_order_intent(event, context):
    dialog_state = event['request']['dialogState']

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        return confirm_place_order(event, context)

    else:
        return statement("place_order_intent", "No dialog")    

def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(message)
        
def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)
    
def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech

def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card        

def build_response(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response