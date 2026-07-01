import os
"""
Language Manager for Maize Disease Detection System
"""

import psycopg2
from psycopg2 import Error


class LanguageManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.translations = self.get_translations()

    def connect(self):
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            try:
                self.connection = psycopg2.connect(database_url)
                print("✅ Language Manager connected to PostgreSQL")
            except Error as e:
                print(f"❌ Language Manager DB connection error: {e}")
                self.connection = None
        else:
            print("⚠️ Language Manager: DATABASE_URL not set")
            self.connection = None

    def get_translations(self):
        return {
            "home": {"en": "Home", "sw": "Nyumbani"},
            "about": {"en": "About", "sw": "Kuhusu"},
            "dashboard": {"en": "Dashboard", "sw": "Dashibodi"},
            "login": {"en": "Login", "sw": "Ingia"},
            "register": {"en": "Register", "sw": "Jisajili"},
            "logout": {"en": "Logout", "sw": "Toka"},
            "profile": {"en": "Profile", "sw": "Wasifu"},
            "admin_dashboard": {"en": "Admin Dashboard", "sw": "Dashibodi ya Msimamizi"},
            "officer_dashboard": {"en": "Officer Dashboard", "sw": "Dashibodi ya Afisa"},
            "total_users": {"en": "Total Users", "sw": "Jumla ya Watumiaji"},
            "total_farmers": {"en": "Total Farmers", "sw": "Jumla ya Wakulima"},
            "total_officers": {"en": "Extension Officers", "sw": "Maafisa Ugani"},
            "total_predictions": {"en": "Total Predictions", "sw": "Jumla ya Utabiri"},
            "pending": {"en": "Pending", "sw": "Inasubiri"},
            "diseases": {"en": "Diseases", "sw": "Magonjwa"},
            "welcome_back": {"en": "Welcome back", "sw": "Karibu tena"},
            "full_system_control": {"en": "You have full control over the system", "sw": "Una udhibiti kamili wa mfumo"},
            "farmers": {"en": "Farmers", "sw": "Wakulima"},
            "extension_officers": {"en": "Extension Officers", "sw": "Maafisa Ugani"},
            "admins": {"en": "Admins", "sw": "Wasimamizi"},
            "pending_approvals": {"en": "Pending Approvals", "sw": "Idhini Zinazosubiri"},
            "add_new_farmer": {"en": "Add New Farmer", "sw": "Ongeza Mkulima Mpya"},
            "add_new_officer": {"en": "Add New Officer", "sw": "Ongeza Afisa Mpya"},
            "add_new_admin": {"en": "Add New Admin", "sw": "Ongeza Msimamizi Mpya"},
            "add_new_disease": {"en": "Add New Disease", "sw": "Ongeza Ugonjwa Mpya"},
            "user_activity_logs": {"en": "User Activity Logs", "sw": "Rekodi za Shughuli za Watumiaji"},
            "refresh_data": {"en": "Refresh Data", "sw": "Onyesha Upya Data"},
            "id": {"en": "ID", "sw": "Kitambulisho"},
            "name": {"en": "Name", "sw": "Jina"},
            "phone": {"en": "Phone", "sw": "Simu"},
            "email": {"en": "Email", "sw": "Barua Pepe"},
            "location": {"en": "Location", "sw": "Mahali"},
            "district": {"en": "District", "sw": "Wilaya"},
            "region": {"en": "Region", "sw": "Mkoa"},
            "status": {"en": "Status", "sw": "Hali"},
            "role": {"en": "Role", "sw": "Nafasi"},
            "actions": {"en": "Actions", "sw": "Vitendo"},
            "registered": {"en": "Registered", "sw": "Aliyesajiliwa"},
            "approved": {"en": "Approved", "sw": "Imeidhinishwa"},
            "active": {"en": "Active", "sw": "Inafanya kazi"},
            "inactive": {"en": "Inactive", "sw": "Haifanyi kazi"},
            "farmer": {"en": "Farmer", "sw": "Mkulima"},
            "officer": {"en": "Officer", "sw": "Afisa"},
            "admin": {"en": "Admin", "sw": "Msimamizi"},
            "maize_disease_system": {"en": "Maize Disease Detection System", "sw": "Mfumo wa Utambuzi wa Magonjwa ya Mahindi"},
            "helping_farmers": {"en": "Helping farmers protect their crops", "sw": "Kuwasaidia wakulima kulinda mazao yao"},
            "powered_by_ai": {"en": "Powered by Artificial Intelligence", "sw": "Inaendeshwa na Akili Bandia"},
            "accuracy": {"en": "Accuracy", "sw": "Usahihi"},
            "instant_results": {"en": "Instant Results", "sw": "Matokeo ya Papo hapo"},
            "edit": {"en": "Edit", "sw": "Hariri"},
            "delete": {"en": "Delete", "sw": "Futa"},
            "view": {"en": "View", "sw": "Angalia"},
            "add": {"en": "Add", "sw": "Ongeza"},
            "save": {"en": "Save", "sw": "Hifadhi"},
            "cancel": {"en": "Cancel", "sw": "Ghairi"},
            "close": {"en": "Close", "sw": "Funga"},
            "back": {"en": "Back", "sw": "Rudi"},
            "approve": {"en": "Approve", "sw": "Idhinisha"},
            "reject": {"en": "Reject", "sw": "Kataa"},
            "search": {"en": "Search", "sw": "Tafuta"},
            "my_profile": {"en": "My Profile", "sw": "Wasifu Wangu"},
            "prediction_history": {"en": "Prediction History", "sw": "Historia ya Utabiri"},
            "maize_disease_detection": {"en": "Maize Disease Detection", "sw": "Utambuzi wa Magonjwa ya Mahindi"},
            "upload_image": {"en": "Upload Image", "sw": "Pakia Picha"},
            "take_photo": {"en": "Take Photo", "sw": "Piga Picha"},
            "click_or_drag": {"en": "Click or drag image here", "sw": "Bonyeza au buruta picha hapa"},
            "choose_image": {"en": "Choose Image", "sw": "Chagua Picha"},
            "analyze_disease": {"en": "Analyze Disease", "sw": "Chambua Ugonjwa"},
            "new_prediction": {"en": "New Prediction", "sw": "Utabiri Mpya"},
            "analyzing": {"en": "Analyzing...", "sw": "Inachambua..."},
            "change_image": {"en": "Change Image", "sw": "Badilisha Picha"},
            "retake": {"en": "Retake", "sw": "Piga Tena"},
            "maize_leaf_only": {"en": "Please upload a clear image of a maize leaf", "sw": "Tafadhali pakia picha wazi ya jani la mahindi"},
            "diagnosis_result": {"en": "Diagnosis Result", "sw": "Matokeo ya Utambuzi"},
            "description": {"en": "Description", "sw": "Maelezo"},
            "symptoms": {"en": "Symptoms", "sw": "Dalili"},
            "treatment": {"en": "Treatment", "sw": "Matibabu"},
            "organic_treatment": {"en": "Organic Treatment", "sw": "Matibabu Asilia"},
            "chemical_treatment": {"en": "Chemical Treatment", "sw": "Matibabu ya Kemikali"},
            "cultural_practices": {"en": "Cultural Practices", "sw": "Mbinu za Kitamaduni"},
            "action_plan": {"en": "Action Plan", "sw": "Mpango wa Utekelezaji"},
            "confidence": {"en": "Confidence", "sw": "Uhakika"},
            "reports": {"en": "Reports", "sw": "Ripoti"},
            "generate_report": {"en": "Generate Report", "sw": "Tengeneza Ripoti"},
            "user_reports": {"en": "User Reports", "sw": "Ripoti za Watumiaji"},
            "disease_reports": {"en": "Disease Reports", "sw": "Ripoti za Magonjwa"},
            "analytics": {"en": "Analytics", "sw": "Uchambuzi"},
            "disease_management": {"en": "Disease Management", "sw": "Udhibiti wa Magonjwa"},
            "disease_name_en": {"en": "Disease Name (English)", "sw": "Jina la Ugonjwa (Kiingereza)"},
            "disease_name_sw": {"en": "Disease Name (Swahili)", "sw": "Jina la Ugonjwa (Kiswahili)"},
            "scientific_name": {"en": "Scientific Name", "sw": "Jina la Kisayansi"},
            "welcome_title": {"en": "AI-Powered Maize Disease Detection", "sw": "Utambuzi wa Magonjwa ya Mahindi kwa AI"},
            "welcome_subtitle": {"en": "Early Detection for Better Harvest", "sw": "Utambuzi wa Mapema kwa Mavuno Bora"},
            "hero_description": {"en": "Protect your maize crops with our advanced AI technology. Upload a photo and get instant diagnosis and treatment recommendations.", "sw": "Linda mazao yako ya mahindi kwa teknolojia ya AI. Pakia picha na upate utambuzi wa papo hapo."},
            "get_started": {"en": "Get Started", "sw": "Anza"},
            "how_it_works": {"en": "How It Works", "sw": "Jinsi Inavyofanya Kazi"},
            "step_desc": {"en": "Three simple steps to protect your maize crop", "sw": "Hatua tatu rahisi za kulinda mazao yako ya mahindi"},
            "step1_title": {"en": "Capture or Upload", "sw": "Piga au Pakia Picha"},
            "step1_desc": {"en": "Take a clear photo of the affected maize leaf using your phone camera, or upload an existing image from your gallery.", "sw": "Piga picha wazi ya jani la mahindi lililoathirika kwa kamera ya simu yako, au pakia picha iliyopo kwenye nyaraka zako."},
            "step2_title": {"en": "AI Detection", "sw": "Utambuzi wa AI"},
            "step2_desc": {"en": "Our advanced AI model analyzes the image and identifies the specific maize disease with high accuracy (95%+).", "sw": "Mfano wetu wa AI huchambua picha na kutambua ugonjwa mahususi wa mahindi kwa usahihi wa juu (95%+)."},
            "step3_title": {"en": "Get Recommendations", "sw": "Pata Mapendekezo"},
            "step3_desc": {"en": "Receive instant treatment recommendations including chemical, organic, and cultural control methods.", "sw": "Pokea mapendekezo ya matibabu ya papo hapo ikiwa ni pamoja na kemikali, asili, na mbinu za kitamaduni."},
            "detection_accuracy": {"en": "Detection Accuracy", "sw": "Usahihi wa Utambuzi"},
            "disease_types": {"en": "Disease Types", "sw": "Aina za Magonjwa"},
            "avg_response_time": {"en": "Average Response Time", "sw": "Wastani wa Muda wa Kujibu"},
            "common_diseases": {"en": "Common Maize Diseases We Detect", "sw": "Magonjwa ya Kawaida ya Mahindi Tunayogundua"},
            "common_diseases_desc": {"en": "Our AI can identify these common maize diseases with high accuracy", "sw": "AI yetu inaweza kutambua magonjwa haya ya kawaida ya mahindi kwa usahihi wa juu"},
            "common_rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "common_rust_desc": {"en": "Reddish-brown pustules on leaves causing reduced yield", "sw": "Madoa mekundu-kahawia kwenye majani yanayosababisha kupungua kwa mavuno"},
            "gray_leaf_spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "gray_leaf_spot_desc": {"en": "Rectangular gray lesions causing premature leaf death", "sw": "Madoa meusi yenye umbo la mstatili yanayosababisha majani kukauka mapema"},
            "northern_leaf_blight": {"en": "Northern Leaf Blight", "sw": "Ugonjwa wa Majani wa Kaskazini"},
            "northern_leaf_blight_desc": {"en": "Long cigar-shaped lesions that reduce photosynthesis", "sw": "Madoa marefu yenye umbo la sigara yanayopunguza usanisinuru"},
            "healthy_leaf": {"en": "Healthy Leaf", "sw": "Jani lenye Afya"},
            "healthy_leaf_desc": {"en": "No disease symptoms detected", "sw": "Hakuna dalili za ugonjwa zilizogunduliwa"},
            "protect_crop_title": {"en": "Protect Your Maize Crop Today!", "sw": "Linda Mazao Yako ya Mahindi Leo!"},
            "protect_crop_message": {"en": "Early detection saves your harvest. Upload a photo now and get instant diagnosis and treatment recommendations.", "sw": "Utambuzi wa mapema huokoa mavuno yako. Pakia picha sasa na upate utambuzi na mapendekezo ya matibabu ya papo hapo."},
            "start_detection": {"en": "Start Disease Detection", "sw": "Anza Utambuzi wa Ugonjwa"},
            "welcome_back_officer": {"en": "Welcome back", "sw": "Karibu tena"},
            "your_region": {"en": "Your Region", "sw": "Mkoa Wako"},
            "total_diagnoses": {"en": "Total Diagnoses", "sw": "Jumla ya Uchunguzi"},
            "diseases_detected": {"en": "Diseases Detected", "sw": "Magonjwa Yaliyogunduliwa"},
            "active_farmers_30d": {"en": "Active Farmers (30 days)", "sw": "Wakulima Wanafanya kazi (Siku 30)"},
            "all_farmers": {"en": "All Farmers", "sw": "Wakulima Wote"},
            "search_farmers": {"en": "Search Farmers", "sw": "Tafuta Wakulima"},
            "recent_predictions": {"en": "Recent Predictions", "sw": "Utabiri wa Hivi Karibuni"},
            "all_diseases": {"en": "All Diseases", "sw": "Magonjwa Yote"},
            "farmer_name": {"en": "Farmer Name", "sw": "Jina la Mkulima"},
            "date": {"en": "Date", "sw": "Tarehe"},
            "action": {"en": "Action", "sw": "Kitendo"},
            "disease": {"en": "Disease", "sw": "Ugonjwa"},
            "total_logins": {"en": "Total Logins", "sw": "Jumla ya Kuingia"},
            "total_logouts": {"en": "Total Logouts", "sw": "Jumla ya Kutoka"},
            "active_users": {"en": "Active Users", "sw": "Watumiaji Wanafanya kazi"},
            "user_activities": {"en": "User Activities", "sw": "Shughuli za Watumiaji"},
            "date_time": {"en": "Date & Time", "sw": "Tarehe na Saa"},
            "user": {"en": "User", "sw": "Mtumiaji"},
            "activity_type": {"en": "Activity Type", "sw": "Aina ya Shughuli"},
            "details": {"en": "Details", "sw": "Maelezo"},
            "ip_address": {"en": "IP Address", "sw": "Anwani ya IP"},
            "profile_photo": {"en": "Profile Photo", "sw": "Picha ya Wasifu"},
            "upload_photo": {"en": "Upload Photo", "sw": "Pakia Picha"},
            "account_info": {"en": "Account Information", "sw": "Taarifa za Akaunti"},
            "member_since": {"en": "Member since", "sw": "Amejiunga tangu"},
            "last_login": {"en": "Last login", "sw": "Mara ya mwisho kuingia"},
            "edit_profile": {"en": "Edit Profile", "sw": "Hariri Wasifu"},
            "save_changes": {"en": "Save Changes", "sw": "Hifadhi Mabadiliko"},
            "change_password": {"en": "Change Password", "sw": "Badilisha Nenosiri"},
            "current_password": {"en": "Current Password", "sw": "Nenosiri la Sasa"},
            "new_password": {"en": "New Password", "sw": "Nenosiri Jipya"},
            "update_password": {"en": "Update Password", "sw": "Sasisha Nenosiri"},
        }

    def get_text(self, key, language="en"):
        if key in self.translations:
            return self.translations[key].get(language, self.translations[key].get("en", key))
        return key

    def get_disease_translation(self, disease_name, language="en"):
        disease_translations = {
            "Blight": {"en": "Northern Leaf Blight", "sw": "Ugonjwa wa Majani wa Kaskazini"},
            "Common_Rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "Gray_Leaf_Spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "Healthy": {"en": "Healthy", "sw": "Afya"},
        }
        if disease_name in disease_translations:
            return disease_translations[disease_name].get(language, disease_name)
        return disease_name


lang_manager = LanguageManager()
