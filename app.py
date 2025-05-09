from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
import locale
import requests
import json
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)


# Simple responses for the chatbot
RESPONSES = {
    # Basic greetings
    "مرحبا": "أهلاً وسهلاً! كيف يمكنني مساعدتك اليوم؟",
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته! كيف حالك؟",
    "كيف حالك": "أنا بخير، شكراً على سؤالك! كيف يمكنني مساعدتك؟",
    "صباح الخير": "صباح النور! أتمنى لك يوماً سعيداً",
    "مساء الخير": "مساء النور! أتمنى لك مساءً سعيداً",
    
    # Identity and purpose
    "من انت": "أنا مساعد ذكي مصمم لمساعدتك. يمكنك التحدث معي باللغة العربية.",
    "ما هو اسمك": "اسمي المساعد الذكي، وأنا هنا لمساعدتك",
    "ماذا يمكنك أن تفعل": "يمكنني التحدث معك باللغة العربية والإجابة على أسئلتك البسيطة",
    
    # Common questions
    "كيف يمكنني استخدامك": "يمكنك التحدث معي باللغة العربية وطرح أسئلتك، وسأحاول مساعدتك",
    
    # Farewell
    "مع السلامة": "مع السلامة! أتمنى أن أكون قد ساعدتك",
    "الى اللقاء": "إلى اللقاء! أتمنى لك يوماً سعيداً",
    "شكراً": "العفو! أنا هنا دائماً لمساعدتك",
    
    # Help
    "ساعدني": "بالتأكيد! كيف يمكنني مساعدتك؟",
    "لا أفهم": "لا تقلق، يمكنك إعادة صياغة سؤالك بطريقة أخرى",
    "ماذا تقول": "أنا هنا لمساعدتك. هل يمكنك توضيح سؤالك؟",
    
    # New additions
    "كيف حالك اليوم": "أنا بخير والحمد لله، كيف حالك أنت؟",
    "من صنعك": "تم صنعي باستخدام تقنيات الذكاء الاصطناعي لمساعدتك في المهام المختلفة",
    "هل أنت ذكي": "نعم، أنا مصمم لمساعدتك بأفضل ما يمكنني",
    "هل يمكنك التحدث بالعربية": "نعم، يمكنني التحدث باللغة العربية بطلاقة",
    "ما هي قدراتك": "يمكنني مساعدتك في معرفة الوقت والتاريخ ومواقيت الصلاة وإجراء العمليات الحسابية البسيطة",
    "هل أنت روبوت": "نعم، أنا مساعد ذكي مصمم لمساعدتك في المهام المختلفة",
    "كيف تعمل": "أعمل من خلال معالجة أسئلتك وتقديم الإجابات المناسبة باستخدام الذكاء الاصطناعي",
    "هل يمكنك التعلم": "نعم، يمكنني التعلم من خلال التفاعل معك وتحسين إجاباتي",
    "ما هو هدفك": "هدفي هو مساعدتك وتقديم المعلومات المفيدة لك بأفضل طريقة ممكنة",
    "هل يمكنك الغناء": "عذراً، لا أستطيع الغناء، لكن يمكنني مساعدتك في مهام أخرى",
    "هل يمكنك الرقص": "عذراً، لا أستطيع الرقص، لكن يمكنني مساعدتك في مهام أخرى",
    "هل أنت حقيقي": "أنا مساعد ذكي افتراضي، لكنني هنا لمساعدتك بشكل حقيقي",
    "ما هو عمرك": "أنا مساعد ذكي جديد، لكن عمري لا يهم بقدر ما يهمني مساعدتك",
    "هل يمكنك الكذب": "لا، أنا مصمم لقول الحقيقة دائماً ومساعدتك بشكل صادق",
    "ما هي لغاتك": "أستطيع التحدث باللغة العربية بطلاقة",
    "هل أنت متاح دائماً": "نعم، أنا متاح دائماً لمساعدتك عندما تحتاج إلي",
    "كيف يمكنني التواصل معك": "يمكنك التحدث معي مباشرة باللغة العربية وسأحاول مساعدتك",
    "هل يمكنك حفظ المعلومات": "نعم، يمكنني حفظ المعلومات خلال محادثتنا الحالية",
    "ما هي حدودك": "يمكنني مساعدتك في معرفة الوقت والتاريخ ومواقيت الصلاة والحسابات البسيطة، لكن لدي حدود في المهام المعقدة",
    "هل يمكنك التحدث مع أشخاص آخرين": "نعم، يمكنني التحدث مع أي شخص يتحدث العربية"
}

