import os
"""
Language Manager for Maize Disease Detection System
PostgreSQL Version - Complete Website Translation
"""

import psycopg2
from psycopg2 import Error


class LanguageManager:
    """Manage translations and language-specific content"""

    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to database using DATABASE_URL from environment"""
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            try:
                self.connection = psycopg2.connect(database_url)
                print("? Language Manager connected to PostgreSQL")
            except Error as e:
                print(f"? Language Manager DB connection error: {e}")
                self.connection = None
        else:
            print("?? Language Manager: DATABASE_URL not set, running without DB")
            self.connection = None

    def get_text(self, key, language="en"):
        """Get translated text by key"""
        translations = {
            # ==================== GENERAL / NAVIGATION ====================
            "home": {"en": "Home", "sw": "Nyumbani"},
            "about": {"en": "About", "sw": "Kuhusu"},
            "dashboard": {"en": "Dashboard", "sw": "Dashibodi"},
            "farmers": {"en": "Farmers", "sw": "Wakulima"},
            "detect_disease": {"en": "Detect Disease", "sw": "Gundua Ugonjwa"},
            "predict": {"en": "Predict Disease", "sw": "Tabiri Ugonjwa"},
            "predict_disease": {"en": "Predict Disease", "sw": "Tabiri Ugonjwa"},
            "prediction": {"en": "Prediction", "sw": "Utabiri"},
            "history": {"en": "History", "sw": "Historia"},
            "notifications": {"en": "Notifications", "sw": "Arifa"},
            "profile": {"en": "Profile", "sw": "Wasifu"},
            "logout": {"en": "Logout", "sw": "Toka"},
            "login": {"en": "Login", "sw": "Ingia"},
            "register": {"en": "Register", "sw": "Jisajili"},
            "back": {"en": "Back", "sw": "Rudi"},
            "cancel": {"en": "Cancel", "sw": "Ghairi"},
            "save": {"en": "Save", "sw": "Hifadhi"},
            "confirm": {"en": "Confirm", "sw": "Thibitisha"},
            "close": {"en": "Close", "sw": "Funga"},
            "submit": {"en": "Submit", "sw": "Wasilisha"},
            "edit": {"en": "Edit", "sw": "Hariri"},
            "delete": {"en": "Delete", "sw": "Futa"},
            "update": {"en": "Update", "sw": "Sasisha"},
            "add": {"en": "Add", "sw": "Ongeza"},
            "view": {"en": "View", "sw": "Angalia"},
            "search": {"en": "Search", "sw": "Tafuta"},
            "filter": {"en": "Filter", "sw": "Chuja"},
            "export": {"en": "Export", "sw": "Toa Nje"},
            "refresh": {"en": "Refresh", "sw": "Onyesha Upya"},
            "loading": {"en": "Loading...", "sw": "Inapakia..."},
            "no_data": {"en": "No data available", "sw": "Hakuna data"},
            "error": {"en": "Error", "sw": "Hitilafu"},
            "success": {"en": "Success", "sw": "Imefanikiwa"},
            "warning": {"en": "Warning", "sw": "Tahadhari"},
            "info": {"en": "Information", "sw": "Taarifa"},
            
            # ==================== DASHBOARD ====================
            "admin_dashboard": {"en": "Admin Dashboard", "sw": "Dashibodi ya Msimamizi"},
            "officer_dashboard": {"en": "Officer Dashboard", "sw": "Dashibodi ya Afisa"},
            "farmer_dashboard": {"en": "Farmer Dashboard", "sw": "Dashibodi ya Mkulima"},
            "total_users": {"en": "Total Users", "sw": "Jumla ya Watumiaji"},
            "total_farmers": {"en": "Total Farmers", "sw": "Jumla ya Wakulima"},
            "total_officers": {"en": "Extension Officers", "sw": "Maafisa Ugani"},
            "extension_officers": {"en": "Extension Officers", "sw": "Maafisa Ugani"},
            "total_admins": {"en": "Admins", "sw": "Wasimamizi"},
            "total_predictions": {"en": "Total Predictions", "sw": "Jumla ya Utabiri"},
            "active_diseases": {"en": "Active Diseases", "sw": "Magonjwa Yanayoendelea"},
            "pending_approvals": {"en": "Pending Approvals", "sw": "Idhini Zinazosubiri"},
            "pending": {"en": "Pending", "sw": "Inasubiri"},
            "approved": {"en": "Approved", "sw": "Imeidhinishwa"},
            "rejected": {"en": "Rejected", "sw": "Imekataliwa"},
            "active": {"en": "Active", "sw": "Inafanya kazi"},
            "inactive": {"en": "Inactive", "sw": "Haifanyi kazi"},
            "registered": {"en": "Registered", "sw": "Aliyesajiliwa"},
            "created_at": {"en": "Created", "sw": "Imeundwa"},
            "updated_at": {"en": "Updated", "sw": "Imesasishwa"},
            "actions": {"en": "Actions", "sw": "Vitendo"},
            "status": {"en": "Status", "sw": "Hali"},
            "role": {"en": "Role", "sw": "Nafasi"},
            "name": {"en": "Name", "sw": "Jina"},
            "email": {"en": "Email", "sw": "Barua Pepe"},
            "phone": {"en": "Phone", "sw": "Simu"},
            "location": {"en": "Location", "sw": "Mahali"},
            "district": {"en": "District", "sw": "Wilaya"},
            "region": {"en": "Region", "sw": "Mkoa"},
            
            # ==================== PREDICTION PAGE ====================
            "maize_disease_detection": {"en": "?? Maize Disease Detection", "sw": "?? Utambuzi wa Magonjwa ya Mahindi"},
            "upload_image": {"en": "Upload Image", "sw": "Pakia Picha"},
            "take_photo": {"en": "Take Photo", "sw": "Piga Picha"},
            "choose_image": {"en": "Choose Image", "sw": "Chagua Picha"},
            "analyze_disease": {"en": "Analyze Disease", "sw": "Chambua Ugonjwa"},
            "analyzing": {"en": "Analyzing...", "sw": "Inachambua..."},
            "new_prediction": {"en": "New Prediction", "sw": "Utabiri Mpya"},
            "click_or_drag": {"en": "Click or drag image here", "sw": "Bonyeza au buruta picha hapa"},
            "change_image": {"en": "Change Image", "sw": "Badilisha Picha"},
            "retake": {"en": "Retake", "sw": "Piga Tena"},
            "maize_leaf_only": {"en": "Please upload a clear image of a maize leaf", "sw": "Tafadhali pakia picha wazi ya jani la mahindi"},
            
            # ==================== RESULTS ====================
            "diagnosis_result": {"en": "?? Diagnosis Result", "sw": "?? Matokeo ya Utambuzi"},
            "description": {"en": "Description", "sw": "Maelezo"},
            "symptoms": {"en": "Symptoms", "sw": "Dalili"},
            "treatment": {"en": "Treatment", "sw": "Matibabu"},
            "organic_treatment": {"en": "?? Organic Treatment", "sw": "?? Matibabu Asilia"},
            "chemical_treatment": {"en": "?? Chemical Treatment", "sw": "?? Matibabu ya Kemikali"},
            "cultural_practices": {"en": "?? Cultural Practices", "sw": "?? Mbinu za Kitamaduni"},
            "action_plan": {"en": "?? Action Plan", "sw": "?? Mpango wa Utekelezaji"},
            "confidence": {"en": "Confidence", "sw": "Uhakika"},
            
            # ==================== FOOTER ====================
            "maize_disease_system": {"en": "Maize Disease Detection System", "sw": "Mfumo wa Utambuzi wa Magonjwa ya Mahindi"},
            "helping_farmers": {"en": "Helping farmers protect their crops with AI technology", "sw": "Kuwasaidia wakulima kulinda mazao yao kwa teknolojia ya AI"},
            "powered_by_ai": {"en": "Powered by Artificial Intelligence", "sw": "Inaendeshwa na Akili Bandia"},
            "accuracy": {"en": "High Accuracy", "sw": "Usahihi wa Juu"},
            "instant_results": {"en": "Instant Results", "sw": "Matokeo ya Papo hapo"},
            
            # ==================== WELCOME ====================
            "welcome_back": {"en": "Welcome back", "sw": "Karibu tena"},
            "full_system_control": {"en": "You have full control over the system", "sw": "Una udhibiti kamili wa mfumo"},
            
            # ==================== REPORTS ====================
            "reports": {"en": "Reports", "sw": "Ripoti"},
            "generate_report": {"en": "Generate Report", "sw": "Tengeneza Ripoti"},
            "user_reports": {"en": "User Reports", "sw": "Ripoti za Watumiaji"},
            "disease_reports": {"en": "Disease Reports", "sw": "Ripoti za Magonjwa"},
            "analytics": {"en": "Analytics", "sw": "Uchambuzi"},
            "reports_dashboard": {"en": "Reports Dashboard", "sw": "Dashibodi ya Ripoti"},
            "comprehensive_reports": {"en": "Comprehensive reports and analytics coming soon", "sw": "Ripoti kamili na uchambuzi zitakuja hivi karibuni"},
            "generate_user_reports": {"en": "Generate user registration and activity reports", "sw": "Tengeneza ripoti za usajili na shughuli za watumiaji"},
            "generate_disease_reports": {"en": "Disease prediction and outbreak reports", "sw": "Ripoti za utabiri na milipuko ya magonjwa"},
            "system_analytics": {"en": "System usage and performance analytics", "sw": "Uchambuzi wa matumizi na utendaji wa mfumo"},
            
            # ==================== DISEASE MANAGEMENT ====================
            "disease_management": {"en": "Disease Management", "sw": "Udhibiti wa Magonjwa"},
            "disease_name_en": {"en": "Disease Name (English)", "sw": "Jina la Ugonjwa (Kiingereza)"},
            "disease_name_sw": {"en": "Disease Name (Swahili)", "sw": "Jina la Ugonjwa (Kiswahili)"},
            "scientific_name": {"en": "Scientific Name", "sw": "Jina la Kisayansi"},
            
            # ==================== ADD USER FORMS ====================
            "add_new_farmer": {"en": "Add New Farmer", "sw": "Ongeza Mkulima Mpya"},
            "add_new_officer": {"en": "Add New Extension Officer", "sw": "Ongeza Afisa Ugani Mpya"},
            "add_new_admin": {"en": "Add New Admin", "sw": "Ongeza Msimamizi Mpya"},
            "add_new_disease": {"en": "Add New Disease", "sw": "Ongeza Ugonjwa Mpya"},
            "user_activity_logs": {"en": "User Activity Logs", "sw": "Rekodi za Shughuli za Watumiaji"},
            "refresh_data": {"en": "Refresh Data", "sw": "Onyesha Upya Data"},
            
            # ==================== PROFILE ====================
            "my_profile": {"en": "My Profile", "sw": "Wasifu Wangu"},
            "prediction_history": {"en": "Prediction History", "sw": "Historia ya Utabiri"},
            
            # ==================== TABLE HEADERS ====================
            "id": {"en": "ID", "sw": "Kitambulisho"},
            "farmer": {"en": "Farmer", "sw": "Mkulima"},
            "officer": {"en": "Officer", "sw": "Afisa"},
            "admin": {"en": "Admin", "sw": "Msimamizi"},
        }
        
        if key in translations:
            return translations[key].get(language, translations[key].get("en", key))
        return key
    
    def get_disease_translation(self, disease_name, language="en"):
        """Get translated disease name"""
        disease_translations = {
            "Blight": {"en": "Blight", "sw": "Ugonjwa wa Kuvu"},
            "Common_Rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "Gray_Leaf_Spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "Healthy": {"en": "Healthy", "sw": "Afya"},
            "Turcicum Leaf Blight": {"en": "Turcicum Leaf Blight", "sw": "Ugonjwa wa Majani wa Turcicum"},
        }
        
        if disease_name in disease_translations:
            return disease_translations[disease_name].get(language, disease_name)
        return disease_name


# Create global instance
lang_manager = LanguageManager()
