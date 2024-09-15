from flask import Flask, render_template, request, jsonify, session
from rasa.nlu.model import Interpreter
import json
import pymysql
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import random

# Load responses from a JSON file
with open('responses.json') as f:
    dataresp = json.load(f)

# Database connection
timeout = 10
connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="mysql-30059af1-yogyachugh-695c.b.aivencloud.com",
    password="AVNS_C23ljLnWIaThTRYI9YZ",
    read_timeout=timeout,
    port=27336,
    user="avnadmin",
    write_timeout=timeout,
)
cursor = connection.cursor()

global debugging_option
debugging_option = True

# Load Rasa NLU model
interpreter = Interpreter.load("nlu-20240916-001455//nlu")

app = Flask(__name__)
app.secret_key = 'Bro life is good'
app.permanent_session_lifetime = timedelta(days=1)

global museum_selected
museum_selected = 'marble palace'

@app.route('/')
def index():
    cursor.execute(
        "SELECT name, type, ticket_price_adult, ticket_price_child, ticket_price_foreigner_child, ticket_price_foreigner FROM city_museum"
    )
    result = cursor.fetchall()
    today = date.today()
    new_date = today + relativedelta(months=3)
    ticket_list = []
    for i in result:
        if i['name'] == museum_selected:
            ticket_list = [i['ticket_price_adult'], i['ticket_price_child'], i['ticket_price_foreigner'], i['ticket_price_foreigner_child']]
    return render_template('index.html', result=result, date1=today, date2=new_date, ticket_list=ticket_list)

@app.route('/debugger_on', methods=['GET','POST'])
def debugger_on():
    global debugging_option
    debugging_option = not debugging_option
    print(debugging_option)
    return jsonify({'response': "jingalala"})

@app.route('/selector/<string:select>', methods=['POST'])
def museum_selector(select):
    global museum_selected
    museum_selected = select.lower()
    return jsonify({'message': f'Value received: {select}'}), 200

@app.route('/ticketbook', methods=['POST'])
def ticketbook():
    # Handle the ticket booking form data
    a = request.form
    print(a)  # For debugging purposes
    return jsonify({'status': 'success'}), 200

@app.route('/chatbot',methods=['GET','POST'])
def bot_msg():
    data = request.get_json()
    msg = data.get('message')
    botresp = interpreter.parse(msg)
    bot_response, bot_function = respond(botresp)
    a = botresp.get('intent')
    print(a)
    if (not bot_function):
        bot_function = "No function assigned"
    sending_response = "<strong>Intent: </strong>" + a.get('name') + "<br>" + "<strong>Confidence: </strong>" + str(a.get('confidence')) + "<br>" + "<strong>Response: </strong>" +  bot_response + "<br>" + "<strong>Function: </strong>" + bot_function
    if debugging_option==True:
        return jsonify({'response': sending_response})
    else:
        return jsonify({'response': bot_response, 'function': bot_function})