# Follow-up responses for common conversation flows
FOLLOW_UP_RESPONSES = {
    "بخير": "حسناً، كيف يمكنني مساعدتك اليوم؟",
    "الحمد لله": "الحمد لله، كيف يمكنني مساعدتك؟",
    "تمام": "ممتاز! كيف يمكنني مساعدتك؟",
    "ممتاز": "رائع! كيف يمكنني مساعدتك؟",
    "جيد": "حسناً، كيف يمكنني مساعدتك؟",
    "كويس": "ممتاز! كيف يمكنني مساعدتك؟",
    "تمام الحمد لله": "الحمد لله، كيف يمكنني مساعدتك؟",
    "الحمدلله": "الحمد لله، كيف يمكنني مساعدتك؟",
    "ماشي": "حسناً، كيف يمكنني مساعدتك؟",
    "تمام الحمدلله": "الحمد لله، كيف يمكنني مساعدتك؟",
    # New follow-up responses
    "حسنا": "هل هناك شيء آخر تريد معرفته؟",
    "تمام جدا": "رائع! هل هناك شيء آخر يمكنني مساعدتك به؟",
    "شكرا جزيلا": "العفو! أنا هنا دائماً لمساعدتك",
    "ممتاز جدا": "سعيد أنني استطعت مساعدتك! هل هناك شيء آخر؟",
    "رائع": "شكراً لك! هل هناك شيء آخر تريد معرفته؟",
    "جميل": "سعيد أنك استفدت! هل هناك شيء آخر يمكنني مساعدتك به؟",
    "حلو": "شكراً لك! هل تريد معرفة المزيد؟",
    "ماشي تمام": "حسناً، هل هناك شيء آخر تريد معرفته؟",
    "تمام جدا": "رائع! هل هناك شيء آخر يمكنني مساعدتك به؟",
    "شكرا كتير": "العفو! أنا هنا دائماً لمساعدتك"
}

def get_arabic_time():
    # Get current time in Egypt timezone
    egypt_tz = pytz.timezone('Africa/Cairo')
    current_time = datetime.now(egypt_tz)
    
    # Format time in 12-hour format
    hour = current_time.hour
    minute = current_time.minute
    
    # Convert to 12-hour format
    if hour > 12:
        hour = hour - 12
        period = "مساءً"
    else:
        period = "صباحاً"
    
    # Format the time string in Arabic
    time_str = f"الساعة الآن {hour}:{minute:02d} {period}"
    return time_str

def get_arabic_date():
    # Get current date in Egypt timezone
    egypt_tz = pytz.timezone('Africa/Cairo')
    current_date = datetime.now(egypt_tz)
    
    # Arabic month names
    arabic_months = {
        1: "يناير",
        2: "فبراير",
        3: "مارس",
        4: "أبريل",
        5: "مايو",
        6: "يونيو",
        7: "يوليو",
        8: "أغسطس",
        9: "سبتمبر",
        10: "أكتوبر",
        11: "نوفمبر",
        12: "ديسمبر"
    }
    
    # Arabic day names
    arabic_days = {
        0: "الاثنين",
        1: "الثلاثاء",
        2: "الأربعاء",
        3: "الخميس",
        4: "الجمعة",
        5: "السبت",
        6: "الأحد"
    }
    
    # Get the day name, date, and month
    day_name = arabic_days[current_date.weekday()]
    day = current_date.day
    month = arabic_months[current_date.month]
    year = current_date.year
    
    # Format the date string in Arabic
    date_str = f"اليوم {day_name} {day} {month} {year}"
    return date_str

