import os
from dotenv import load_dotenv

load_dotenv()

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
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            try:
                self.connection = psycopg2.connect(database_url)
                print("✅ Language Manager connected to PostgreSQL")
            except Error as e:
                print(f"❌ Language Manager DB connection error: {e}")
                self.connection = None
        else:
            print("ℹ️ Language Manager: No DATABASE_URL configured, using built-in translations.")
            self.connection = None

    def get_translations(self):
        return {
            # ==================== ACTIONS ====================
            "action": {"en": "Action", "sw": "Kitendo"},
            "action_plan": {"en": "Action Plan", "sw": "Mpango wa Utekelezaji"},
            "actions": {"en": "Actions", "sw": "Vitendo"},
            "add": {"en": "Add", "sw": "Ongeza"},
            "add_new_admin": {"en": "Add New Admin", "sw": "Ongeza Msimamizi Mpya"},
            "add_new_disease": {"en": "Add New Disease", "sw": "Ongeza Ugonjwa Mpya"},
            "add_new_farmer": {"en": "Add New Farmer", "sw": "Ongeza Mkulima Mpya"},
            "add_new_officer": {"en": "Add New Officer", "sw": "Ongeza Afisa Mpya"},
            "all_diseases": {"en": "All Diseases", "sw": "Magonjwa Yote"},
            "all_farmers": {"en": "All Farmers", "sw": "Wakulima Wote"},
            "analyze_disease": {"en": "Analyze Disease", "sw": "Chambua Ugonjwa"},
            "analyzing": {"en": "Analyzing...", "sw": "Inachambua..."},
            "analytics": {"en": "Analytics", "sw": "Uchambuzi"},
            "approve": {"en": "Approve", "sw": "Idhinisha"},
            "approved": {"en": "Approved", "sw": "Imeidhinishwa"},
            "avg_response_time": {
                "en": "Average Response Time",
                "sw": "Wastani wa Muda wa Kujibu",
            },
            "hero_main_title": {
                "en": "AI-Powered Maize Disease",
                "sw": "Ugonjwa wa Mahindi Unaotumia AI",
            },
            "hero_tagline": {
                "en": "Early Detection for Better Harvest",
                "sw": "Ugunduzi wa Mapema kwa Mavuno Bora",
            },
            "hero_description": {
                "en": "Protect your maize crops with our advanced AI technology. Upload a photo and get instant diagnosis and treatment recommendations.",
                "sw": "Linda mazao yako ya mahindi kwa teknolojia yetu ya hali ya juu ya AI. Pakia picha na upate uchunguzi wa papo hapo na mapendekezo ya matibabu.",
            },
            "helping_farmers": {
                "en": "Helping farmers protect their crops",
                "sw": "Kuwasaidia wakulima kulinda mazao yao",
            },
            # ==================== BACK ====================
            "back": {"en": "Back", "sw": "Rudi"},
            # ==================== CANCEL ====================
            "cancel": {"en": "Cancel", "sw": "Ghairi"},
            "change_image": {"en": "Change Image", "sw": "Badilisha Picha"},
            "change_password": {"en": "Change Password", "sw": "Badilisha Nenosiri"},
            "chemical_treatment": {
                "en": "Chemical Treatment",
                "sw": "Matibabu ya Kemikali",
            },
            "choose_image": {"en": "Choose Image", "sw": "Chagua Picha"},
            "click_or_drag": {
                "en": "Click or drag image here",
                "sw": "Bonyeza au buruta picha hapa",
            },
            "close": {"en": "Close", "sw": "Funga"},
            "common_diseases": {
                "en": "Common Maize Diseases We Detect",
                "sw": "Magonjwa ya Kawaida ya Mahindi Tunayogundua",
            },
            "common_diseases_desc": {
                "en": "Our AI can identify these common maize diseases with high accuracy",
                "sw": "AI yetu inaweza kutambua magonjwa haya ya kawaida ya mahindi kwa usahihi wa juu",
            },
            "common_rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "common_rust_desc": {
                "en": "Reddish-brown pustules on leaves causing reduced yield",
                "sw": "Madoa mekundu-kahawia kwenye majani yanayosababisha kupungua kwa mavuno",
            },
            "confidence": {"en": "Confidence", "sw": "Uhakika"},
            "confidence_level": {"en": "Confidence Level", "sw": "Kiwango cha Uhakika"},
            "copy": {"en": "Copy", "sw": "Nakili"},
            "copy_link": {"en": "Copy Link", "sw": "Nakili Kiungo"},
            "cultural_practices": {
                "en": "Cultural Practices",
                "sw": "Mbinu za Kitamaduni",
            },
            "current_password": {"en": "Current Password", "sw": "Nenosiri la Sasa"},
            # ==================== DASHBOARD ====================
            "dashboard": {"en": "Dashboard", "sw": "Dashibodi"},
            "date": {"en": "Date", "sw": "Tarehe"},
            "date_time": {"en": "Date & Time", "sw": "Tarehe na Saa"},
            "delete": {"en": "Delete", "sw": "Futa"},
            "description": {"en": "Description", "sw": "Maelezo"},
            "detection_accuracy": {
                "en": "Detection Accuracy",
                "sw": "Usahihi wa Utambuzi",
            },
            "details": {"en": "Details", "sw": "Maelezo"},
            "diagnosis": {"en": "Diagnosis", "sw": "Utambuzi"},
            "diagnosis_report": {"en": "Diagnosis Report", "sw": "Ripoti ya Utambuzi"},
            "diagnosis_result": {"en": "Diagnosis Result", "sw": "Matokeo ya Utambuzi"},
            "disease": {"en": "Disease", "sw": "Ugonjwa"},
            "disease_management": {
                "en": "Disease Management",
                "sw": "Udhibiti wa Magonjwa",
            },
            "disease_name_en": {
                "en": "Disease Name (English)",
                "sw": "Jina la Ugonjwa (Kiingereza)",
            },
            "disease_name_sw": {
                "en": "Disease Name (Swahili)",
                "sw": "Jina la Ugonjwa (Kiswahili)",
            },
            "disease_reports": {"en": "Disease Reports", "sw": "Ripoti za Magonjwa"},
            "disease_types": {"en": "Disease Types", "sw": "Aina za Magonjwa"},
            "diseases": {"en": "Diseases", "sw": "Magonjwa"},
            "diseases_detected": {
                "en": "Diseases Detected",
                "sw": "Magonjwa Yaliyogunduliwa",
            },
            "district": {"en": "District", "sw": "Wilaya"},
            # ==================== ECONOMIC IMPACT ====================
            "economic_impact": {"en": "Economic Impact", "sw": "Athari za Kiuchumi"},
            "economic_impact_default": {
                "en": "Significant yield losses if not controlled promptly",
                "sw": "Hasara kubwa ya mavuno ikiwa haitadhibitiwa haraka",
            },
            "edit": {"en": "Edit", "sw": "Hariri"},
            "edit_profile": {"en": "Edit Profile", "sw": "Hariri Wasifu"},
            "email": {"en": "Email", "sw": "Barua Pepe"},
            "export": {"en": "Export", "sw": "Hamisha"},
            # ==================== FARMERS ====================
            "farmer": {"en": "Farmer", "sw": "Mkulima"},
            "farmer_name": {"en": "Farmer Name", "sw": "Jina la Mkulima"},
            "farmers": {"en": "Farmers", "sw": "Wakulima"},
            "follow_up": {"en": "Follow-up", "sw": "Ufuatiliaji"},
            "follow_up_default": {
                "en": "Re-evaluate after 7 days",
                "sw": "Tathmini tena baada ya siku 7",
            },
            "full_system_control": {
                "en": "You have full control over the system",
                "sw": "Una udhibiti kamili wa mfumo",
            },
            # ==================== GENERATE REPORT ====================
            "generate_report": {"en": "Generate Report", "sw": "Tengeneza Ripoti"},
            "get_started": {"en": "Get Started", "sw": "Anza"},
            "gray_leaf_spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "gray_leaf_spot_desc": {
                "en": "Rectangular gray lesions causing premature leaf death",
                "sw": "Madoa meusi yenye umbo la mstatili yanayosababisha majani kukauka mapema",
            },
            # ==================== HEALTHY ====================
            "healthy_leaf": {"en": "Healthy Leaf", "sw": "Jani lenye Afya"},
            "healthy_leaf_desc": {
                "en": "No disease symptoms detected",
                "sw": "Hakuna dalili za ugonjwa zilizogunduliwa",
            },
            "helping_farmers": {
                "en": "Helping farmers protect their crops",
                "sw": "Kuwasaidia wakulima kulinda mazao yao",
            },
            "hero_description": {
                "en": "Protect your maize crops with our advanced AI technology. Upload a photo and get instant diagnosis and treatment recommendations.",
                "sw": "Linda mazao yako ya mahindi kwa teknolojia ya AI. Pakia picha na upate utambuzi wa papo hapo.",
            },
            "history": {"en": "History", "sw": "Historia"},
            "home": {"en": "Home", "sw": "Nyumbani"},
            "how_it_works": {"en": "How It Works", "sw": "Jinsi Inavyofanya Kazi"},
            # ==================== ID ====================
            "id": {"en": "ID", "sw": "Kitambulisho"},
            "immediate_action": {
                "en": "Immediate action required",
                "sw": "Hatua ya haraka inahitajika",
            },
            "inactive": {"en": "Inactive", "sw": "Haifanyi kazi"},
            "instant_results": {"en": "Instant Results", "sw": "Matokeo ya Papo hapo"},
            "ip_address": {"en": "IP Address", "sw": "Anwani ya IP"},
            # ==================== LAST LOGIN ====================
            "last_login": {"en": "Last login", "sw": "Mara ya mwisho kuingia"},
            "location": {"en": "Location", "sw": "Mahali"},
            "login": {"en": "Login", "sw": "Ingia"},
            "login_btn": {"en": "Login", "sw": "Ingia"},
            "login_to_account": {
                "en": "Login to your account",
                "sw": "Ingia kwenye akaunti yako",
            },
            "logout": {"en": "Logout", "sw": "Toka"},
            "our_mission": {"en": "Our Mission", "sw": "Dhamira Yetu"},
            "mission_text": {
                "en": "Empower farmers with fast, accurate maize disease diagnosis and practical guidance to protect yields.",
                "sw": "Kuwawezesha wakulima kwa utambuzi wa haraka na sahihi wa magonjwa ya mahindi pamoja na mwongozo wa vitendo kulinda mavuno.",
            },
            "our_vision": {"en": "Our Vision", "sw": "Maono Yetu"},
            "vision_text": {
                "en": "Create a healthier maize ecosystem by making AI-driven disease detection available to every farm.",
                "sw": "Kuunda mazingira bora ya mahindi kwa kufanya utambuzi wa magonjwa kwa kutumia AI upatikane kwa kila shamba.",
            },
            "technology_stack": {"en": "Technology Stack", "sw": "Teknolojia Yetu"},
            "the_problem": {"en": "The Problem", "sw": "Tatizo"},
            "problem_text": {
                "en": "Smallholder farmers often lack access to fast disease diagnosis, leading to crop losses and reduced income.",
                "sw": "Wakulima wadogo mara nyingi hawapati utambuzi wa haraka wa magonjwa, jambo linalosababisha kupoteza mazao na mapato yaliyopunguzwa.",
            },
            "diseases_we_detect": {
                "en": "Diseases We Detect",
                "sw": "Magonjwa Tunayotambua",
            },
            "ready_to_protect": {
                "en": "Ready to Protect Your Crops?",
                "sw": "Tayari Kulinda Mazao Yako?",
            },
            "upload_photo_cta": {
                "en": "Upload a maize leaf photo now and get instant treatment advice.",
                "sw": "Pakia picha ya jani la mahindi sasa na upate ushauri wa matibabu papo hapo.",
            },
            "responsive_ui": {"en": "Responsive UI", "sw": "Muonekano unaojibu"},
            "long_term_prevention": {
                "en": "Long-term Prevention",
                "sw": "Kinga ya Muda Mrefu",
            },
            # ==================== MAIZE DISEASE ====================
            "maize_disease_detection": {
                "en": "Maize Disease Detection",
                "sw": "Utambuzi wa Magonjwa ya Mahindi",
            },
            "maize_disease_system": {
                "en": "Maize Disease Detection System",
                "sw": "Mfumo wa Utambuzi wa Magonjwa ya Mahindi",
            },
            "maize_leaf_only": {
                "en": "Please upload a clear image of a maize leaf",
                "sw": "Tafadhali pakia picha wazi ya jani la mahindi",
            },
            "member_since": {"en": "Member since", "sw": "Amejiunga tangu"},
            "monitoring_frequency": {
                "en": "Monitoring Frequency",
                "sw": "Mara kwa Mara ya Ufuatiliaji",
            },
            "monitoring_schedule": {
                "en": "Monitoring Schedule",
                "sw": "Ratiba ya Ufuatiliaji",
            },
            "my_profile": {"en": "My Profile", "sw": "Wasifu Wangu"},
            # ==================== NAME ====================
            "name": {"en": "Name", "sw": "Jina"},
            "new_analysis": {"en": "New Analysis", "sw": "Uchambuzi Mpya"},
            "new_password": {"en": "New Password", "sw": "Nenosiri Jipya"},
            "new_prediction": {"en": "New Prediction", "sw": "Utabiri Mpya"},
            "no_action_plan": {
                "en": "No specific action plan available",
                "sw": "Hakuna mpango maalum wa utekelezaji",
            },
            "no_chemical_treatment": {
                "en": "No chemical treatment information available",
                "sw": "Hakuna taarifa za matibabu ya kemikali",
            },
            "no_organic_treatment": {
                "en": "No organic treatment information available",
                "sw": "Hakuna taarifa za matibabu asilia",
            },
            "no_prevention_info": {
                "en": "No prevention information available",
                "sw": "Hakuna taarifa za kinga",
            },
            "northern_leaf_blight": {
                "en": "Northern Leaf Blight",
                "sw": "Ugonjwa wa Majani wa Kaskazini",
            },
            "northern_leaf_blight_desc": {
                "en": "Long cigar-shaped lesions that reduce photosynthesis",
                "sw": "Madoa marefu yenye umbo la sigara yanayopunguza usanisinuru",
            },
            # ==================== OFFICER ====================
            "officer": {"en": "Officer", "sw": "Afisa"},
            "officer_dashboard": {
                "en": "Officer Dashboard",
                "sw": "Dashibodi ya Afisa",
            },
            "organic_solutions": {"en": "Organic Solutions", "sw": "Suluhisho Asilia"},
            "organic_treatment": {"en": "Organic Treatment", "sw": "Matibabu Asilia"},
            # ==================== PENDING ====================
            "pending": {"en": "Pending", "sw": "Inasubiri"},
            "pending_approvals": {
                "en": "Pending Approvals",
                "sw": "Idhini Zinazosubiri",
            },
            "phone": {"en": "Phone", "sw": "Simu"},
            "powered_by_ai": {
                "en": "Powered by Artificial Intelligence",
                "sw": "Inaendeshwa na Akili Bandia",
            },
            "predict_disease": {"en": "Predict Disease", "sw": "Tabiri Ugonjwa"},
            "prediction_history": {
                "en": "Prediction History",
                "sw": "Historia ya Utabiri",
            },
            "prevention_monitoring": {
                "en": "Prevention & Monitoring",
                "sw": "Kinga na Ufuatiliaji",
            },
            "print": {"en": "Print", "sw": "Chapisha"},
            "profile": {"en": "Profile", "sw": "Wasifu"},
            "profile_photo": {"en": "Profile Photo", "sw": "Picha ya Wasifu"},
            "protect_crop_message": {
                "en": "Early detection saves your harvest. Upload a photo now and get instant diagnosis and treatment recommendations.",
                "sw": "Utambuzi wa mapema huokoa mavuno yako. Pakia picha sasa na upate utambuzi na mapendekezo ya matibabu ya papo hapo.",
            },
            "protect_crop_title": {
                "en": "Protect Your Maize Crop Today!",
                "sw": "Linda Mazao Yako ya Mahindi Leo!",
            },
            # ==================== RECENT PREDICTIONS ====================
            "recent_predictions": {
                "en": "Recent Predictions",
                "sw": "Utabiri wa Hivi Karibuni",
            },
            "refresh": {"en": "Refresh", "sw": "Onyesha Upya"},
            "refresh_data": {"en": "Refresh Data", "sw": "Onyesha Upya Data"},
            "region": {"en": "Region", "sw": "Mkoa"},
            "register": {"en": "Register", "sw": "Jisajili"},
            "registered": {"en": "Registered", "sw": "Aliyesajiliwa"},
            "reject": {"en": "Reject", "sw": "Kataa"},
            "reports": {"en": "Reports", "sw": "Ripoti"},
            "response_deadline": {"en": "Response Deadline", "sw": "Muda wa Kujibu"},
            "retake": {"en": "Retake", "sw": "Piga Tena"},
            "role": {"en": "Role", "sw": "Nafasi"},
            # ==================== SAVE ====================
            "save": {"en": "Save", "sw": "Hifadhi"},
            "save_changes": {"en": "Save Changes", "sw": "Hifadhi Mabadiliko"},
            "save_html": {"en": "Save as HTML", "sw": "Hifadhi kama HTML"},
            "save_text": {"en": "Save as Text", "sw": "Hifadhi kama Maandishi"},
            "scientific_name": {"en": "Scientific Name", "sw": "Jina la Kisayansi"},
            "search": {"en": "Search", "sw": "Tafuta"},
            "search_farmers": {"en": "Search Farmers", "sw": "Tafuta Wakulima"},
            "severity": {"en": "Severity", "sw": "Ukali"},
            "share_information": {"en": "Share Information", "sw": "Shiriki Taarifa"},
            "share_message": {
                "en": "Share this diagnosis report with other farmers or extension officers",
                "sw": "Shiriki ripoti hii ya utambuzi na wakulima wengine au maafisa ugani",
            },
            "share_via_whatsapp": {
                "en": "Share via WhatsApp",
                "sw": "Shiriki kupitia WhatsApp",
            },
            "share_via_sms": {"en": "Share via SMS", "sw": "Shiriki kupitia SMS"},
            "sms": {"en": "SMS", "sw": "SMS"},
            "start_detection": {
                "en": "Start Disease Detection",
                "sw": "Anza Utambuzi wa Ugonjwa",
            },
            "status": {"en": "Status", "sw": "Hali"},
            "step1_desc": {
                "en": "Take a clear photo of the affected maize leaf using your phone camera, or upload an existing image from your gallery.",
                "sw": "Piga picha wazi ya jani la mahindi lililoathirika kwa kamera ya simu yako, au pakia picha iliyopo kwenye nyaraka zako.",
            },
            "step1_title": {"en": "Capture or Upload", "sw": "Piga au Pakia Picha"},
            "step2_desc": {
                "en": "Our advanced AI model analyzes the image and identifies the specific maize disease with high accuracy (95%+).",
                "sw": "Mfano wetu wa AI huchambua picha na kutambua ugonjwa mahususi wa mahindi kwa usahihi wa juu (95%+).",
            },
            "step2_title": {"en": "AI Detection", "sw": "Utambuzi wa AI"},
            "step3_desc": {
                "en": "Receive instant treatment recommendations including chemical, organic, and cultural control methods.",
                "sw": "Pokea mapendekezo ya matibabu ya papo hapo ikiwa ni pamoja na kemikali, asili, na mbinu za kitamaduni.",
            },
            "step3_title": {"en": "Get Recommendations", "sw": "Pata Mapendekezo"},
            "step_by_step": {
                "en": "Step by Step Guide",
                "sw": "Mwongozo wa Hatua kwa Hatua",
            },
            "step_desc": {
                "en": "Three simple steps to protect your maize crop",
                "sw": "Hatua tatu rahisi za kulinda mazao yako ya mahindi",
            },
            "symptoms": {"en": "Symptoms", "sw": "Dalili"},
            # ==================== TAKE PHOTO ====================
            "take_photo": {"en": "Take Photo", "sw": "Piga Picha"},
            "tips": {"en": "Tips", "sw": "Vidokezo"},
            "total_diagnoses": {"en": "Total Diagnoses", "sw": "Jumla ya Uchunguzi"},
            "total_farmers": {"en": "Total Farmers", "sw": "Jumla ya Wakulima"},
            "total_logins": {"en": "Total Logins", "sw": "Jumla ya Kuingia"},
            "total_logouts": {"en": "Total Logouts", "sw": "Jumla ya Kutoka"},
            "total_officers": {"en": "Extension Officers", "sw": "Maafisa Ugani"},
            "total_predictions": {"en": "Total Predictions", "sw": "Jumla ya Utabiri"},
            "total_users": {"en": "Total Users", "sw": "Jumla ya Watumiaji"},
            "treatment": {"en": "Treatment", "sw": "Matibabu"},
            # ==================== UPDATE PASSWORD ====================
            "update_password": {"en": "Update Password", "sw": "Sasisha Nenosiri"},
            "upload_image": {"en": "Upload Image", "sw": "Pakia Picha"},
            "upload_photo": {"en": "Upload Photo", "sw": "Pakia Picha"},
            "user": {"en": "User", "sw": "Mtumiaji"},
            "user_activities": {"en": "User Activities", "sw": "Shughuli za Watumiaji"},
            "user_activity_logs": {
                "en": "User Activity Logs",
                "sw": "Rekodi za Shughuli za Watumiaji",
            },
            "user_reports": {"en": "User Reports", "sw": "Ripoti za Watumiaji"},
            # ==================== VIEW ====================
            "view": {"en": "View", "sw": "Angalia"},
            # ==================== WELCOME ====================
            "welcome_back": {"en": "Welcome back", "sw": "Karibu tena"},
            "welcome_back_officer": {"en": "Welcome back", "sw": "Karibu tena"},
            "welcome_subtitle": {
                "en": "Early Detection for Better Harvest",
                "sw": "Utambuzi wa Mapema kwa Mavuno Bora",
            },
            "welcome_title": {
                "en": "AI-Powered Maize Disease Detection",
                "sw": "Utambuzi wa Magonjwa ya Mahindi kwa AI",
            },
            "weekly_monitoring": {
                "en": "Weekly monitoring recommended",
                "sw": "Ufuatiliaji wa kila wiki unapendekezwa",
            },
            # ==================== YOUR REGION ====================
            "your_region": {"en": "Your Region", "sw": "Mkoa Wako"},
            # ==================== SHARE ADDITIONAL ====================
            "report_saved": {
                "en": "Report saved successfully!",
                "sw": "Ripoti imehifadhiwa!",
            },
            "report_copied": {
                "en": "Report copied to clipboard!",
                "sw": "Ripoti imenakiliwa!",
            },
            "copied": {"en": "Copied!", "sw": "Imenakiliwa!"},
            "no_disease_info": {
                "en": "No disease information available",
                "sw": "Hakuna taarifa za ugonjwa",
            },
            "loading": {"en": "Loading...", "sw": "Inapakia..."},
            "error": {"en": "Error", "sw": "Hitilafu"},
            "success": {"en": "Success", "sw": "Imefaulu"},
            "warning": {"en": "Warning", "sw": "Onyo"},
            "info": {"en": "Information", "sw": "Taarifa"},
            "confirm": {"en": "Confirm", "sw": "Thibitisha"},
            "cancel_action": {"en": "Cancel", "sw": "Ghairi"},
            "delete_confirmation": {
                "en": "Are you sure you want to delete this?",
                "sw": "Je, una uhakika unataka kufuta hii?",
            },
            "approve_confirmation": {
                "en": "Are you sure you want to approve this?",
                "sw": "Je, una uhakika unataka kuidhinisha hii?",
            },
            "reject_confirmation": {
                "en": "Are you sure you want to reject this?",
                "sw": "Je, una uhakika unataka kukataa hii?",
            },
            "upload_success": {"en": "Upload successful!", "sw": "Upakiaji umefaulu!"},
            "upload_failed": {
                "en": "Upload failed. Please try again.",
                "sw": "Upakiaji umeshindwa. Tafadhali jaribu tena.",
            },
            "processing": {"en": "Processing...", "sw": "Inachakata..."},
            "done": {"en": "Done!", "sw": "Imekamilika!"},
            "try_again": {"en": "Try Again", "sw": "Jaribu Tena"},
            "go_back": {"en": "Go Back", "sw": "Rudi Nyuma"},
            "contact_support": {"en": "Contact Support", "sw": "Wasiliana na Msaada"},
            "view_details": {"en": "View Details", "sw": "Angalia Maelezo"},
            "show_more": {"en": "Show More", "sw": "Onyesha Zaidi"},
            "show_less": {"en": "Show Less", "sw": "Onyesha Kidogo"},
            "all": {"en": "All", "sw": "Zote"},
            "none": {"en": "None", "sw": "Hakuna"},
            "select_all": {"en": "Select All", "sw": "Chagua Zote"},
            "deselect_all": {"en": "Deselect All", "sw": "Ondoa Zote"},
            "filter": {"en": "Filter", "sw": "Chuja"},
            "sort": {"en": "Sort", "sw": "Panga"},
            "ascending": {"en": "Ascending", "sw": "Kupanda"},
            "descending": {"en": "Descending", "sw": "Kushuka"},
            "no_results": {
                "en": "No results found",
                "sw": "Hakuna matokeo yaliyopatikana",
            },
            "page": {"en": "Page", "sw": "Ukurasa"},
            "of": {"en": "of", "sw": "ya"},
            "previous": {"en": "Previous", "sw": "Iliyotangulia"},
            "next": {"en": "Next", "sw": "Inayofuata"},
            "first": {"en": "First", "sw": "Ya Kwanza"},
            "last": {"en": "Last", "sw": "Ya Mwisho"},
            # ==================== UPLOAD TIPS ====================
            "upload_clear_image": {
                "en": "Upload a clear image of a maize leaf",
                "sw": "Pakia picha wazi ya jani la mahindi",
            },
            "good_lighting": {
                "en": "Ensure good lighting for accurate results",
                "sw": "Hakikisha mwanga mzuri kwa matokeo sahihi",
            },
            "supported_formats": {
                "en": "Supported formats: PNG, JPG, JPEG, WEBP",
                "sw": "Miundo inayotumika: PNG, JPG, JPEG, WEBP",
            },
            "invalid_file_type": {
                "en": "Please upload a valid image file",
                "sw": "Tafadhali pakia faili sahihi ya picha",
            },
            "file_too_large": {
                "en": "File too large. Max 10MB",
                "sw": "Faili kubwa sana. Upeo 10MB",
            },
            # ==================== DISEASE NAMES ====================
            "blight": {"en": "Blight", "sw": "Ugonjwa wa Majani"},
            "common_rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "gray_leaf_spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "healthy": {"en": "Healthy", "sw": "Afya"},
            # ==================== ADDITIONAL ADMIN/UI STRINGS ====================
            "user_details_label": {"en": "User Details", "sw": "Maelezo ya Mtumiaji"},
            "user_id": {"en": "User ID", "sw": "Kitambulisho cha Mtumiaji"},
            "full_name": {"en": "Full Name", "sw": "Jina Kamili"},
            "phone_number": {"en": "Phone Number", "sw": "Namba ya Simu"},
            "user_id_label": {"en": "User ID:", "sw": "Kitambulisho cha Mtumiaji:"},
            "full_name_label": {"en": "Full Name:", "sw": "Jina Kamili:"},
            "phone_number_label": {"en": "Phone Number:", "sw": "Namba ya Simu:"},
            "email_label": {"en": "Email:", "sw": "Barua Pepe:"},
            "role_label": {"en": "Role:", "sw": "Nafasi:"},
            "location_label": {"en": "Location:", "sw": "Mahali:"},
            "district_label": {"en": "District:", "sw": "Wilaya:"},
            "region_label": {"en": "Region:", "sw": "Mkoa:"},
            "status_label": {"en": "Status:", "sw": "Hali:"},
            "active": {"en": "Active", "sw": "Inayofanya kazi"},
            "inactive_label": {"en": "Inactive", "sw": "Haifanyi kazi"},
            "approved_label": {"en": "Approved:", "sw": "Imeidhinishwa:"},
            "registered_label": {"en": "Registered:", "sw": "Aliyesajiliwa:"},
            "approved_date": {"en": "Approved Date", "sw": "Tarehe ya Kumidhinisha"},
            "last_login_label": {"en": "Last Login:", "sw": "Kuingia kwa Mwisho:"},
            "back_to_dashboard": {
                "en": "Back to Dashboard",
                "sw": "Rudi kwenye Dashibodi",
            },
            "disease_details": {"en": "Disease Details", "sw": "Maelezo ya Ugonjwa"},
            "prediction_details": {
                "en": "Prediction Details",
                "sw": "Maelezo ya Utabiri",
            },
            "print_report": {"en": "Print Report", "sw": "Chapisha Ripoti"},
            "disease_blight": {"en": "Blight", "sw": "Ugonjwa wa Majani"},
            "disease_common_rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "disease_gray_leaf_spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "disease_healthy": {"en": "Healthy", "sw": "Afya"},
            # ==================== SECURITY LOGS ====================
            "system_security_logs": {
                "en": "System Security Logs - Database",
                "sw": "Rekodi za Usalama wa Mfumo",
            },
            "detected_attacks": {
                "en": "Detected Attacks",
                "sw": "Mashambulizi Yaliyogunduliwa",
            },
            "failed_logins": {"en": "Failed Logins", "sw": "Kuingia Kulishindwa"},
            "successful_logins": {
                "en": "Successful Logins",
                "sw": "Kuingia Kulipofaulu",
            },
            "total_events": {"en": "Total Events", "sw": "Jumla ya Matukio"},
            "clear_all_logs": {"en": "Clear All Logs", "sw": "Futa Rekodi Zote"},
            "export_logs": {"en": "Export Logs", "sw": "Hamisha Rekodi"},
            "last_updated_just_now": {
                "en": "Last updated: Just now",
                "sw": "Ilibadilishwa kwa mwisho: Sasa",
            },
            "database_security_logs": {
                "en": "Database Security Logs",
                "sw": "Rekodi za Usalama wa Hifadhidata",
            },
            "security_events": {"en": "Security Events", "sw": "Matukio ya Usalama"},
            "attack_detection": {
                "en": "Attack Detection",
                "sw": "Utambuzi wa Mashambulizi",
            },
            "authentication_label": {"en": "Authentication", "sw": "Uthibitishaji"},
            "access_logs": {"en": "Access Logs", "sw": "Rekodi za Kupata Hadhi"},
            "timestamp": {"en": "Timestamp", "sw": "Muda"},
            "event_type": {"en": "Event Type", "sw": "Aina ya Matukio"},
            "severity": {"en": "Severity", "sw": "Ukali"},
            "ip_address_label": {"en": "IP Address", "sw": "Anwani ya IP"},
            "user_role": {"en": "User Role", "sw": "Nafasi ya Mtumiaji"},
            "loading_security_logs": {
                "en": "Loading security logs...",
                "sw": "Inapakia rekodi za usalama...",
            },
            "loading_attack_logs": {
                "en": "Loading attack logs...",
                "sw": "Inapakia rekodi za mashambulizi...",
            },
            "loading_authentication_logs": {
                "en": "Loading authentication logs...",
                "sw": "Inapakia rekodi za uthibitishaji...",
            },
            "loading_access_logs": {
                "en": "Loading access logs...",
                "sw": "Inapakia rekodi za hadhi...",
            },
            "error_loading_logs": {
                "en": "Error loading logs",
                "sw": "Hitilafu katika kupakia rekodi",
            },
            "no_security_logs_found": {
                "en": "No security logs found",
                "sw": "Hakuna rekodi za usalama",
            },
            "no_auth_logs_found": {
                "en": "No authentication logs found",
                "sw": "Hakuna rekodi za uthibitishaji",
            },
            "no_attacks_detected": {
                "en": "No attacks detected - System is secure!",
                "sw": "Hakuna mashambulizi yaliyogunduliwa - Mfumo ni salama!",
            },
            "no_access_logs_found": {
                "en": "No access logs found",
                "sw": "Hakuna rekodi za hadhi",
            },
            "failed": {"en": "Failed", "sw": "Imeshindwa"},
            "attack_type": {"en": "Attack Type", "sw": "Aina ya Shambulio"},
            "endpoint": {"en": "Endpoint", "sw": "Ncha"},
            "pattern": {"en": "Pattern", "sw": "Mifumo"},
            "event": {"en": "Event", "sw": "Matukio"},
            "username": {"en": "Username", "sw": "Jina la Mtumiaji"},
            "method": {"en": "Method", "sw": "Njia"},
            "response_time": {"en": "Response Time", "sw": "Muda wa Kujibu"},
            # ==================== ERROR PAGES ====================
            "error_500_title": {
                "en": "500 - Internal Server Error",
                "sw": "500 - Hitilafu ya Mfumo wa Ndani",
            },
            "internal_server_error": {
                "en": "Internal Server Error",
                "sw": "Hitilafu ya Mfumo wa Ndani",
            },
            "internal_error_message": {
                "en": "Something went wrong on our end. Please try again later.",
                "sw": "Kitu kilienda vibaya katika upande wetu. Tafadhali jaribu tena baadaye.",
            },
            "go_to_homepage": {"en": "Go to Homepage", "sw": "Nenda Ukurasa wa Kwanza"},
            # ==================== FORM LABELS ====================
            "full_name_required": {"en": "Full Name *", "sw": "Jina Kamili *"},
            "phone_number_required": {"en": "Phone Number *", "sw": "Namba ya Simu *"},
            "password_required": {"en": "Password *", "sw": "Nenosiri *"},
            "disease_name_english_required": {
                "en": "Disease Name (English) *",
                "sw": "Jina la Ugonjwa (Kiingereza) *",
            },
            "disease_name_swahili_label": {
                "en": "Disease Name (Swahili)",
                "sw": "Jina la Ugonjwa (Kiswahili)",
            },
            "scientific_name_label": {
                "en": "Scientific Name",
                "sw": "Jina la Kisayansi",
            },
            "description_english": {
                "en": "Description (English)",
                "sw": "Maelezo (Kiingereza)",
            },
            "description_swahili": {
                "en": "Description (Swahili)",
                "sw": "Maelezo (Kiswahili)",
            },
            "symptoms_english": {
                "en": "Symptoms (English)",
                "sw": "Dalili (Kiingereza)",
            },
            "symptoms_swahili": {
                "en": "Symptoms (Swahili)",
                "sw": "Dalili (Kiswahili)",
            },
            "treatment_english": {
                "en": "Treatment (English)",
                "sw": "Matibabu (Kiingereza)",
            },
            "treatment_swahili": {
                "en": "Treatment (Swahili)",
                "sw": "Matibabu (Kiswahili)",
            },
            "active_account": {"en": "Active Account", "sw": "Akaunti Inayofanya Kazi"},
            "email_optional": {"en": "Email (Optional)", "sw": "Barua Pepe (Hiari)"},
            "street_help": {"en": "e.g., Main Street", "sw": "Mfano: Barabara Kuu"},
            "account_type": {"en": "Account Type", "sw": "Aina ya Akaunti"},
            "street": {"en": "Street", "sw": "Barabara"},
            "extension_officer_label": {"en": "Extension Officer", "sw": "Afisa Ugani"},
            "admin_label": {"en": "Admin", "sw": "Msimamizi"},
            # ==================== TECHNOLOGY BADGES ====================
            "tech_python": {"en": "Python", "sw": "Python"},
            "tech_tensorflow": {"en": "TensorFlow", "sw": "TensorFlow"},
            "tech_flask": {"en": "Flask", "sw": "Flask"},
            "tech_bootstrap": {"en": "Bootstrap 5", "sw": "Bootstrap 5"},
            "tech_postgresql": {"en": "PostgreSQL", "sw": "PostgreSQL"},
            "tech_cnn": {"en": "CNN Model", "sw": "Mfano wa CNN"},
            # ==================== MODAL & BUTTON LABELS ====================
            "confirm_details": {"en": "Confirm Details", "sw": "Thibitisha Maelezo"},
            "confirm_register": {"en": "Confirm Register", "sw": "Thibitisha Usajili"},
            "create_account": {"en": "Create Account", "sw": "Tengeneza Akaunti"},
            "have_account": {
                "en": "Already have an account?",
                "sw": "Tayari una akaunti?",
            },
            "login_here": {"en": "Login here", "sw": "Ingia hapa"},
            "or": {"en": "or", "sw": "au"},
            "review_register": {
                "en": "I agree to the Terms and Conditions",
                "sw": "Nakubali Masharti na Hali",
            },
            "review_info": {
                "en": "Please review your information before submitting",
                "sw": "Tafadhali kagua taarifa yako kabla ya kuwasilisha",
            },
            "secure_info": {
                "en": "Your information is secure and encrypted",
                "sw": "Taarifa yako ni salama na imefichwa",
            },
            "officer_warning_title": {"en": "Important:", "sw": "Muhimu:"},
            "officer_warning_text": {
                "en": "Officer registrations require admin approval",
                "sw": "Usajili wa Afisa unahitaji ukubali wa Msimamizi",
            },
            "farmer_info": {
                "en": "Farmers can diagnose plant diseases and access treatment recommendations",
                "sw": "Wakulima wanaweza kusanidi magonjwa ya mimea na kupata mapendekezo ya matibabu",
            },
            "select_or_capture_image_then_predict": {
                "en": "Select or capture an image first, then tap Predict.",
                "sw": "Chagua au kama picha kwanza, kisha bonyeza Tabiri.",
            },
            "retake_photo": {"en": "Retake Photo", "sw": "Piga Picha Tena"},
        }

    def get_text(self, key, language="en"):
        if key in self.translations:
            return self.translations[key].get(
                language, self.translations[key].get("en", key)
            )
        return key

    def get_disease_translation(self, disease_name, language="en"):
        disease_translations = {
            "Blight": {
                "en": "Northern Leaf Blight",
                "sw": "Ugonjwa wa Majani wa Kaskazini",
            },
            "Common_Rust": {"en": "Common Rust", "sw": "Kutu wa Kawaida"},
            "Gray_Leaf_Spot": {"en": "Gray Leaf Spot", "sw": "Madoa Meusi"},
            "Healthy": {"en": "Healthy", "sw": "Afya"},
        }
        if disease_name in disease_translations:
            return disease_translations[disease_name].get(language, disease_name)
        return disease_name


lang_manager = LanguageManager()
