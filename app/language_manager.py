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