def get_prayer_times():
    try:
        # Get current date
        current_date = datetime.now().strftime('%d-%m-%Y')
        
        # API endpoint for prayer times in Cairo
        url = f"http://api.aladhan.com/v1/timingsByCity/{current_date}?city=Cairo&country=Egypt&method=5"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            timings = data['data']['timings']
            
            def convert_to_12h(time_str):
                hour, minute = map(int, time_str.split(':'))
                if hour > 12:
                    hour = hour - 12
                    period = "مساءً"
                else:
                    period = "صباحاً"
                return f"{hour}:{minute:02d} {period}"
            
            # Format prayer times in Arabic with 12-hour format
            prayer_times = f"""مواقيت الصلاة اليوم:
الفجر: {convert_to_12h(timings['Fajr'])}
الشروق: {convert_to_12h(timings['Sunrise'])}
الظهر: {convert_to_12h(timings['Dhuhr'])}
العصر: {convert_to_12h(timings['Asr'])}
المغرب: {convert_to_12h(timings['Maghrib'])}
العشاء: {convert_to_12h(timings['Isha'])}"""
            return prayer_times
        else:
            return "عذراً، حدث خطأ في جلب مواقيت الصلاة. يرجى المحاولة مرة أخرى لاحقاً."
    except:
        return "عذراً، حدث خطأ في جلب مواقيت الصلاة. يرجى المحاولة مرة أخرى لاحقاً."

def calculate(expression):
    try:
        # Remove any spaces and convert Arabic numbers to English
        expression = expression.replace(" ", "")
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        
        # Evaluate the expression
        result = eval(expression)
        return f"النتيجة هي: {result}"
    except:
        return "عذراً، لا يمكنني حساب هذه العملية. يرجى التأكد من صحة العملية الحسابية."

def get_response(message):
    # Convert message to lowercase for better matching
    message = message.strip()
    
    # Check for time-related questions
    time_questions = [
        "ما هو الوقت",
        "كم الساعة",
        "التوقيت",
        "الوقت",
        "كم الساعة الآن",
        "ما هو التوقيت الحالي",
        "كم الساعة دلوقتي",
        "الساعة كام",
        "الساعة كم",
        "كم الساعة",
        "التوقيت كام",
        "التوقيت كم",
        "الساعة",
        "التوقيت",
        "دلوقتي الساعة كام",
        "دلوقتي الساعة كم",
        "الساعة كام دلوقتي",
        "الساعة كم دلوقتي"
    ]
    if message in time_questions:
        return get_arabic_time()
    
    # Check for date-related questions
    date_questions = [
        "ما هو التاريخ",
        "التاريخ",
        "اليوم كام",
        "اليوم كم",
        "التاريخ كام",
        "التاريخ كم",
        "كم التاريخ",
        "ما هو اليوم",
        "اليوم",
        "اي يوم",
        "اي يوم النهاردة",
        "النهاردة كام",
        "النهاردة كم",
        "اي شهر",
        "اي شهر دلوقتي",
        "اي سنة",
        "اي سنة دلوقتي",
        "كم السنة",
        "السنة كام",
        "السنة كم"
    ]
    if message in date_questions:
        return get_arabic_date()
    
    # Check for prayer times questions
    prayer_questions = [
        "مواقيت الصلاة",
        "مواعيد الصلاة",
        "الصلاة",
        "اذان",
        "الاذان",
        "متى الصلاة",
        "متى وقت الصلاة",
        "متى صلاة",
        "متى اذان",
        "متى الاذان",
        "مواقيت الصلاة اليوم",
        "مواعيد الصلاة اليوم",
        "الصلاة كام",
        "الصلاة كم",
        "اذان كام",
        "اذان كم"
    ]
    if message in prayer_questions:
        return get_prayer_times()
    
    # Check for calculation questions
    if any(op in message for op in ['+', '-', '*', '/', '×', '÷']):
        return calculate(message)
    
    # Check for follow-up responses
    if message in FOLLOW_UP_RESPONSES:
        return FOLLOW_UP_RESPONSES[message]
    
    # Check for exact matches
    if message in RESPONSES:
        return RESPONSES[message]
    
    # Default response if no match is found
    return "عذراً، لم أفهم سؤالك. هل يمكنك إعادة صياغته بطريقة أخرى؟"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message', '')
    bot_response = get_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True) 