def respond(data):
    session.permanent = True
    session['intents'] = []
    session['user_details'] = session.get('user_details', {})

    data2 = data.get('intent')
    intent = data2.get('name')

    fixed_response=["age","info_suggestions","cancel_ticket","discount","museum_membership","info_payment","age_young","age_old","bye","greet","status_owner","status_place","status_creator","status_process","status_who","sad","happy","other","abusive_language","get_joke","complement_positive","complement_negative", "info_languages"]
    if intent in dataresp and intent in fixed_response:
        session['intents'].append(intent)
        return random.choice(dataresp[intent]), None
    

    if intent=='age_user' or intent=='share_name':
        user_name = data.get('entities')
        session['intents'].append(intent)
        for i in user_name:
            if i['entity'] == 'user_name':
                session['user_details']['user_name'] = i['value']
                return dataresp.get('age_user'), None
    elif ('again' in data.get('text') or 'more' in data.get('text')) and (session['intents'][-1]=='get_joke' or session['intents'[-1]=='again']):
        session['intents'].append('again')
        return dataresp.get('get_joke'), None
    elif intent=='book_ticket':
        session['intents'].append(intent)
        return "Here you go ...","ticket_book"
    elif intent=='museum_portal':
        session['intents'].append(intent)
        return "On your command :)","museum_portal"
    elif intent=='abuse_no':
        session['intents'].append(intent)
        return "It's against our policy !", None
    elif intent=='list_policy':
        session['intents'].append(intent)
        return "👇 Here's the link to the policy","policy_button"
    elif intent=='send_mail':
        session['intents'].append(intent)
        return "📫 Mail sender on the go ...","mail_sender"
    elif intent=='send_whatsapp':
        session['intents'].append(intent)
        return "Your Whatsapp Helper is here ","send_whatsapp"
    elif intent=='send_mms':
        session['intents'].append(intent)
        return 'Messaging you as we speak ✉️',"send_mms"
    elif intent=='download_ticket':
        session['intents'].append(intent)
        return "Here's your downloader","download_ticket"
    elif intent=='info_ticket_price':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "SELECT ticket_price_adult, ticket_price_child, ticket_price_foreigner_child, ticket_price_foreigner from city_museum WHERE name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_ticket_price"
                else:
                    return f"Ticket prices:-\nAdult:- {re['ticket_price_adult']}, Children:- {re['ticket_price_child']}, Foreigner:- {re['ticket_price_foreigner']}, Foreigner Children:- {re['ticket_price_foreigner_child']}", None
        return "Sure ! Select from the museums below: ","museum_select_ticket_price"
    elif intent=='inquire_museum_hours':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select timings from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_time"
                else:
                    return f"Timings for {singer.title()} are {re.get('timings')}", None
        return "Sure ! Select from the museums below: ","museum_select_time"
    elif intent=='museum_description':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select short_description from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_desc"
                else:
                    return f"{re.get('short_description')}", None
        return "Sure ! Select from the museums below: ","museum_select_desc"
    elif intent=='museum_history':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select history from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_history"
                else:
                    return f"{re.get('history')}", None
        return "Sure ! Select from the museums below: ","museum_select_history"
    elif intent=='museum_speciality':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select speciality from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_speciality"
                else:
                    return f"{re.get('speciality')}", None
        return "Sure ! Select from the museums below: ","museum_select_speciality"
    elif intent=='museum_list_type':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='type':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select name from city_museum where type=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_list_type"
                else:
                    return f"Here are some museums related to {singer}: \n {re}",None
        return "Sure ! Select from the museums below: ","museum_select_list_type"
    elif intent=='museum_inquiry':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select description from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select"
                else:
                    return f"{re.get('description')}", None
        return "Sure ! Select from the museums below: ","museum_select"
    elif intent=='museum_shows' or intent=='museum_exhibitions':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select shows from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_shows"
                else:
                    return f"{re.get('shows')}", None
        return "Sure ! Select from the museums below: ","museum_select_shows"
    elif intent=='info_metro':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select nearest_metro_station from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_metro"
                else:
                    return f"{re.get('nearest_metro_station')}", None
        return "Sure ! Select from the museums below: ","museum_select_metro"
    elif intent=='info_food':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select food_facilities from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_food"
                else:
                    return f"{re.get('food_facilities')}", None
        return "Sure ! Select from the museums below: ","museum_select_food"
    elif intent=='info_parking':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select parking_availability from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_parking"
                else:
                    return f"{re.get('parking_availability')}", None
        return "Sure ! Select from the museums below: ","museum_select_parking"
    elif intent=='info_museum_age':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select founded from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_age"
                else:
                    return f"{re.get('founded')}", None
        return "Sure ! Select from the museums below: ","museum_select_age"
    elif intent=='info_safety':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select safety_measures from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_safety"
                else:
                    return f"{re.get('safety_measures')}", None
        return "Sure ! Select from the museums below: ","museum_select_safety"
    elif intent=='info_safety_overall':
        return "Here's our safety policy", "safety_overall"
    elif intent=='info_museum_loc':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select address from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_loc"
                else:
                    return f"{re.get('address')}", None
        return "Sure ! Select from the museums below: ","museum_select_loc"
    elif intent=='info_route_launch':
        return "Launching the google map api !!", "transport_gl_launch"
    elif intent=='info_allowance' or intent=='museum_guidelines' or intent=='info_museum_restrictions':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select disallowance from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_allowance"
                else:
                    return f"{re.get('disallowance')}", None
        return "Sure ! Select from the museums below: ","museum_select_allowance"
    elif intent=='info_museum_restroom':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select restroom from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_restroom"
                else:
                    return f"{re.get('restroom')}", None
        return "Sure ! Select from the museums below: ","museum_select_restroom"
    elif intent=='info_museum_disabled':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select disabled_facilities from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_disabled"
                else:
                    return f"{re.get('disabled_facilities')}", None
        return "Sure ! Select from the museums below: ","museum_select_disabled"
    elif intent=='info_incomplete' or intent=="info_construction":
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select construction from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_incomplete"
                else:
                    return f"{re.get('construction')}", None
        return "Sure ! Select from the museums below: ","museum_select_incomplete"
    elif intent=="feedback_form":
        return "Let's get u there !", "feedback_form"
    elif intent=="give_feedback":
        return "Thanks for your feedback! It will help us improve user experience! ✌️", "save_feedback"
    elif intent=="unhappy_result":
        return "😔 Sorry for your bad experience ! I think rephrasing might solve the issue", "report_issue"
    elif intent=="customer_support":
        return "Customer Support No. :- +91 1234567891", None
    elif intent=='info_museum_camera':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select disallowance from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_camera"
                else:
                    return f"{re.get('disallowance')[0]}", None
        return "Sure ! Select from the museums below: ","museum_select_camera"
    elif intent=='info_museum_interactive':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select facebook,twitter,instagram from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_interactive"
                else:
                    return f"I don't have information about that but u can check their info at {re.get('facebook')}", None
        return "Sure ! Select from the museums below: ","museum_select_interactive"
    elif intent=='lost_item':
        return "You can contact here:- \nCustomer Support No. :- +91 1234567891", None
    elif intent=='info_students':
        return "Yup! All museums are configured to provide some sort of knowledge 📖 or reflect Indian culture 🖼️", None
    elif intent=="special_guide":
        return "Sorry but special guides is not under my coverage ! You can contact customer support at +91 1234567891", None
    elif intent=="info_transport":
        return "I can launch google maps route for you to check how many ways you can reach your destination!", "transport_gl_launch"
    elif intent=='group_tickets':
        return "You can buy as many tickets as you want , just track your wallet 😁", None
    elif intent=="voice_input":
        return "Here you go !", "voice_input"
    elif intent=="info_special" or intent=='special_event_pass' or intent=='ticket_VIP':
        return "Sorry but there is no special service !", None
    elif intent=="info_app":
        return "We don't have a separate app on Play Store but you can install our website as a PWA (app)", "pwa"
    elif intent=='activities' or intent=='info_vr':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select facebook,twitter,instagram from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_select_activity"
                else:
                    return f"I don't have information about that but u can check their info at {re.get('facebook')}", None
        return "Sure ! Select from the museums below: ","museum_select_activity"
    elif intent=="time_specific":
        return "Move you eyeballs 👀 on the screen ! You will soon locate some numbers called time ⏳",None
    elif intent=="ticket_book_advance":
        return "You can book tickets 3 months prior to your visit !",None
    elif intent=='total_facility':
        return "You can get full information about any museum here:- ", "museum_portal_launch"
    elif intent=='info_museum_store':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select store from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_store"
                else:
                    return f"{re.get('store')}", None
        return "Sure ! Select from the museums below: ","museum_store"
    elif intent=="info_venue":
        return "Holding events at museums is strictly prohibited :)", None
    elif intent=="ticket_lost":
        return "You can login to see past bought tickets ! Or you can see log here for bought tickets !", "log"
    elif intent=="sign-info" or intent=='delete_account':
        return "Sorry! but I am not allowed to perform this !", None
    elif intent=="user_security":
        return "We implement best practices to secure your data using Blockchain and other security measures! ", None
    elif intent=="info_processing":
        return "I can't share that due to security reasons", None
    elif intent=='other_talk':
        return "You can book tickets here by just telling me to do so !", None
    elif intent=="moc_info":
        return "You can visit the official website of Ministry of Culture here:-","moc_site"
    elif intent=="home_delivery" or intent=="in_hand":
        return "It is not supported !", None
    elif intent=='peak_hour_spec':
        return "Currently that feature is still in development !", None
    elif intent=='weather_report':
        return "Currently that feature is still in development !", None
    elif intent=='info_picture_spot':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select best_spot from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_picture"
                else:
                    return f"The best picture spot goes here :- {re.get('best_spot')}", None
        return "Sure ! Select from the museums below: ","museum_picture"
    elif intent=='info_pets_allowed':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select pets from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_pets"
                else:
                    return f"{re.get('pets')}", None
        return "Sure ! Select from the museums below: ","museum_pets"
    elif intent=="ticket_types":
        return "There are 4 types of tickets:- \nAdult\nChild\nForeigner Child\nForeigner", None
    elif intent=='info_museum_layout' or intent=="info_workshop":
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select facebook,twitter,instagram from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_layout"
                else:
                    return f"I don't have information about that but u can check their info at {re.get('facebook')}", None
        return "Sure ! Select from the museums below: ","museum_layout"
    elif intent=="ticket_upgrade":
        return "Upgrading tickets isn't supported ! But you can alter ticket info here","ticket_alter_info"
    elif intent=='museum_closed':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select closed from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_closed"
                else:
                    return f"Museum is closed on {re.get('closed')}", None
        return "Sure ! Select from the museums below: ","museum_closed"
    elif intent=='special_for_kids':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select kids from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_kids"
                else:
                    return f"{re.get('kids')}", None
        return "Sure ! Select from the museums below: ","museum_kids"
    elif intent=='special_for_school':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select customer_care_no from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_school"
                else:
                    return f"I don't have information about that ! You can contact museum support at {re.get('customer_care_no')}", None
        return "Sure ! Select from the museums below: ","museum_school"
    elif intent=="info_initiatives":
        return "Sorry ! I don't have information regarding that !", None
    elif intent=='info_changes':
        return "I am not aware about any recent changes", None
    elif intent=="share_testimonals" or intent=='steps_experience':
        return "Here you go !", "share_testimonals"
    elif intent=='museum_evolve' or intent=='call_brochure' or intent=="museum_collaborate":
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select facebook,twitter,instagram from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_evolve"
                else:
                    return f"I don't have information about that but u can check their info at {re.get('facebook')}", None
        return "Sure ! Select from the museums below: ","museum_evolve"
    elif intent=='ticket_booking_steps':
        return "You can ask me to book tickets to which I will open a ticket booking UI where you can book ticket", None
    elif intent=='change_ticket_info':
        return "Here you go !","ticket_alter_info"
    elif intent=='family_friendly':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select family_friendly from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_family"
                else:
                    return f"{re.get('family_friendly')}", None
        return "Sure ! Select from the museums below: ","museum_family"
    elif intent=="solve_error":
        return "Refreshing the page might help", None
    elif intent=="gift_ticket":
        return "Just share the ticket with anyone you wanna gift and there u go 😊", None
    elif "change_account_info":
        return "You can sign in your account and visit dashboard to change account info ! I am not allowed to perform that!", None
    elif "call_roadmap":
        return "Here you go !", None
    elif "user_confused":
        return "These are the tasks I can help you with ","bot_tasks"
    elif "set_reminder":
        return "I can't set custom reminders but there is an automatic reminder set 24 hours prior to the user's visit", None
    elif "person_donate":
        return "Teleporting you to the donation center", "donate"
    elif intent=='food_facility':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select nearby_food_corners from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_food_corners"
                else:
                    return f"{re.get('nearby_food_corners')}", None
        return "Sure ! Select from the museums below: ","museum_food_corners"
    elif intent=="info_national_event":
        return "I don't have information regarding that! ", None
    elif intent=='ticket_transfer':
        return "You can just share your ticket with anyone and you are set to go :)", None
    elif intent=='social_media_share':
        ig = data.get('entities')
        for i in ig:
            if i['entity']=='museum':
                singer = i['value'].lower()
                singer = singer.strip()
                session['intents'].append(intent)
                cursor.execute(
                    "select facebook,twitter,instagram from city_museum where name=%s",
                    (singer)
                )
                re = cursor.fetchall()
                if not re:
                    return "Sorry but i couldn't fetch that data 😔 ! You should rather choose from the museums below:","museum_sm"
                else:
                    return f"{re.get('facebook')},{re.get('twitter')},{re.get('instagram')}", None
        return "Sure ! Select from the museums below: ","museum_sm"
    elif intent=='moc_social_media':
        return "Teleporting to wonders :)", "mocsm"
    elif intent=='sections_of_people':
        return "All sections of people are allowed !", None
    elif intent=='whatsapp_talk':
        return "You can say 'hi' to +91 1234567891 on Whatsapp", None
    elif intent=='mms_talk':
        return "You can say 'hi' to +91 1234567891 on MMS", None
    elif intent=='tech_used':
        return "We used Rasa Open Source model for intent recognition and that's all I am allowed to share 😊", None
    elif intent=='if_event_cancelled':
        return "I don't have information regarding event cancellation", None
    elif intent=='info_refund':
        return "Sorry ! But refund isn't permitted !", None
    elif intent=='is_info_verified':
        return "Each alphabet of information I provide is thoroughly investigated 🔎", None
    elif intent=='ticket_ways':
        return "You can get your ticket using Whatsapp, Email, MMS or simply download it !", None
    elif intent=='feedback_processing':
        return "Each feedback is like a million dollars 💰 to us ! We inspect each and try to improve user experience in it entirety!"
    elif intent=='enhance_experience':
        return "You can enhance your experience by following the guidelines mentioned by specific museums and monitoring the crowd and weather intel provided by Prachin", None
    elif intent=='FAQs':
        return "Launching you to the planet !", "faqs"
    elif intent=='info_museum_list_city':
        return "This feature is still in development! ",None
    else:
        return "Report to the OG Yogya that this intent isn't recognized 😎", None
    
    return "No option", None

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
