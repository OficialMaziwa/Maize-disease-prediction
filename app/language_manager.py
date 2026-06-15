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
        try:
            self.connection = psycopg2.connect(database_url) if database_url else None)
            print("Language Manager connected to PostgreSQL")
        except Error as e:
            print(f"Language Manager DB connection error: {e}")
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
            "search": {"en": "Search", "sw": "Tafuta"},
            "filter": {"en": "Filter", "sw": "Chuja"},
            "export": {"en": "Export", "sw": "Hamisha"},
            "import": {"en": "Import", "sw": "Ingiza"},
            "download": {"en": "Download", "sw": "Pakua"},
            "upload": {"en": "Upload", "sw": "Pakia"},
            "refresh": {"en": "Refresh", "sw": "Onyesha upya"},
            "loading": {"en": "Loading...", "sw": "Inapakia..."},
            "error": {"en": "Error", "sw": "Hitilafu"},
            "success": {"en": "Success", "sw": "Imefanikiwa"},
            "warning": {"en": "Warning", "sw": "Onyo"},
            "info": {"en": "Information", "sw": "Taarifa"},
            "yes": {"en": "Yes", "sw": "Ndiyo"},
            "no": {"en": "No", "sw": "Hapana"},
            "ok": {"en": "OK", "sw": "Sawa"},
            "total": {"en": "Total", "sw": "Jumla"},
            "all": {"en": "All", "sw": "Zote"},
            "none": {"en": "None", "sw": "Hakuna"},
            "actions": {"en": "Actions", "sw": "Vitendo"},
            "status": {"en": "Status", "sw": "Hali"},
            "date": {"en": "Date", "sw": "Tarehe"},
            "time": {"en": "Time", "sw": "Muda"},
            "created": {"en": "Created", "sw": "Imeundwa"},
            "updated": {"en": "Updated", "sw": "Imesasishwa"},
            "active": {"en": "Active", "sw": "Inafanya kazi"},
            "inactive": {"en": "Inactive", "sw": "Haifanyi kazi"},
            "pending": {"en": "Pending", "sw": "Inasubiri"},
            "approved": {"en": "Approved", "sw": "Imekubaliwa"},
            "rejected": {"en": "Rejected", "sw": "Imekataliwa"},
            "offline_mode": {"en": "Offline Mode", "sw": "Hali ya Nje ya Mtandao"},
            "powered_by_ai": {"en": "Powered by AI", "sw": "Inaendeshwa na AI"},
            "instant_results": {"en": "Instant Results", "sw": "Matokeo ya Papo hapo"},
            "accuracy": {"en": "Accuracy", "sw": "Usahihi"},
            "diseases": {"en": "Diseases", "sw": "Magonjwa"},
            "images_trained": {"en": "Images Trained", "sw": "Picha Zilizofunzwa"},
            "response_time": {"en": "Response Time", "sw": "Muda wa Kujibu"},
            "helping_farmers": {
                "en": "Helping farmers protect their crops",
                "sw": "Kusaidia wakulima kulinda mazao yao",
            },
            "maize_disease_system": {
                "en": "Maize Disease Detection System",
                "sw": "Mfumo wa Ugunduzi wa Magonjwa ya Mahindi",
            },
            "maize_disease_detection": {
                "en": "Maize Disease Detection",
                "sw": "Ugunduzi wa Magonjwa ya Mahindi",
            },
            "responsive_ui": {"en": "Responsive UI", "sw": "Muundo Unaobadilika"},
            "mark_all_read": {"en": "Mark all read", "sw": "Weka zote kama zimesomwa"},
            "all_notifications": {"en": "All Notifications", "sw": "Arifa Zote"},
            "officer": {"en": "Officer", "sw": "Afisa"},
            "admin": {"en": "Admin", "sw": "Msimamizi"},
            "admins": {"en": "Admins", "sw": "Wasimamizi"},
            "reports": {"en": "Reports", "sw": "Ripoti"},
            "id": {"en": "ID", "sw": "Kitambulisho"},
            "name": {"en": "Name", "sw": "Jina"},
            "phone": {"en": "Phone", "sw": "Simu"},
            "email": {"en": "Email", "sw": "Barua Pepe"},
            "location": {"en": "Location", "sw": "Eneo"},
            "district": {"en": "District", "sw": "Wilaya"},
            "region": {"en": "Region", "sw": "Mkoa"},
            "view": {"en": "View", "sw": "Angalia"},
            "mode": {"en": "Mode", "sw": "Hali"},
            "synced": {"en": "Synced", "sw": "Imesawazishwa"},
            "online": {"en": "Online", "sw": "Mtandaoni"},
            "offline": {"en": "Offline", "sw": "Nje ya Mtandao"},
            "pending_sync": {"en": "Pending Sync", "sw": "Inasubiri Kusawazishwa"},
            "user": {"en": "User", "sw": "Mtumiaji"},
            "details": {"en": "Details", "sw": "Maelezo"},
            "ip_address": {"en": "IP Address", "sw": "Anwani ya IP"},
            "unknown": {"en": "Unknown", "sw": "Hajulikani"},
            "na": {"en": "N/A", "sw": "Haipatikani"},
            "date_time": {"en": "Date & Time", "sw": "Tarehe na Muda"},
            "activity_type": {"en": "Activity Type", "sw": "Aina ya Shughuli"},
            "farmer": {"en": "Farmer", "sw": "Mkulima"},
            "action": {"en": "Action", "sw": "Kitendo"},
            "print_report": {"en": "Print Report", "sw": "Chapisha Ripoti"},
            "prediction_details": {
                "en": "Prediction Details",
                "sw": "Maelezo ya Utabiri",
            },
            "full_name": {"en": "Full Name", "sw": "Jina Kamili"},
            "phone_number": {"en": "Phone Number", "sw": "Namba ya Simu"},
            "farmer_name": {"en": "Farmer Name", "sw": "Jina la Mkulima"},
            "sms": {"en": "SMS", "sw": "Ujumbe Mfupi"},
            "copy_link": {"en": "Copy Link", "sw": "Nakili Kiungo"},
            "from_date": {"en": "From", "sw": "Kuanzia"},
            "to_date": {"en": "To", "sw": "Mpaka"},
            "to": {"en": "to", "sw": "mpaka"},
            "of": {"en": "of", "sw": "kati ya"},
            "showing": {"en": "Showing", "sw": "Inaonyesha"},
            "never": {"en": "Never", "sw": "Kamwe"},
            "print": {"en": "Print", "sw": "Chapisha"},
            "copy": {"en": "Copy", "sw": "Nakili"},
            "weekly_monitoring": {
                "en": "Weekly monitoring recommended",
                "sw": "Ufuatiliaji wa kila wiki unapendekezwa",
            },
            "immediate_action": {
                "en": "Immediate action required",
                "sw": "Hatua ya haraka inahitajika",
            },
            # ==================== AUTHENTICATION PAGES ====================
            "welcome_back_login": {"en": "Welcome Back!", "sw": "Karibu Tena!"},
            "login_to_account": {
                "en": "Login to your account",
                "sw": "Ingia kwenye akaunti yako",
            },
            "phone_or_email": {
                "en": "Phone Number or Email",
                "sw": "Namba ya Simu au Barua pepe",
            },
            "password": {"en": "Password", "sw": "Nenosiri"},
            "login_btn": {"en": "Login", "sw": "Ingia"},
            "no_account": {"en": "Don't have an account?", "sw": "Huna akaunti?"},
            "register_here": {"en": "Register here", "sw": "Jisajili hapa"},
            "forgot_password": {"en": "Forgot Password?", "sw": "Umesahau Nenosiri?"},
            "demo_accounts": {"en": "Demo Accounts", "sw": "Akaunti za Majaribio"},
            "demo_farmer": {"en": "Farmer", "sw": "Mkulima"},
            "demo_officer": {"en": "Extension Officer", "sw": "Afisa Ugani"},
            "demo_admin": {"en": "Admin", "sw": "Msimamizi"},
            "create_account": {
                "en": "Create New Account",
                "sw": "Jisajili Akaunti Mpya",
            },
            "email_optional": {
                "en": "Email (Optional)",
                "sw": "Barua pepe (Si Lazima)",
            },
            "account_type": {"en": "Account Type", "sw": "Aina ya Akaunti"},
            "extension_officer": {"en": "Extension Officer", "sw": "Afisa Ugani"},
            "confirm_password": {"en": "Confirm Password", "sw": "Thibitisha Nenosiri"},
            "phone_example": {
                "en": "Example: 255712345678",
                "sw": "Mfano: 255712345678",
            },
            "farmer_info": {
                "en": "Farmers get immediate access to disease detection and prediction features.",
                "sw": "Wakulima wanapata ufikiaji wa haraka wa huduma za kugundua na kutabiri magonjwa.",
            },
            "officer_info": {
                "en": "Extension officers need admin approval before accessing the system. Your account will be reviewed by an administrator.",
                "sw": "Maafisa ugani wanahitaji idhini ya msimamizi kabla ya kutumia mfumo. Akaunti yako itakaguliwa na msimamizi.",
            },
            "terms_agreement": {
                "en": "By registering, you agree to our terms of service",
                "sw": "Kwa kujisajili, unakubali sheria na masharti yetu",
            },
            "already_account": {
                "en": "Already have an account?",
                "sw": "Tayari una akaunti?",
            },
            "login_here": {"en": "Login here", "sw": "Ingia hapa"},
            "identifier": {"en": "Phone or Email", "sw": "Simu au Barua Pepe"},
            # ==================== HOME PAGE ====================
            "welcome_title": {
                "en": "Maize Disease Prediction System",
                "sw": "Mfumo wa Utabiri wa Magonjwa ya Mahindi",
            },
            "welcome_subtitle": {
                "en": "Early Detection for Better Harvest",
                "sw": "Ugunduzi wa Mapema kwa Mavuno Bora",
            },
            "hero_description": {
                "en": "Protect your maize crops with AI-powered disease detection. Upload a photo or take a picture of your maize leaf and get instant diagnosis and treatment recommendations.",
                "sw": "Linda mazao yako ya mahindi kwa ugunduzi wa magonjwa kwa AI. Pakia picha au piga picha ya jani lako la mahindi na upate uchunguzi wa haraka na mapendekezo ya matibabu.",
            },
            "get_started": {"en": "Get Started", "sw": "Anza"},
            "how_it_works": {"en": "How It Works", "sw": "Jinsi Inavyofanya Kazi"},
            "step1_title": {"en": "Capture or Upload", "sw": "Piga Picha au Pakia"},
            "step1_desc": {
                "en": "Take a clear photo of the affected maize leaf using your phone camera, or upload an existing image from your gallery.",
                "sw": "Piga picha wazi ya jani la mahindi lililoathirika kwa kamera ya simu yako, au pakia picha uliyonayo kwenye nyaraka zako.",
            },
            "step2_title": {"en": "AI Detection", "sw": "Ugunduzi wa AI"},
            "step2_desc": {
                "en": "Our advanced AI model analyzes the image and identifies the specific maize disease with high accuracy (95%+).",
                "sw": "Modeli yetu ya AI inachambua picha na kutambua ugonjwa maalum wa mahindi kwa usahihi wa juu (95%+).",
            },
            "step3_title": {"en": "Get Recommendations", "sw": "Pata Mapendekezo"},
            "step3_desc": {
                "en": "Receive instant treatment recommendations including chemical, organic, and cultural control methods.",
                "sw": "Pata mapendekezo ya matibabu ya haraka ikiwa ni pamoja na njia za kemikali, asili, na za kitamaduni.",
            },
            "detection_accuracy": {
                "en": "Detection Accuracy",
                "sw": "Usahihi wa Ugunduzi",
            },
            "disease_types": {"en": "Disease Types", "sw": "Aina za Magonjwa"},
            "avg_response_time": {
                "en": "Average Response Time",
                "sw": "Wastani wa Muda wa Kujibu",
            },
            "common_diseases": {
                "en": "Common Maize Diseases We Detect",
                "sw": "Magonjwa ya Kawaida ya Mahindi Tunayogundua",
            },
            "common_rust": {"en": "Common Rust", "sw": "Kutu ya Kawaida"},
            "common_rust_desc": {
                "en": "Reddish-brown pustules on leaves causing reduced yield",
                "sw": "Madoa mekundu-kahawia kwenye majani yanayosababisha kupungua kwa mavuno",
            },
            "gray_leaf_spot": {
                "en": "Gray Leaf Spot",
                "sw": "Madoa Kijivu kwenye Majani",
            },
            "gray_leaf_spot_desc": {
                "en": "Rectangular gray lesions causing premature leaf death",
                "sw": "Madoa ya kijivu yenye umbo la mstatili yanayosababisha kufa kwa majani mapema",
            },
            "northern_leaf_blight": {
                "en": "Turcicum Leaf Blight",
                "sw": "Ugonjwa wa Majani wa Turcicum",
            },
            "northern_leaf_blight_desc": {
                "en": "Long cigar-shaped lesions that reduce photosynthesis",
                "sw": "Madoa marefu yenye umbo la sigara yanayopunguza usanisinuru",
            },
            "healthy_leaf": {"en": "Healthy Leaf", "sw": "Jani Bora"},
            "healthy_leaf_desc": {
                "en": "No disease symptoms detected",
                "sw": "Hakuna dalili za ugonjwa zilizogunduliwa",
            },
            "protect_crop_title": {
                "en": "Protect Your Maize Crop Today!",
                "sw": "Linda Mazao Yako ya Mahindi Leo!",
            },
            "protect_crop_message": {
                "en": "Early detection saves your harvest. Upload a photo now and get instant diagnosis and treatment recommendations.",
                "sw": "Ugunduzi wa mapema unaokoa mavuno yako. Pakia picha sasa na upate uchunguzi wa haraka na mapendekezo ya matibabu.",
            },
            # ==================== PREDICT PAGE ====================
            "upload_image": {"en": "Upload Image", "sw": "Pakia Picha"},
            "take_photo": {"en": "Take Photo", "sw": "Piga Picha"},
            "click_or_drag": {
                "en": "Click or drag image here",
                "sw": "Bonyeza au buruta picha hapa",
            },
            "maize_leaf_only": {
                "en": "Please upload a clear image of a maize leaf only",
                "sw": "Tafadhali pakia picha wazi ya jani la mahindi pekee",
            },
            "choose_image": {"en": "Choose Image", "sw": "Chagua Picha"},
            "change_image": {"en": "Change Image", "sw": "Badilisha Picha"},
            "retake": {"en": "Retake", "sw": "Piga Tena"},
            "analyzing": {"en": "Analyzing", "sw": "Inachambua"},
            "description": {"en": "Description", "sw": "Maelezo"},
            "symptoms": {"en": "Symptoms", "sw": "Dalili"},
            "organic_treatment": {"en": "Organic Treatment", "sw": "Matibabu Asili"},
            "chemical_treatment": {
                "en": "Chemical Treatment",
                "sw": "Matibabu ya Kemikali",
            },
            "cultural_practices": {
                "en": "Cultural Practices",
                "sw": "Mazoea ya Kitamaduni",
            },
            "action_plan": {"en": "Action Plan", "sw": "Mpango wa Kutekeleza"},
            "new_prediction": {"en": "New Prediction", "sw": "Utabiri Mpya"},
            "upload_maize_leaf": {
                "en": "Upload Maize Leaf Image",
                "sw": "Pakia Picha ya Jani la Mahindi",
            },
            "supported_formats": {
                "en": "Supported formats: JPG, PNG, GIF (Max 10MB)",
                "sw": "Miundo inayotumika: JPG, PNG, GIF (Upeo 10MB)",
            },
            "analyze_disease": {"en": "Analyze Disease", "sw": "Chambua Ugonjwa"},
            "how_it_works_title": {
                "en": "How it works:",
                "sw": "Jinsi inavyofanya kazi:",
            },
            "step_photo": {
                "en": "Take a clear photo of a maize leaf showing symptoms",
                "sw": "Piga picha wazi ya jani la mahindi linaloonyesha dalili",
            },
            "step_upload": {
                "en": "Upload the image using the form above",
                "sw": "Pakia picha kwa kutumia fomu iliyo juu",
            },
            "step_analyze": {
                "en": "Our AI will analyze the image and identify the disease",
                "sw": "AI yetu itachambua picha na kutambua ugonjwa",
            },
            "step_results": {
                "en": "You'll receive treatment recommendations instantly",
                "sw": "Utapokea mapendekezo ya matibabu papo hapo",
            },
            "tips_best_results": {
                "en": "Tips for best results:",
                "sw": "Vidokezo kwa matokeo bora:",
            },
            "tip_good_lighting": {
                "en": "Use a well-lit area to take the photo",
                "sw": "Tumia eneo lenye mwanga mzuri kupiga picha",
            },
            "tip_focus_affected": {
                "en": "Focus on the affected area of the leaf",
                "sw": "Lenga eneo lililoathirika la jani",
            },
            "tip_clear_visibility": {
                "en": "Make sure the leaf is clearly visible",
                "sw": "Hakikisha jani linaonekana wazi",
            },
            "tip_avoid_blurry": {
                "en": "Avoid blurry or distant photos",
                "sw": "Epuka picha zisizo wazi au za mbali",
            },
            # ==================== DIAGNOSIS RESULT PAGE ====================
            "diagnosis_result": {
                "en": "Diagnosis Result",
                "sw": "Matokeo ya Uchunguzi",
            },
            "detection_results": {
                "en": "Detection Results",
                "sw": "Matokeo ya Ugunduzi",
            },
            "disease": {"en": "Disease", "sw": "Ugonjwa"},
            "confidence": {"en": "Confidence", "sw": "Uhakika"},
            "confidence_level": {"en": "Confidence Level", "sw": "Kiwango cha Uhakika"},
            "confidence_percentage": {"en": "Confidence", "sw": "Asilimia ya Uhakika"},
            "detection_date": {"en": "Detection Date", "sw": "Tarehe ya Ugunduzi"},
            "disease_information": {
                "en": "Disease Information",
                "sw": "Taarifa za Ugonjwa",
            },
            "severity": {"en": "Severity", "sw": "Ukali"},
            "recommended_treatments": {
                "en": "Recommended Treatments",
                "sw": "Matibabu Yanayopendekezwa",
            },
            "organic_options": {"en": "Organic Options", "sw": "Njia Asili"},
            "long_term_solutions": {
                "en": "Long-term Solutions",
                "sw": "Suluhu za Muda Mrefu",
            },
            "analyze_another": {
                "en": "Analyze Another Image",
                "sw": "Chambua Picha Nyingine",
            },
            "back_to_home": {"en": "Back to Home", "sw": "Rudi Nyumbani"},
            "diagnosis": {"en": "Diagnosis", "sw": "Uchunguzi"},
            "economic_impact": {"en": "Economic Impact", "sw": "Athari za Kiuchumi"},
            "response_deadline": {
                "en": "Response Deadline",
                "sw": "Muda wa Kukabiliana",
            },
            "step_by_step": {
                "en": "Step by Step Guide",
                "sw": "Mwongozo wa Hatua kwa Hatua",
            },
            "organic_solutions": {"en": "Organic Solutions", "sw": "Suluhu za Asili"},
            "prevention_monitoring": {
                "en": "Prevention & Monitoring",
                "sw": "Kinga na Ufuatiliaji",
            },
            "long_term_prevention": {
                "en": "Long-term Prevention",
                "sw": "Kinga ya Muda Mrefu",
            },
            "monitoring_schedule": {
                "en": "Monitoring Schedule",
                "sw": "Ratiba ya Ufuatiliaji",
            },
            "follow_up": {"en": "Follow-up", "sw": "Ufuatiliaji"},
            "save_html": {"en": "Save HTML", "sw": "Hifadhi HTML"},
            "save_text": {"en": "Save Text", "sw": "Hifadhi Maandishi"},
            "new_analysis": {"en": "New Analysis", "sw": "Uchambuzi Mpya"},
            "report_saved": {
                "en": "Report saved successfully!",
                "sw": "Ripoti imehifadhiwa kikamilifu!",
            },
            "report_copied": {
                "en": "Report copied to clipboard!",
                "sw": "Ripoti imenakiliwa kwenye clipboard!",
            },
            "no_chemical_treatment": {
                "en": "No chemical treatment information available",
                "sw": "Hakuna taarifa za matibabu ya kemikali",
            },
            "no_organic_treatment": {
                "en": "No organic treatment information available",
                "sw": "Hakuna taarifa za matibabu asili",
            },
            "no_prevention_info": {
                "en": "No prevention information available",
                "sw": "Hakuna taarifa za kinga",
            },
            "diagnosis_report": {"en": "Diagnosis Report", "sw": "Ripoti ya Uchunguzi"},
            "share_information": {"en": "Share Information", "sw": "Shiriki Taarifa"},
            "share_message": {
                "en": "Share this diagnosis report with other farmers or extension officers",
                "sw": "Shiriki ripoti hii ya uchunguzi na wakulima wengine au maafisa ugani",
            },
            "share_via_whatsapp": {
                "en": "Share via WhatsApp",
                "sw": "Shiriki kupitia WhatsApp",
            },
            "share_via_sms": {
                "en": "Share via SMS",
                "sw": "Shiriki kupitia Ujumbe Mfupi",
            },
            "economic_impact_default": {
                "en": "Significant yield losses if not controlled promptly",
                "sw": "Hasara kubwa ya mavuno ikitoshindwa kudhibitiwa kwa haraka",
            },
            "no_action_plan": {
                "en": "No specific action plan available",
                "sw": "Hakuna mpango maalum wa utekelezaji",
            },
            "follow_up_default": {
                "en": "Re-evaluate after 7 days",
                "sw": "Tathmini tena baada ya siku 7",
            },
            "high": {"en": "High", "sw": "Kubwa"},
            "medium": {"en": "Medium", "sw": "Wastani"},
            "low": {"en": "Low", "sw": "Ndogo"},
            "critical": {"en": "Critical", "sw": "Muhimu"},
            "severe": {"en": "Severe", "sw": "Kali"},
            "moderate": {"en": "Moderate", "sw": "Wastani"},
            "mild": {"en": "Mild", "sw": "Nyepesi"},
            # ==================== PROFILE PAGE ====================
            "profile_photo": {"en": "Profile Photo", "sw": "Picha ya Wasifu"},
            "upload_photo": {"en": "Upload Photo", "sw": "Pakia Picha"},
            "remove_photo": {"en": "Remove Photo", "sw": "Ondoa Picha"},
            "account_info": {"en": "Account Information", "sw": "Taarifa za Akaunti"},
            "member_since": {"en": "Member Since", "sw": "Akaunti Imefunguliwa"},
            "last_login": {"en": "Last Login", "sw": "Kuingia Mwisho"},
            "edit_profile": {"en": "Edit Profile", "sw": "Hariri Wasifu"},
            "save_changes": {"en": "Save Changes", "sw": "Hifadhi Mabadiliko"},
            "change_password": {"en": "Change Password", "sw": "Badilisha Nenosiri"},
            "current_password": {"en": "Current Password", "sw": "Nenosiri la Sasa"},
            "new_password": {"en": "New Password", "sw": "Nenosiri Jipya"},
            "update_password": {"en": "Update Password", "sw": "Sasisha Nenosiri"},
            "language_preference": {
                "en": "Language Preference",
                "sw": "Lugha Unayopendelea",
            },
            "profile_updated": {
                "en": "Profile updated successfully",
                "sw": "Wasifu umesasishwa kikamilifu",
            },
            "my_profile": {"en": "My Profile", "sw": "Wasifu Wangu"},
            # ==================== ADMIN DASHBOARD ====================
            "admin_dashboard": {
                "en": "Admin Dashboard",
                "sw": "Dashibodi ya Msimamizi",
            },
            "total_users": {"en": "Total Users", "sw": "Jumla ya Watumiaji"},
            "registered_users": {
                "en": "Registered users",
                "sw": "Watumiaji waliojisajili",
            },
            "active_farmers": {
                "en": "Active farmers",
                "sw": "Wakulima wanaofanya kazi",
            },
            "extension_officers": {"en": "Extension officers", "sw": "Maafisa ugani"},
            "total_diagnoses": {"en": "Total diagnoses", "sw": "Jumla ya uchunguzi"},
            "user_management": {
                "en": "User Management",
                "sw": "Usimamizi wa Watumiaji",
            },
            "add_new_farmer": {"en": "Add New Farmer", "sw": "Ongeza Mkulima Mpya"},
            "add_new_officer": {
                "en": "Add New Extension Officer",
                "sw": "Ongeza Afisa Ugani Mpya",
            },
            "add_new_admin": {"en": "Add New Admin", "sw": "Ongeza Msimamizi Mpya"},
            "add_new_disease": {"en": "Add New Disease", "sw": "Ongeza Ugonjwa Mpya"},
            "pending_approvals": {
                "en": "Pending Approvals",
                "sw": "Idhini Zinazosubiri",
            },
            "review_applications": {
                "en": "Review and approve pending extension officer applications",
                "sw": "Kagua na uidhinisha maombi ya maafisa ugani yanayosubiri",
            },
            "application_date": {"en": "Application Date", "sw": "Tarehe ya Maombi"},
            "approve": {"en": "Approve", "sw": "Kubali"},
            "reject": {"en": "Reject", "sw": "Kataa"},
            "review": {"en": "Review", "sw": "Kagua"},
            "export_reports": {"en": "Export Reports", "sw": "Hamisha Ripoti"},
            "export_users": {
                "en": "Export Users Report",
                "sw": "Hamisha Ripoti ya Watumiaji",
            },
            "export_farmers": {
                "en": "Export Farmers Report",
                "sw": "Hamisha Ripoti ya Wakulima",
            },
            "export_officers": {
                "en": "Export Officers Report",
                "sw": "Hamisha Ripoti ya Maafisa",
            },
            "export_predictions": {"en": "Export Predictions", "sw": "Hamisha Utabiri"},
            "user_distribution": {
                "en": "User Distribution",
                "sw": "Usambazaji wa Watumiaji",
            },
            "system_activity": {"en": "System Activity", "sw": "Shughuli za Mfumo"},
            "reports_dashboard": {
                "en": "Reports Dashboard",
                "sw": "Dashibodi ya Ripoti",
            },
            "comprehensive_reports": {
                "en": "Comprehensive reports and analytics coming soon",
                "sw": "Ripoti kamili na uchambuzi zinakuja hivi karibuni",
            },
            "generate_report": {"en": "Generate Report", "sw": "Tengeneza Ripoti"},
            "user_reports": {"en": "User Reports", "sw": "Ripoti za Watumiaji"},
            "disease_reports": {"en": "Disease Reports", "sw": "Ripoti za Magonjwa"},
            "analytics": {"en": "Analytics", "sw": "Uchambuzi"},
            "system_analytics": {
                "en": "System usage and performance analytics",
                "sw": "Matumizi ya mfumo na uchambuzi wa utendaji",
            },
            "generate_user_reports": {
                "en": "Generate user registration and activity reports",
                "sw": "Tengeneza ripoti za usajili na shughuli za watumiaji",
            },
            "generate_disease_reports": {
                "en": "Disease prediction and outbreak reports",
                "sw": "Utabiri wa magonjwa na ripoti za milipuko",
            },
            "disease_name_en": {
                "en": "Disease Name (English)",
                "sw": "Jina la Ugonjwa (Kiingereza)",
            },
            "disease_name_sw": {
                "en": "Disease Name (Swahili)",
                "sw": "Jina la Ugonjwa (Kiswahili)",
            },
            "scientific_name": {"en": "Scientific Name", "sw": "Jina la Kisayansi"},
            "refresh_data": {"en": "Refresh Data", "sw": "Onyesha Data Mpya"},
            "full_system_control": {
                "en": "Full system control panel",
                "sw": "Paneli kamili ya udhibiti wa mfumo",
            },
            "welcome_back": {"en": "Welcome back", "sw": "Karibu tena"},
            "back_to_dashboard": {
                "en": "Back to Dashboard",
                "sw": "Rudi kwenye Dashibodi",
            },
            "user_activity_logs": {
                "en": "User Activity Logs",
                "sw": "Rekodi za Shughuli za Watumiaji",
            },
            # ==================== OFFICER DASHBOARD ====================
            "officer_dashboard": {
                "en": "Extension Officer Dashboard",
                "sw": "Dashibodi ya Afisa Ugani",
            },
            "welcome_back_officer": {"en": "Welcome back", "sw": "Karibu tena"},
            "your_region": {"en": "Your Region", "sw": "Mkoa Wako"},
            "all_regions": {"en": "All Regions", "sw": "Mikoa Yote"},
            "total_farmers": {"en": "Total Farmers", "sw": "Jumla ya Wakulima"},
            "total_diagnoses": {"en": "Total Diagnoses", "sw": "Jumla ya Uchunguzi"},
            "diseases_detected": {
                "en": "Diseases Detected",
                "sw": "Magonjwa Yaliyogunduliwa",
            },
            "active_farmers_30d": {
                "en": "Active Farmers (30 days)",
                "sw": "Wakulima Wanaofanya Kazi (siku 30)",
            },
            "disease_management": {
                "en": "Disease Management",
                "sw": "Usimamizi wa Magonjwa",
            },
            "all_farmers": {"en": "All Farmers", "sw": "Wakulima Wote"},
            "search_farmers": {"en": "Search farmers...", "sw": "Tafuta wakulima..."},
            "export_csv": {"en": "Export CSV", "sw": "Hamisha CSV"},
            "recent_predictions": {
                "en": "Recent Predictions",
                "sw": "Utabiri wa Hivi Karibuni",
            },
            "all_diseases": {"en": "All Diseases", "sw": "Magonjwa Yote"},
            "turcicum_leaf_blight": {
                "en": "Turcicum Leaf Blight",
                "sw": "Ugonjwa wa Turcicum",
            },
            "gray_leaf_spot": {"en": "Gray Leaf Spot", "sw": "Madoa Kijivu"},
            "healthy": {"en": "Healthy", "sw": "Afya"},
            "add_disease": {"en": "Add Disease", "sw": "Ongeza Ugonjwa"},
            "edit_disease": {"en": "Edit Disease", "sw": "Hariri Ugonjwa"},
            "description_en": {
                "en": "Description (English)",
                "sw": "Maelezo (Kiingereza)",
            },
            "description_sw": {
                "en": "Description (Swahili)",
                "sw": "Maelezo (Kiswahili)",
            },
            "symptoms_en": {"en": "Symptoms (English)", "sw": "Dalili (Kiingereza)"},
            "symptoms_sw": {"en": "Symptoms (Swahili)", "sw": "Dalili (Kiswahili)"},
            "treatment_en": {
                "en": "Treatment (English)",
                "sw": "Matibabu (Kiingereza)",
            },
            "treatment_sw": {
                "en": "Treatment (Swahili)",
                "sw": "Matibabu (Kiswahili)",
            },
            "loading_diseases": {
                "en": "Loading diseases...",
                "sw": "Inapakia magonjwa...",
            },
            "loading_farmers": {
                "en": "Loading farmers...",
                "sw": "Inapakia wakulima...",
            },
            "loading_predictions": {
                "en": "Loading predictions...",
                "sw": "Inapakia utabiri...",
            },
            "farmers_supported": {
                "en": "Farmers Supported",
                "sw": "Wakulima Wanaosaidiwa",
            },
            "active_cases": {"en": "Active Cases", "sw": "Kesi Zinazoendelea"},
            "resolved_cases": {"en": "Resolved Cases", "sw": "Kesi Zilizotatuliwa"},
            "manage_farmers": {"en": "Manage Farmers", "sw": "Simamia Wakulima"},
            "recent_cases": {
                "en": "Recent Farmer Cases",
                "sw": "Kesi za Hivi Karibuni za Wakulima",
            },
            "view_details": {"en": "View Details", "sw": "Angalia Maelezo"},
            # ==================== USER ACTIVITY LOGS ====================
            "total_logins": {"en": "Total Logins", "sw": "Jumla ya Kuingia"},
            "total_logouts": {"en": "Total Logouts", "sw": "Jumla ya Kutoka"},
            "active_users": {"en": "Active Users", "sw": "Watumiaji Wanaofanya Kazi"},
            "user_activities": {"en": "User Activities", "sw": "Shughuli za Watumiaji"},
            "loading_activities": {
                "en": "Loading activities...",
                "sw": "Inapakia shughuli...",
            },
            "no_activities_found": {
                "en": "No activities found",
                "sw": "Hakuna shughuli zilizopatikana",
            },
            "error_loading_activities": {
                "en": "Failed to load activities",
                "sw": "Imeshindwa kupakia shughuli",
            },
            # ==================== HISTORY / PREDICTION HISTORY ====================
            "prediction_history": {
                "en": "Prediction History",
                "sw": "Historia ya Utabiri",
            },
            "stored_locally": {
                "en": "Stored Locally",
                "sw": "Imehifadhiwa Ndani ya Kifaa",
            },
            "total_predictions": {"en": "Total Predictions", "sw": "Jumla ya Utabiri"},
            "avg_confidence": {"en": "Average Confidence", "sw": "Wastani wa Uhakika"},
            "offline_predictions": {
                "en": "Offline Predictions",
                "sw": "Utabiri wa Nje ya Mtandao",
            },
            "clear_history": {"en": "Clear History", "sw": "Futa Historia"},
            "sync_now": {"en": "Sync Now", "sw": "Sawazisha Sasa"},
            "loading_history": {
                "en": "Loading history...",
                "sw": "Inapakia historia...",
            },
            "error_loading_history": {
                "en": "Error loading history",
                "sw": "Hitilafu katika kupakia historia",
            },
            "no_history": {
                "en": "No History Found",
                "sw": "Hakuna Historia Iliyopatikana",
            },
            "no_history_message": {
                "en": "You haven't made any predictions yet.",
                "sw": "Bado hujafanya utabiri wowote.",
            },
            "make_prediction": {"en": "Make a Prediction", "sw": "Fanya Utabiri"},
            "confirm_delete": {
                "en": "Are you sure you want to delete this prediction?",
                "sw": "Una uhakika unataka kufuta utabiri huu?",
            },
            "confirm_clear_all": {
                "en": "Are you sure you want to clear all prediction history? This cannot be undone.",
                "sw": "Una uhakika unataka kufuta historia yote ya utabiri? Hii haiwezi kutenduliwa.",
            },
            "delete_confirmation": {
                "en": "Delete Confirmation",
                "sw": "Uthibitisho wa Kufuta",
            },
            "clear_all_confirmation": {
                "en": "Clear All Confirmation",
                "sw": "Uthibitisho wa Kufuta Zote",
            },
            # ==================== FARMERS MANAGEMENT ====================
            "farmers_management": {
                "en": "Farmers Management",
                "sw": "Usimamizi wa Wakulima",
            },
            "farmers_management_desc": {
                "en": "Manage and monitor all registered farmers in your region",
                "sw": "Simamia na ufuatilie wakulima wote waliojisajili katika mkoa wako",
            },
            "inactive_farmers": {
                "en": "Inactive Farmers",
                "sw": "Wakulima Wasiofanya Kazi",
            },
            "search_by_name_phone_location": {
                "en": "Search by name, phone or location...",
                "sw": "Tafuta kwa jina, simu au eneo...",
            },
            "all_status": {"en": "All Status", "sw": "Hali Zote"},
            "all_districts": {"en": "All Districts", "sw": "Wilaya Zote"},
            "registered_date": {"en": "Registered", "sw": "Alijisajili"},
            "loading_farmers_data": {
                "en": "Loading farmers data...",
                "sw": "Inapakia data za wakulima...",
            },
            "farmer_details": {"en": "Farmer Details", "sw": "Maelezo ya Mkulima"},
            "view_diagnoses": {"en": "View Diagnoses", "sw": "Angalia Uchunguzi"},
            "farmer_diagnoses_history": {
                "en": "Farmer Diagnoses History",
                "sw": "Historia ya Uchunguzi wa Mkulima",
            },
            "registered_farmers": {
                "en": "Registered Farmers",
                "sw": "Wakulima Waliojisajili",
            },
            "farmer_id": {"en": "Farmer ID", "sw": "Kitambulisho cha Mkulima"},
            "registered": {"en": "Registered", "sw": "Alijisajili"},
            # ==================== USER DETAILS ====================
            "user_details": {"en": "User Details", "sw": "Maelezo ya Mtumiaji"},
            "user_profile": {"en": "User Profile", "sw": "Wasifu wa Mtumiaji"},
            "user_profile_desc": {
                "en": "View and manage user information, activity, and account settings",
                "sw": "Tazama na usimamie taarifa za mtumiaji, shughuli, na mipangilio ya akaunti",
            },
            "success_rate": {"en": "Success Rate", "sw": "Kiwango cha Mafanikio"},
            "active_days": {"en": "Active Days", "sw": "Siku za Shughuli"},
            "personal_information": {
                "en": "Personal Information",
                "sw": "Taarifa za Kibinafsi",
            },
            "location_information": {
                "en": "Location Information",
                "sw": "Taarifa za Eneo",
            },
            "recent_activity": {
                "en": "Recent Activity",
                "sw": "Shughuli za Hivi Karibuni",
            },
            "loading_activity": {
                "en": "Loading activity...",
                "sw": "Inapakia shughuli...",
            },
            "toggle_status": {"en": "Toggle Status", "sw": "Badilisha Hali"},
            "edit_user": {"en": "Edit User", "sw": "Hariri Mtumiaji"},
            "delete_user": {"en": "Delete User", "sw": "Futa Mtumiaji"},
            "send_notification": {"en": "Send Notification", "sw": "Tuma Arifa"},
            "title_english": {"en": "Title (English)", "sw": "Kichwa (Kiingereza)"},
            "title_swahili": {"en": "Title (Swahili)", "sw": "Kichwa (Kiswahili)"},
            "message_english": {"en": "Message (English)", "sw": "Ujumbe (Kiingereza)"},
            "message_swahili": {"en": "Message (Swahili)", "sw": "Ujumbe (Kiswahili)"},
            "notification_type": {"en": "Notification Type", "sw": "Aina ya Arifa"},
            "system_update": {"en": "System Update", "sw": "Sasisho la Mfumo"},
            "tip": {"en": "Tip", "sw": "Kidokezo"},
            "reminder": {"en": "Reminder", "sw": "Kumbusho"},
            "weather_alert": {"en": "Weather Alert", "sw": "Tahadhari ya Hali ya Hewa"},
            # ==================== OFFLINE PAGE ====================
            "offline_title": {
                "en": "You are currently offline",
                "sw": "Uko nje ya mtandao kwa sasa",
            },
            "offline_message": {
                "en": "You can still analyze maize diseases using the offline AI model",
                "sw": "Bado unaweza kuchambua magonjwa ya mahindi kwa kutumia modeli ya AI ya nje ya mtandao",
            },
            "continue_offline": {
                "en": "Continue Offline",
                "sw": "Endelea Nje ya Mtandao",
            },
            # ==================== ERROR MESSAGES ====================
            "no_file_selected": {
                "en": "No file selected",
                "sw": "Hakuna faili iliyochaguliwa",
            },
            "file_too_large": {
                "en": "File is too large. Maximum size is 10MB",
                "sw": "Faili ni kubwa sana. Ukubwa wa juu ni 10MB",
            },
            "invalid_file_type": {
                "en": "Invalid file type. Please upload JPG, PNG, or GIF",
                "sw": "Aina ya faili si sahihi. Tafadhali pakia JPG, PNG, au GIF",
            },
            "required_fields": {
                "en": "All required fields must be filled",
                "sw": "Sehemu zote zinazohitajika lazima zijazwe",
            },
            "password_mismatch": {
                "en": "Passwords do not match",
                "sw": "Nyaya hazifanani",
            },
            "invalid_credentials": {
                "en": "Invalid phone number/email or password",
                "sw": "Namba ya simu/barua pepe au nenosiri si sahihi",
            },
            "access_denied": {
                "en": "Access denied. Admin privileges required.",
                "sw": "Ufikiaji umekataliwa. Haki za msimamizi zinahitajika.",
            },
            "officer_access_denied": {
                "en": "Access denied. Extension officer privileges required.",
                "sw": "Ufikiaji umekataliwa. Haki za afisa ugani zinahitajika.",
            },
            "pending_approval": {
                "en": "Your account is pending admin approval. Please wait for approval.",
                "sw": "Akaunti yako inasubiri idhini ya msimamizi. Tafadhali subiri idhini.",
            },
            "prediction_error": {
                "en": "Error during prediction",
                "sw": "Hitilafu wakati wa utabiri",
            },
            "login_required": {
                "en": "Please login to view profile",
                "sw": "Tafadhali ingia ili kuona wasifu",
            },
            # ==================== SUCCESS MESSAGES ====================
            "register_success": {
                "en": "Registration successful! Please login",
                "sw": "Usajili umefanikiwa! Tafadhali ingia",
            },
            "officer_register_success": {
                "en": "Registration submitted! Awaiting admin approval.",
                "sw": "Usajili umewasilishwa! Subiri idhini ya msimamizi.",
            },
            "login_success": {
                "en": "Login successful! Welcome back",
                "sw": "Kuingia kumefanikiwa! Karibu tena",
            },
            "logout_success": {
                "en": "You have been logged out",
                "sw": "Umetoka nje ya mfumo",
            },
            "officer_approved": {
                "en": "Officer approved successfully",
                "sw": "Afisa amekubaliwa kikamilifu",
            },
            "officer_rejected": {
                "en": "Officer application rejected",
                "sw": "Maombi ya afisa yamekataliwa",
            },
            "disease_added": {
                "en": "Disease added successfully",
                "sw": "Ugonjwa umeongezwa kikamilifu",
            },
            "disease_updated": {
                "en": "Disease updated successfully",
                "sw": "Ugonjwa umesasishwa kikamilifu",
            },
            "disease_deleted": {
                "en": "Disease deleted successfully",
                "sw": "Ugonjwa umefutwa kikamilifu",
            },
            "user_deleted": {
                "en": "User deleted successfully",
                "sw": "Mtumiaji amefutwa kikamilifu",
            },
            "user_created": {
                "en": "User created successfully",
                "sw": "Mtumiaji ameundwa kikamilifu",
            },
            "user_updated": {
                "en": "User updated successfully",
                "sw": "Mtumiaji amesasishwa kikamilifu",
            },
            # ==================== DISEASE NAMES ====================
            "Common_Rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "Blight": {"en": "Turcicum Leaf Blight", "sw": "Ugonjwa wa Turcicum"},
            "Gray_Leaf_Spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi ya Majani"},
            "Maize_Lethal_Necrosis": {
                "en": "Maize Lethal Necrosis",
                "sw": "Ugonjwa wa Kukauka kwa Mahindi",
            },
            # ==================== ABOUT PAGE ====================
            "about_project": {
                "en": "About Maize Disease Prediction System",
                "sw": "Kuhusu Mfumo wa Utabiri wa Magonjwa ya Mahindi",
            },
            "about_description": {
                "en": "Empowering Tanzanian farmers with AI-powered disease detection and treatment recommendations",
                "sw": "Kuwapa nguvu wakulima wa Tanzania kwa ugunduzi wa magonjwa kwa AI na mapendekezo ya matibabu",
            },
            "our_mission": {"en": "Our Mission", "sw": "Dhamira Yetu"},
            "mission_text": {
                "en": "To provide Tanzanian smallholder farmers with an accessible, accurate, and easy-to-use AI-powered tool for early detection of maize diseases, reducing crop losses, and improving food security through instant treatment recommendations.",
                "sw": "Kuwapa wakulima wadogo wa Tanzania zana inayopatikana, sahihi, na rahisi kutumia ya AI kwa ugunduzi wa mapema wa magonjwa ya mahindi, kupunguza hasara ya mazao, na kuboresha usalama wa chakula kupitia mapendekezo ya matibabu ya papo hapo.",
            },
            "our_vision": {"en": "Our Vision", "sw": "Dira Yetu"},
            "vision_text": {
                "en": "A future where every farmer in Tanzania has access to digital agricultural extension services, enabling them to make informed decisions, increase crop productivity, and build resilient farming communities through technology.",
                "sw": "Mustakabali ambapo kila mkulima nchini Tanzania anapata huduma za ugani za kidijitali, kuwawezesha kufanya maamuzi sahihi, kuongeza tija ya mazao, na kujenga jumuiya za kilimo zenye uwezo wa kukabiliana na changamoto kupitia teknolojia.",
            },
            "technology_stack": {
                "en": "Technology Stack",
                "sw": "Teknolojia Tunazotumia",
            },
            "model_performance": {
                "en": "Model Performance",
                "sw": "Utendaji wa Modeli",
            },
            "the_problem": {
                "en": "The Problem We Solve",
                "sw": "Tatizo Tunalosuluhisha",
            },
            "problem_text": {
                "en": "Maize farmers in Tanzania struggle to accurately identify crop diseases at an early stage, resulting in significant yield losses, unnecessary pesticide expenditure, and environmental degradation. Our system provides instant, reliable disease diagnosis to help farmers make informed decisions.",
                "sw": "Wakulima wa mahindi nchini Tanzania wanatatizika kutambua magonjwa ya mazao kwa usahihi katika hatua za awali, na kusababisha hasara kubwa ya mavuno, matumizi yasiyo ya lazima ya dawa, na uharibifu wa mazingira. Mfumo wetu hutoa uchunguzi wa haraka na wa kuaminika wa magonjwa kusaidia wakulima kufanya maamuzi sahihi.",
            },
            "diseases_we_detect": {
                "en": "Diseases We Detect",
                "sw": "Magonjwa Tunayogundua",
            },
            "ready_to_protect": {
                "en": "Ready to Protect Your Maize Crop?",
                "sw": "Uko tayari kulinda mazao yako ya mahindi?",
            },
            # ==================== ADDITIONAL KEYS ====================
            "step_desc": {
                "en": "Three simple steps to protect your maize crop",
                "sw": "Hatua tatu rahisi za kulinda mazao yako ya mahindi",
            },
            "common_diseases_desc": {
                "en": "Our AI can identify these common maize diseases with high accuracy",
                "sw": "AI yetu inaweza kutambua magonjwa haya ya kawaida ya mahindi kwa usahihi wa juu",
            },
            "start_detection": {
                "en": "Start Disease Detection",
                "sw": "Anza Ugunduzi wa Magonjwa",
            },
            "upload_photo_cta": {
                "en": "Upload a photo of your maize leaf now and get instant diagnosis and treatment recommendations.",
                "sw": "Pakia picha ya jani lako la mahindi sasa na upate uchunguzi wa haraka na mapendekezo ya matibabu.",
            },
            "stored_locally": {
                "en": "Stored Locally",
                "sw": "Imehifadhiwa Ndani ya Kifaa",
            },
            "role": {"en": "Role", "sw": "Nafasi"},
        }

        # Return translation if key exists, otherwise return the key itself
        if key in translations:
            return translations[key].get(language, translations[key]["en"])
        return key

    def get_disease_translation(self, disease_name, language="sw"):
        """Get disease name in specified language"""
        disease_translations = {
            "Blight": {"en": "Turcicum Leaf Blight", "sw": "Ugonjwa wa Turcicum"},
            "Common_Rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "Gray_Leaf_Spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi ya Majani"},
            "Healthy": {"en": "Healthy", "sw": "Afya"},
            "Maize_Lethal_Necrosis": {
                "en": "Maize Lethal Necrosis",
                "sw": "Ugonjwa wa Kukauka kwa Mahindi",
            },
        }

        if disease_name in disease_translations:
            return disease_translations[disease_name].get(
                language, disease_translations[disease_name]["en"]
            )
        return disease_name

    def get_severity_translation(self, severity, language="sw"):
        """Translate severity level"""
        translations = {
            "High": "Kubwa",
            "Medium": "Wastani",
            "Low": "Ndogo",
            "Critical": "Muhimu",
            "Severe": "Kali",
            "Moderate": "Wastani",
            "Mild": "Nyepesi",
            "None": "Hakuna",
        }

        if language == "sw":
            return translations.get(severity, severity)
        return severity

    def get_recommendation_translation(self, recommendation, language="sw"):
        """Translate recommendation text"""
        recommendations_translations = {
            "Apply fungicide immediately": "Tumia dawa ya kuvu mara moja",
            "Remove infected leaves": "Ondoa majani yaliyoathirika",
            "Practice crop rotation": "Zoea mzunguko wa mazao",
            "Use resistant varieties": "Tumia aina zinazostahimili magonjwa",
            "Ensure proper spacing": "Hakikisha umbali sahihi wa kupanda",
            "Apply organic compost": "Tumia mbolea ya asili",
            "Monitor regularly": "Fuatilia mara kwa mara",
            "Destroy infected plants": "Haribu mimea iliyoathirika",
            "Clean farming equipment": "Safisha vifaa vya kilimo",
            "Avoid overhead irrigation": "Epuka umwagiliaji wa juu",
            "Apply neem oil": "Tumia mafuta ya mwarobaini",
            "Use baking soda solution": "Tumia suluhisho la baking soda",
        }

        if language == "sw" and recommendation in recommendations_translations:
            return recommendations_translations[recommendation]
        return recommendation

    def translate_action_plan(self, action_plan, language="sw"):
        """Translate action plan list"""
        if language == "en" or not action_plan:
            return action_plan

        translated_plan = []
        for step in action_plan:
            translated_plan.append(self.get_recommendation_translation(step, language))
        return translated_plan


# Create global instance
lang_manager = LanguageManager()
