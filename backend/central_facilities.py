"""
central_facilities.py
=====================
Comprehensive data module for HBTU (Harcourt Butler Technical University) Central Facilities.
Extracted from https://hbtu.ac.in (Official University Website)

Source: hbtu.ac.in - Central Facilities section
Last Updated: May 2026

This module contains detailed information about all central facilities available
at HBTU Kanpur for use in chatbot knowledge bases, FAQ systems, and information portals.
"""

# =============================================================================
# UNIVERSITY OVERVIEW
# =============================================================================

UNIVERSITY_INFO = {
    "name": "Harcourt Butler Technical University",
    "abbreviation": "HBTU",
    "former_name": "Harcourt Butler Technological Institute (HBTI)",
    "established": 1921,
    "university_status": "September 01, 2016",
    "location": "Nawabganj, Kanpur - 208002, Uttar Pradesh, India",
    "naac_grade": "A+",
    "campuses": {
        "east_campus": {
            "area_acres": 74,
            "location": "Near CSA University of Agriculture & Technology, Agricultural College Lane",
            "primary_use": "Academic activities, administrative offices, girls hostels, some boys hostels",
            "landmarks_nearby": [
                "CSA University of Agriculture & Technology",
                "GSVM Medical College",
                "Kanpur Zoo",
                "Company Bagh",
                "Rawatpur Railway Station (3 km)",
                "Rawatpur Metro Station (3 km)",
                "Kanpur Central Railway Station (8 km)",
                "Kanpur Central Bus Station (9 km)"
            ]
        },
        "west_campus": {
            "area_acres": 250,
            "location": "Indra Road, opposite Deen Dayal Nagar locality, near Kanpur Zoo",
            "primary_use": "Residential campus, boys hostels, faculty/staff quarters",
            "landmarks_nearby": [
                "Kanpur Zoo",
                "Gurudev Chauraha (1 km)",
                "GT Road"
            ]
        },
        "distance_between_campuses": "Approximately 3 kilometers",
        "inter_campus_transport": "Cycle facility available for mobility between campuses"
    },
    "vision": "To achieve excellence in technical education, research and innovation",
    "mission": [
        "To promote studies, research & innovation in engineering areas of higher education",
        "To enhance skill development through continuing education programmes",
        "To achieve excellence in higher technical education"
    ],
    "contact": {
        "phone": "+91-0512-2534001-5, 2533812",
        "email": "vc@hbtu.ac.in",
        "website": "https://hbtu.ac.in"
    }
}


# =============================================================================
# CENTRAL FACILITIES - MASTER LIST
# =============================================================================

CENTRAL_FACILITIES = {
    "academic_support": [
        "Centre of Excellence",
        "Central Workshop",
        "Computer Centre",
        "Central Library (Tagore Central Library)",
        "IT Cell",
        "MOOCs Recording Studio",
        "Central Store and Purchase"
    ],
    "student_welfare": [
        "Hostel Facility",
        "Guest House",
        "Post Office",
        "Gymnasium/Sport",
        "Bank",
        "Auditorium/Canteen",
        "Health Centre"
    ],
    "research_innovation": [
        "Incubation Centre (Atal Incubation Hub)",
        "Centre of Excellence",
        "Central Instrumentation Centre",
        "Animal House/Green House",
        "Museum",
        "Media Laboratory/Studios",
        "Business Lab",
        "Research/Statistical Databases",
        "Mootcourt",
        "Theatre",
        "Art Gallery"
    ],
    "infrastructure": [
        "Maintenance",
        "Central Workshop",
        "IT Cell"
    ]
}


# =============================================================================
# 1. CENTRE OF EXCELLENCE
# =============================================================================

CENTRE_OF_EXCELLENCE = {
    "name": "Centre of Excellence on Applied Research, Training and Education in Lipid Science",
    "department": "Department of Oil Technology",
    "established_under": "TEQIP-II project of World Bank",
    "location": "East Campus, HBTU Kanpur",
    "thematic_areas": [
        "Oleo-chemicals and advanced oil processing technologies",
        "Novel surfactants, eco-efficient soaps and detergents",
        "Renewable feedstock based technologies for lubricants and fuels",
        "Nutraceuticals, bioactive compounds",
        "Eco-efficient polymers and coatings"
    ],
    "key_activities_completed": [
        "National Workshop on 'Advances in Oil Processing' (Sept 28-29, 2013)",
        "National Workshop on 'Advances in Soaps and Detergents' (Mar 27-28, 2014)",
        "National Workshop on 'Innovative Techniques in Vegetable Oil Processing' (Sept 27-28, 2014)",
        "National Conference on 'Newer Oleochemicals: Production and Industrial Applications' (Jan 10-11, 2015)",
        "National Workshop on 'Opportunities and Challenges in Biofuels and Biolubricant' (Nov 21-22, 2015)",
        "Practical Training for 'Manufacturing Cosmetic Products' (May 30 - June 04, 2016)",
        "Practical Training for 'Making low cost plastic products' (July 04-09, 2016)",
        "Practical Training for 'Manufacturing Low cost paints from indigenous cheap raw materials' (July 27 - Aug 01, 2016)",
        "Faculty Development Program on 'Corrosion Control in Chemical and Allied Industries' (Aug 22-27, 2016)",
        "10 expert lectures organized from industry professionals",
        "Industry-Institute-Interaction Meet (Aug 27, 2016)",
        "Industrial Trainings for faculty of Oil Technology, Paint Technology and Plastic Technology",
        "Scholarships provided to research scholars in thematic area"
    ],
    "laboratories": {
        "advance_surfactant_lab": {
            "equipment": [
                "UV-Visible Spectrophotometer",
                "FT-IR Spectrophotometer",
                "GC-MS Spectrometer",
                "Atomic Bomb Calorimeter",
                "Differential Scanning Calorimeter",
                "Thermogravimetric Analyzer",
                "Glossmeter",
                "Multi-fuel Analyzer",
                "Surface Tensiometer",
                "Rheometer",
                "Lovibond Tintometer",
                "High Performance Liquid Chromatograph (HPLC)"
            ]
        },
        "knowledge_resource_center": {
            "resources": [
                "60 hard bound books on thematic area",
                "E-books collection",
                "20 desktop computers",
                "Software: MATLAB, Design Expert, STATISTICA, Origin Pro"
            ]
        }
    },
    "industry_collaborations_mou": [
        "M/s Ruchi Soya Industries Ltd., Mumbai",
        "M/s FARELABS, Gurgaon",
        "M/s Mineral Oil Corporation, Kanpur",
        "M/s MILINDIA Ltd., Noida"
    ],
    "future_plans": [
        "Environment and Energy",
        "Construction Technology",
        "Automation and Robotics",
        "Artificial Intelligence and Machine Learning",
        "VLSI Design",
        "Chemical Technology Centre",
        "Electrical Vehicle and Machines",
        "Simulation and Modeling"
    ]
}


# =============================================================================
# 2. CENTRAL WORKSHOP
# =============================================================================

CENTRAL_WORKSHOP = {
    "name": "Central Workshop",
    "location": "East Campus (established 1957)",
    "purpose": "For inculcating various practical skills in students through hands-on training",
    "shops": [
        {
            "name": "Machining Shop",
            "description": "Machine tools and operations training"
        },
        {
            "name": "Carpentry Shop",
            "practices": [
                "Prepare half lap corner joint from given pieces of mango wood",
                "Prepare mortise and Tenon joint from given pieces of mango wood"
            ],
            "instructions": "Description and demonstration of different tools, joints along with advanced Carpentry joints, classification and definition of timber, wood seasoning, demonstration of wood working lathe and advanced power tools used in carpentry work, safety precaution during actual working."
        },
        {
            "name": "Fitting and Bench Working Shop",
            "practices": [
                "Prepare male-female joint from given pieces of mild steel",
                "Prepare practice work piece involving marking, measuring, sawing, drilling and tapping operations"
            ],
            "instructions": "Classification and description of different tools used in fitting shop e.g. marking and measuring tools, holding and supporting tools, striking tools and cutting tools etc, safety precaution during actual working."
        },
        {
            "name": "Blacksmithy Shop",
            "practices": [
                "Prepare 'L' shape job from given piece of mild steel rod by hand forging",
                "Prepare a 'Ring' from given piece of mild steel rod by hand forging"
            ],
            "instructions": "Description of various forging processes done in black-smithy work e.g. upsetting, drawing down, punching, bending, fullering etc, classification and description of different tools, equipment used in black smithy shop, safety precaution during actual working."
        },
        {
            "name": "Foundry Shop",
            "description": "Casting and molding operations"
        },
        {
            "name": "Welding Shop",
            "description": "Welding techniques and joint preparation"
        },
        {
            "name": "Sheet Metal Shop",
            "description": "Sheet metal fabrication and forming"
        }
    ],
    "historical_note": "Once also had a state-of-the-art industrial-grade oil mill, a sugar plant, a soap-factory, and manufacturing machines for paint and varnish.",
    "modern_equipment": [
        "CNC Machines"
    ],
    "key_personnel": "Workshop Superintendent"
}


# =============================================================================
# 3. COMPUTER CENTRE
# =============================================================================

COMPUTER_CENTRE = {
    "name": "Computer Centre",
    "location": "East Campus, HBTU Kanpur",
    "purpose": "Catering to computing needs of faculty, staff and students for research and teaching",
    "infrastructure": {
        "computers": "Around 150 computers connected into LAN",
        "servers": "State-of-the-art servers (high-end Linux and Windows)",
        "labs": "High-end Linux and Windows labs with application software",
        "network": {
            "type": "Institute-wide fiber optic network",
            "bandwidth": "200 Mbps (1:1)",
            "topology": "Tree topology",
            "core_switch": "Cisco Layer 3 10 Gbps (Q2) Core switch",
            "firewall": "Sophos XGS 4500 firewall",
            "backup": "Backup RF connection for OFC media outage",
            "power_backup": "Dedicated 5 KVA Online UPS"
        },
        "internet": {
            "primary": "200 Mbps dedicated Multi Internet link via BSNL fiber leased line",
            "backup": "RF connection setup",
            "ethernet_cards": "10/100/1000 Mbps on all systems (servers & clients)"
        }
    },
    "connectivity": {
        "connected_areas": [
            "All academic departments",
            "Library",
            "All hostels",
            "Residences",
            "Other central facilities"
        ]
    },
    "wi_fi_facility": {
        "availability": "Available at all Hostels, Academic buildings, Smart classrooms, Workshops, Library and Administrative building",
        "support": "24x7 helpline for users to resolve connectivity issues",
        "bandwidth": "1 Gig bandwidth delivered through Access points installed at all premises",
        "access": "Login available only to registered students and faculty/staff members as per University approved list"
    },
    "services": [
        "Internet access",
        "Programming facilities for all software related laboratories",
        "Research computing support",
        "Teaching computing support"
    ]
}


# =============================================================================
# 4. CENTRAL LIBRARY (TAGORE CENTRAL LIBRARY)
# =============================================================================

CENTRAL_LIBRARY = {
    "name": "Tagore Central Library",
    "named_after": "Rabindranath Tagore (Nobel Prize for Literature, 1913)",
    "location": "East Campus, independent building",
    "building": "Central air-conditioned library",
    "vision": "To achieve excellence by providing latest information to enhance technical Knowledge so as to use it in research and innovation",
    "mission": [
        "Providing precise information to users of University for developing analytical ability in science and technology",
        "To update users with latest resources to enable students to cope latest challenges in Society",
        "To keep users updated with recent findings of research at global level",
        "To make users acquainted with literature which inculcates spiritual and moral values apart from technical knowledge"
    ],
    "collection": {
        "total_books": 82636,
        "bound_journals": 25482,
        "e_books": 843,
        "total_collection": 108961,
        "national_journals": 16,
        "international_journals": 34,
        "online_resources": [
            "E-resources",
            "Research papers",
            "Articles"
        ]
    },
    "digital_resources": {
        "e_journals_platforms": [
            "ACS (American Chemical Society)",
            "J-Gate",
            "IEEE",
            "Springer Nature",
            "Web of Science database"
        ],
        "e_books_publishers": "Leading publishers",
        "subscriptions": [
            "E-ShodhSindhu (eSS)",
            "NDLI eBooks/archives",
            "ShodhShuddhi PDS system"
        ],
        "anti_plagiarism": [
            "Turnitin (https://www.turnitin.com)",
            "Urkund (https://secure.urkund.com)"
        ],
        "web_opac": "Web-based OPAC catalogue with 83,000+ books and 25,000+ journals & periodicals",
        "mou": "Memorandum of Understanding with Shodhganga of INFLIBNET (UGC body)"
    },
    "j_gate_access": {
        "url": "https://jgateplus.com/home/",
        "instructions": "Login -> my J-Gate -> create new account for remote access under J-Gate package",
        "requirement": "Accessible through HBTU IP range",
        "registration_code": "fCe-9QS-ugn",
        "user_id": "HBTU",
        "password as given"
    },
    "services": [
        "Circulation",
        "Photocopying",
        "Reference services",
        "OPAC (Online Public Access Catalogue)",
        "Open access system",
        "Newspaper reading section"
    ],
    "newspapers_subscribed": [
        "Dainik Jagran (Hindi)",
        "Amar Ujala (Hindi)",
        "Hindustan (Hindi)",
        "Rashtriya Sahara (Hindi)",
        "i-next (Hindi)",
        "Hindustan Times (English)",
        "The Hindu (English)",
        "The Indian Express (English)",
        "The Times of India (English)",
        "The Economic Times (English)",
        "The Financial Express (English)",
        "Employment News",
        "Rojgar Samachar"
    ],
    "timings": {
        "monday_to_friday": "09:30 AM - 09:00 PM",
        "saturday_sunday": "09:30 AM - 07:00 PM"
    },
    "ndli_club": "National Digital Library of India Club active",
    "key_personnel": "Librarian"
}


# =============================================================================
# 5. IT CELL
# =============================================================================

IT_CELL = {
    "name": "IT Cell",
    "purpose": "Managing IT infrastructure, ERP systems, and digital services of the University",
    "responsibilities": [
        "Maintenance and upkeep of all IT facilities in the University",
        "ERP system management (Samarth and HBTU ERP)",
        "Website management",
        "Digital infrastructure support",
        "Network administration"
    ],
    "erp_systems": {
        "samarth": {
            "student_login": "Student Login (Samarth)",
            "employee_login": "Employee Login (Samarth)"
        },
        "hbtu_erp": {
            "student_login": "Student Login (HBTU ERP)",
            "faculty_login": "Faculty Login (HBTU ERP)"
        },
        "other_portals": [
            "Alumni Portal",
            "Endowment Portal",
            "Convocation Portal",
            "Recruitment Portal for Teaching",
            "Recruitment Portal for Non-Teaching",
            "Public Grievance Portal"
        ]
    },
    "key_personnel": "System Manager"
}


# =============================================================================
# 6. CENTRAL STORE AND PURCHASE
# =============================================================================

CENTRAL_STORE_PURCHASE = {
    "name": "Central Store and Purchase",
    "purpose": "Managing procurement, inventory, and supply of goods and materials for the University",
    "functions": [
        "Centralized procurement for all departments",
        "Inventory management",
        "Vendor management",
        "Purchase order processing",
        "Stock verification and auditing"
    ],
    "committees": [
        "Central Purchase Committee"
    ]
}


# =============================================================================
# 7. MOOCs RECORDING STUDIO
# =============================================================================

MOOCS_RECORDING_STUDIO = {
    "name": "MOOCs Recording Studio",
    "location": "East Campus, Main Building",
    "purpose": "Recording and production of Massive Open Online Courses (MOOCs) and digital learning content",
    "facilities": [
        "Professional recording equipment",
        "Video editing suite",
        "Soundproof studio environment"
    ],
    "usage": [
        "Faculty lecture recordings",
        "Online course content creation",
        "Educational video production",
        "Webinar and seminar recordings"
    ]
}


# =============================================================================
# 8. HOSTEL FACILITY
# =============================================================================

HOSTEL_FACILITY = {
    "name": "Hostel Facility",
    "total_hostels": 14,
    "east_campus": {
        "boys_hostels": [
            {
                "name": "Shirdharacharya Hostel",
                "type": "Boys"
            },
            {
                "name": "Ramanujan Hostel",
                "type": "Boys"
            }
        ],
        "girls_hostels": [
            {
                "name": "Alaknanda Hostel",
                "type": "Girls"
            },
            {
                "name": "Mandakini Hostel",
                "type": "Girls"
            },
            {
                "name": "Gangotri Hostel",
                "type": "Girls"
            },
            {
                "name": "Bhagirathi Hostel",
                "type": "Girls"
            },
            {
                "name": "Kaveri Hostel",
                "type": "Girls"
            },
            {
                "name": "Saraswati Hostel",
                "type": "Girls"
            }
        ]
    },
    "west_campus": {
        "boys_hostels": [
            {
                "name": "Abdul Kalam Hostel (WCH-I)",
                "type": "Boys"
            },
            {
                "name": "Visveswaraya Hostel (WCH-II)",
                "type": "Boys"
            },
            {
                "name": "Raman Hostel (WCH-III)",
                "type": "Boys"
            },
            {
                "name": "Ambedkar Hostel (DBRA-I)",
                "type": "Boys"
            },
            {
                "name": "Aryabhatt Hostel (DBRA-II)",
                "type": "Boys"
            },
            {
                "name": "Vishwakarma Hostel (WCH-IV)",
                "type": "Boys"
            }
        ]
    },
    "amenities": [
        "Individual cots",
        "Study tables",
        "Chairs",
        "Wardrobes with locking facility",
        "24 hours power backup",
        "Good drinking water facility",
        "Mess facility",
        "Common room with TV",
        "Lounge",
        "Wi-Fi internet facilities",
        "Security guards on 24x7 basis",
        "Lady guards and lady wardens for girls hostels"
    ],
    "mess_rules": {
        "annual_deposit": "Rs. 36,000.00 per annum",
        "semester_advance": "Rs. 18,000.00 per semester (odd and even)",
        "management": "Run by students under general supervision of Warden",
        "committee": "Executive Committee consisting of elected/nominated student members",
        "account_preparation": "Mess Secretary prepares account within 3 days of month closure",
        "membership": "Mandatory for all inmates (exemption on medical grounds possible)",
        "outsiders": "Not normally allowed; Warden may permit briefly"
    },
    "hostel_rules_summary": [
        "General management by wardens with Hostel Management Committee (HMC)",
        "No noise or vulgar behavior allowed",
        "Unauthorized persons not allowed to stay overnight (09:00 PM to 06:00 AM) without permission",
        "No female guests in boys hostel and vice-versa",
        "No exchange/interchange of hostel/room without Warden consent",
        "Furniture not to be removed from rooms",
        "Mandatory presence in hostel during night (08:00 PM to 06:00 AM)",
        "Heaters/Coolers not allowed; personal computers permitted",
        "No meetings/assembly without Warden permission",
        "No religious or political gatherings in hostels",
        "Mandatory mess membership (medical exemption possible)",
        "Gambling and liquor/drugs strictly prohibited",
        "Firearms and pets not permitted",
        "Vacate hostel during summer vacation",
        "Common room available till 10:00 PM (extended with written permission)",
        "Damaging hostel property punishable with fine"
    ],
    "security": [
        "24x7 security guards",
        "Lady guards for girls hostels",
        "Lady wardens for girls hostels",
        "Faculty mentors",
        "Squad system for security checks"
    ]
}


# =============================================================================
# 9. GUEST HOUSE
# =============================================================================

GUEST_HOUSE = {
    "name": "University Guest House (UGH)",
    "location": "East Campus",
    "purpose": "For visiting faculty, officers, guests, examiners, parents, and designated staff",
    "room_types": [
        {
            "type": "VIP Suites",
            "count": 2
        },
        {
            "type": "Deluxe Rooms",
            "count": 2
        },
        {
            "type": "Air-conditioned Rooms",
            "count": 8,
            "bedding": "Double bedded"
        }
    ],
    "booking": {
        "advance_booking": "Can be booked in advance",
        "on_spot": "Can be booked on spot if vacant",
        "charges": "As laid down by the University",
        "form": "Duly filled UGH registration form forwarded by respective forwarding authority",
        "id_proof": "Guest must produce ID proof upon arrival",
        "contact": {
            "mobile": "7081300575",
            "phone": "0512 2534001-5",
            "email": "guesthouse@hbtu.ac.in"
        }
    },
    "key_personnel": "Sri Akshay Kumar Singh"
}


# =============================================================================
# 10. POST OFFICE
# =============================================================================

POST_OFFICE = {
    "name": "Post Office",
    "location": "West Campus",
    "additional": "Main post office located in Nawabganj area near East Campus",
    "services": [
        "Postal services for faculty, staff, and students",
        "Letter and parcel dispatch",
        "Money order services",
        "Speed post and registered post"
    ],
    "availability": "Available on West Campus; additional postal facility near East Campus"
}


# =============================================================================
# 11. GYMNASIUM / SPORTS
# =============================================================================

GYMNASIUM_SPORTS = {
    "name": "Gymnasium and Sports Facility",
    "gymnasium": {
        "location": "West Campus, near West Campus Hostel-I",
        "equipment": [
            "Treadmills",
            "Cross trainers",
            "Exercise bikes",
            "Exercise balls",
            "Dumbbells",
            "Strength training machines"
        ],
        "usage_rules": [
            "Students must enter name and details in register",
            "Residents free to use all facilities"
        ],
        "supervision": "Physical Education Instructor"
    },
    "sports_grounds": {
        "total": "One Sports Ground each in West and East Campus",
        "west_campus": [
            "Cricket ground (with turf wicket)",
            "Football ground",
            "Hockey ground",
            "Basketball court",
            "Volleyball court"
        ],
        "east_campus": [
            "Badminton court",
            "Lawn tennis court",
            "Basketball court"
        ]
    },
    "outdoor_games": [
        "Athletics",
        "Cricket",
        "Hockey",
        "Football",
        "Lawn Tennis",
        "Volleyball",
        "Basketball",
        "Handball"
    ],
    "indoor_games": [
        "Table Tennis",
        "Badminton",
        "Chess",
        "Gymnastics"
    ],
    "sports_council": {
        "name": "Sports Sub-Council",
        "structure": [
            "Chairman",
            "Convener",
            "Student Secretary & representatives",
            "Support staff"
        ],
        "functions": [
            "Look after various sports activities",
            "Facilitate needs of different sports",
            "Hold competitions and activities throughout the year"
        ]
    },
    "physical_education": {
        "instructor": "Full-time regular Physical Education Instructor",
        "responsibilities": [
            "Coordinating sports and games activities",
            "Training students",
            "Supervising gymnasium"
        ]
    }
}


# =============================================================================
# 12. BANK
# =============================================================================

BANK = {
    "name": "Banking Facility",
    "east_campus": {
        "bank": "Central Bank of India",
        "type": "Full-fledged branch",
        "atm": "ATM facility available"
    },
    "west_campus": {
        "atm": "State Bank of India (SBI) ATM"
    },
    "nearby_atms": [
        "ICICI Bank ATM",
        "HDFC Bank ATM",
        "SBI ATM"
    ],
    "services": [
        "Cash withdrawal",
        "Deposits",
        "Other banking transactions",
        "Easy cash facility for students and staff"
    ]
}


# =============================================================================
# 13. AUDITORIUM / CANTEEN
# =============================================================================

AUDITORIUM_CANTEEN = {
    "auditoriums": {
        "total": "03 well-equipped and IT-enabled auditoriums",
        "capacity": "Maximum 1000 capacity",
        "locations": [
            "Radhakrishnan Auditorium (East Campus)",
            "New Auditorium (East Campus)",
            "Shatabdi Bhawan / Centenary Auditorium (West Campus)"
        ],
        "features": [
            "Air conditioning",
            "Necessary furniture",
            "Projection system",
            "Sound system",
            "Suitable for cultural activities and seminars"
        ]
    },
    "seminar_halls": {
        "availability": "At least one seminar hall in every department",
        "features": [
            "ICT enabled",
            "Projection system",
            "Computer",
            "Internet connectivity"
        ]
    },
    "canteens": {
        "east_campus": [
            {
                "name": "Main Canteen",
                "food_type": "Vegetarian refreshments (snacks, fast food and fixed meals)",
                "timings": "09:00 AM - 09:00 PM"
            },
            {
                "name": "Workshop Canteen",
                "location": "Near workshop",
                "status": "Operational"
            }
        ],
        "west_campus": [
            "Cafeteria available"
        ]
    },
    "other_venues": [
        "Engineering Drawing Halls",
        "Design Centres",
        "Conference rooms",
        "Multi-purpose hall (Shatabdi Bhawan)"
    ]
}


# =============================================================================
# 14. HEALTH CENTRE
# =============================================================================

HEALTH_CENTRE = {
    "name": "Health Centre / Dispensary",
    "location": "East Campus (outdoor patient dispensary); Dispensary also available in West Campus",
    "medical_officer": "Dr. Anusha Shukla, MBBS",
    "additional_staff": [
        {
            "name": "Dr. Arti Pandey",
            "role": "Medical Officer",
            "contact": "+91 9839037500"
        },
        {
            "name": "Dr. Jagveer Singh Saluja",
            "role": "Dentist"
        },
        {
            "name": "Shri Sujeet Kumar",
            "role": "Lab Attendant",
            "contact": "+91 7007754178"
        },
        {
            "name": "Rajeev Kumar Singh",
            "role": "Junior Assistant"
        }
    ],
    "professor_incharge": {
        "name": "Prof. Vandana Dixit Kaushik",
        "email": "vandana@hbtu.ac.in",
        "contact": "+91 9554449900"
    },
    "services": [
        "Routine health checkups for students and staff",
        "Outpatient dispensary services",
        "Prescribed medicines provided if available",
        "Medical camps and awareness programs",
        "Dental services",
        "Ambulance facility",
        "24x7 medical facility availability"
    ],
    "referral": {
        "description": "Complicated cases referred to Medical College/LLRM Hospital for necessary treatment",
        "hospitals": [
            "Medical College Hospital",
            "LLRM Hospital"
        ]
    },
    "medical_insurance": {
        "coverage": "All students covered under medical insurance scheme",
        "purpose": "To take care of medical requirements in insurance-approved hospitals",
        "cashless_mediclaim": "Available for hospitalization expenses"
    },
    "events": [
        "Medical Camps",
        "Health Awareness Programs"
    ]
}


# =============================================================================
# 15. INCUBATION CENTRE (ATAL INCUBATION HUB)
# =============================================================================

INCUBATION_CENTRE = {
    "name": "Incubation Centre / Atal Incubation Hub",
    "location": "East Campus",
    "dean": "Prof. Narendra Kohli, Dean Incubation Hub",
    "purpose": "Promoting entrepreneurship, startup, innovation and incubation",
    "key_features": [
        "Full-fledged Innovation & Incubation Centre under Dean, Incubation Hub",
        "Collaboration with IIT Kanpur for 'National Initiative for Setting up of Design Innovation Centre'",
        "Assistance for faculty, students, and budding entrepreneurs of Kanpur and nearby areas",
        "Organizes motivational events for entrepreneurship"
    ],
    "prototype_areas": [
        {
            "area": "Education",
            "focus": "Learning content for disadvantaged communities"
        },
        {
            "area": "Healthcare",
            "focus": "Assistive technology and designing of low cost medical equipment"
        },
        {
            "area": "Livelihood",
            "focus": "Sustainable agricultural technologies, Precision manufacturing at affordable costs, Appropriate Technology for SMEs and Cottage industry"
        },
        {
            "area": "Environment",
            "focus": "Treatment of water, Health monitoring of environment, Disposal-Segregation and Recycling of waste"
        }
    ],
    "startup_policy_highlights": [
        "Incubation support for students, staff and faculty for mutually acceptable time-frame",
        "Licensing of IPR from University to startup on easy terms (equity/license fees/royalty)",
        "Students allowed to work on innovative projects and setting up startups while studying",
        "Student entrepreneurs may earn credits for working on innovative prototypes/Business Models",
        "Students can use University address to register company with permission",
        "Students allowed to sit for examinations even with less than minimum attendance with permission"
    ],
    "staff": [
        {
            "name": "Smt Manisha Verma",
            "role": "Computer Operator",
            "contact": "7408435834"
        },
        {
            "name": "Shri Roop Chandra Sonkar",
            "role": "Instructor"
        }
    ],
    "related_committee": "Incubation Council"
}


# =============================================================================
# 16. MAINTENANCE
# =============================================================================

MAINTENANCE = {
    "name": "Maintenance Department",
    "sections": [
        {
            "name": "Civil Maintenance",
            "incharge": "Professor In-charge, Civil Maintenance",
            "responsibilities": [
                "All maintenance-related requests by departments, offices, hostels, and residents",
                "Review scope of work, priority, and urgency",
                "Building repairs and upkeep"
            ]
        },
        {
            "name": "Electrical Maintenance",
            "location": "Electrical Maintenance Section Office"
        },
        {
            "name": "Mechanical Maintenance",
            "location": "Mechanical Maintenance Section Building"
        }
    ],
    "hostel_maintenance": [
        "Regular repairing of furniture, doors, windows, fan, lights, water purifiers, and electrical points",
        "Regular cleaning of hostels, washrooms, kitchens, corridors, and surroundings",
        "Cleaning of overhead water tanks, drainage system, and septic tanks on regular basis"
    ],
    "campus_cleanliness": "Cleaning performed daily in the morning before regular classes begin with regular and outsourced staff",
    "annual_stock_checking": "Physical verification of stocks and equipment; auction if not in use or completed useful life",
    "power_supply": "24x7 uninterrupted power supply across campus",
    "key_personnel": [
        "Professor In-charge, Civil Maintenance",
        "System Manager (IT facilities)",
        "Physical Education Instructor (sports facilities)",
        "Professor In-charge, Library (library facilities)",
        "Workshop Superintendent (central workshop facilities)",
        "Hostel Wardens"
    ]
}


# =============================================================================
# ADDITIONAL RESEARCH SUPPORT FACILITIES
# =============================================================================

RESEARCH_SUPPORT_FACILITIES = {
    "central_instrumentation_centre": {
        "name": "Central Instrumentation Centre",
        "purpose": "Sophisticated instrumentation support for research"
    },
    "animal_house_green_house": {
        "name": "Animal House / Green House",
        "purpose": "Research involving biological specimens and plant studies"
    },
    "museum": {
        "name": "Museum",
        "purpose": "Display of historical and educational artifacts"
    },
    "media_laboratory_studios": {
        "name": "Media Laboratory / Studios",
        "purpose": "Media production and digital content creation"
    },
    "business_lab": {
        "name": "Business Lab",
        "purpose": "Business simulation and management training"
    },
    "research_statistical_databases": {
        "name": "Research / Statistical Databases",
        "purpose": "Data analysis and statistical computing support"
    },
    "mootcourt": {
        "name": "Mootcourt",
        "purpose": "Legal practice and mock court sessions"
    },
    "theatre": {
        "name": "Theatre",
        "purpose": "Dramatic arts and cultural performances"
    },
    "art_gallery": {
        "name": "Art Gallery",
        "purpose": "Display of artistic works and exhibitions"
    },
    "food_processing_lab": {
        "name": "Food Processing Laboratory",
        "purpose": "Research and training in food technology"
    },
    "cad_3d_printing_labs": {
        "name": "CAD and 3-D Printing Labs",
        "purpose": "Computer-aided design and additive manufacturing"
    }
}


# =============================================================================
# PROFESSIONAL COMMUNICATIONS LAB
# =============================================================================

PROFESSIONAL_COMMUNICATIONS_LAB = {
    "name": "Professional Communications Lab",
    "department": "Department of Humanities and Social Sciences",
    "purpose": "Specifically designed to cater to special requirements of students to express themselves in a better way",
    "features": [
        "Language learning software",
        "Presentation skills training",
        "Communication enhancement tools"
    ]
}


# =============================================================================
# NATIONAL ORGANIZATIONS HEADQUARTERS ON CAMPUS
# =============================================================================

CAMPUS_ORGANIZATIONS = {
    "east_campus": [
        {
            "name": "Oil Technologists' Association of India (OTAI)",
            "type": "Headquarters"
        },
        {
            "name": "Council of Leather Exports (CLE)",
            "type": "Central Regional Office"
        },
        {
            "name": "Institution of Engineers (India) - Kanpur Local Centre",
            "type": "Local Centre"
        },
        {
            "name": "Indian Institute of Chemical Engineers (IIChE) - Kanpur Regional Centre",
            "type": "Regional Centre"
        },
        {
            "name": "Paint and Coating Technologist Association (PACT)",
            "type": "Headquarters"
        }
    ]
}


# =============================================================================
# STRATEGIC PLAN HIGHLIGHTS (2030 VISION)
# =============================================================================

STRATEGIC_PLAN_2030 = {
    "new_centres_of_excellence": {
        "target": 8,
        "areas": [
            "Environment and Energy",
            "Construction Technology",
            "Automation and Robotics",
            "Artificial Intelligence and Machine Learning",
            "VLSI Design",
            "Chemical Technology Centre",
            "Electrical Vehicle and Machines",
            "Simulation and Modeling"
        ]
    },
    "research_targets": {
        "phd_production": "20 PhD per year, total 200 by 2030",
        "sponsored_projects": "100 by 2030",
        "active_mous": "100 by 2030",
        "iprs": "5 per year, total 50 by 2030",
        "research_papers": "400 per year, total 5000 by 2030"
    },
    "industry_collaboration": {
        "industry_sponsored_labs": "5 (minimum one per school)"
    }
}


# =============================================================================
# GENDER EQUITY FACILITIES
# =============================================================================

GENDER_EQUITY_FACILITIES = {
    "safety_security": [
        "24x7 security guards in all hostels",
        "Lady guards and lady wardens for girl students",
        "Faculty mentors and attendants",
        "Second layer of security personnel throughout campus",
        "Squad system for security checks headed by senior faculty",
        "Separate hostels, badminton court, gymnasium, canteen for girls"
    ],
    "counseling": [
        "Women Counselling Cell / Internal Complaint Committee (ICC)",
        "Sensitive, equitable, fair, timely and confidential handling of complaints"
    ],
    "health": [
        "Health center and ambulance service available 24 hours",
        "Cashless Mediclaim facility for hospitalization expenses"
    ]
}


# =============================================================================
# HELPER FUNCTIONS FOR CHATBOT USE
# =============================================================================

FACILITY_ALIASES = {
    "centre_of_excellence": [
        "centre of excellence", "center of excellence", "coe", "lipid science"
    ],
    "central_workshop": ["central workshop", "workshop", "machining shop", "carpentry shop", "fitting shop"],
    "computer_centre": ["computer centre", "computer center", "computer lab", "computing", "server", "internet lab"],
    "central_library": [
        "central library", "tagore central library", "tagore library", "library",
        "opac", "book", "books", "journals", "e book", "e books", "e-book", "e-books",
        "e journal", "e journals", "j gate", "j-gate", "turnitin"
    ],
    "it_cell": ["it cell", "erp", "samarth", "website", "network", "digital service"],
    "central_store_purchase": ["central store", "central store and purchase", "store and purchase", "purchase"],
    "moocs_recording_studio": ["moocs", "mooc", "recording studio", "moocs recording studio", "studio"],
    "hostel_facility": [
        "hostel", "hostels", "boys hostel", "girls hostel", "mess", "warden",
        "alaknanda", "mandakini", "gangotri", "bhagirathi", "kaveri", "saraswati",
        "ramanujan", "shirdharacharya", "abdul kalam", "visveswaraya", "raman hostel",
        "ambedkar", "aryabhatt", "vishwakarma"
    ],
    "guest_house": ["guest house", "university guest house", "ugh", "guest room", "vip suite"],
    "post_office": ["post office", "postal"],
    "gymnasium_sports": ["gymnasium", "gym", "sports", "sport", "badminton", "cricket", "football", "basketball"],
    "bank": ["bank", "banking", "atm", "sbi", "state bank"],
    "auditorium_canteen": ["auditorium", "canteen", "seminar hall", "lunch", "food court"],
    "health_centre": ["health centre", "health center", "dispensary", "medical", "doctor", "ambulance", "mediclaim"],
    "incubation_centre": ["incubation centre", "incubation center", "atal incubation hub", "startup", "start up", "entrepreneur"],
    "maintenance": ["maintenance", "civil maintenance", "electrical maintenance", "repair"],
    "central_instrumentation_centre": ["central instrumentation centre", "central instrumentation center", "instrumentation"],
    "animal_house_green_house": ["animal house", "green house", "greenhouse"],
    "museum": ["museum"],
    "media_laboratory_studios": ["media laboratory", "media lab", "media studio"],
    "business_lab": ["business lab"],
    "research_statistical_databases": ["research database", "statistical database", "statistical databases"],
    "mootcourt": ["mootcourt", "moot court"],
    "theatre": ["theatre", "theater"],
    "art_gallery": ["art gallery"],
    "food_processing_lab": ["food processing lab", "food processing laboratory"],
    "cad_3d_printing_labs": ["cad lab", "3d printing", "3-d printing", "printing lab"],
    "professional_communications_lab": ["professional communications lab", "communication lab", "language lab"],
    "campus_organizations": ["otai", "cle", "institution of engineers", "iiche", "pact", "campus organization"],
    "gender_equity_facilities": ["gender equity", "women counselling", "women counseling", "icc", "girls safety"],
}


def _facility_catalog() -> dict:
    return {
        "centre_of_excellence": CENTRE_OF_EXCELLENCE,
        "central_workshop": CENTRAL_WORKSHOP,
        "computer_centre": COMPUTER_CENTRE,
        "central_library": CENTRAL_LIBRARY,
        "it_cell": IT_CELL,
        "central_store_purchase": CENTRAL_STORE_PURCHASE,
        "moocs_recording_studio": MOOCS_RECORDING_STUDIO,
        "hostel_facility": HOSTEL_FACILITY,
        "guest_house": GUEST_HOUSE,
        "post_office": POST_OFFICE,
        "gymnasium_sports": GYMNASIUM_SPORTS,
        "bank": BANK,
        "auditorium_canteen": AUDITORIUM_CANTEEN,
        "health_centre": HEALTH_CENTRE,
        "incubation_centre": INCUBATION_CENTRE,
        "maintenance": MAINTENANCE,
        **RESEARCH_SUPPORT_FACILITIES,
        "professional_communications_lab": PROFESSIONAL_COMMUNICATIONS_LAB,
        "campus_organizations": CAMPUS_ORGANIZATIONS,
        "strategic_plan_2030": STRATEGIC_PLAN_2030,
        "gender_equity_facilities": GENDER_EQUITY_FACILITIES,
    }


def _normalize_text(text: str) -> str:
    import re
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").title()


def _redact_sensitive_value(key: str, value):
    if key.lower() in {"password as given", "registration_code", "user_id"}:
        return "Available through authorized HBTU/library access."
    return value


def _format_value(value, level: int = 0, max_items: int = 50) -> list:
    lines = []
    indent = "  " * level

    if isinstance(value, dict):
        for key, item in value.items():
            item = _redact_sensitive_value(key, item)
            title = _humanize_key(key)
            if isinstance(item, (dict, list)):
                lines.append(f"{indent}- **{title}:**")
                lines.extend(_format_value(item, level + 1, max_items=max_items))
            else:
                lines.append(f"{indent}- **{title}:** {item}")
        return lines

    if isinstance(value, list):
        shown = value[:max_items]
        for item in shown:
            if isinstance(item, dict):
                name = item.get("name") or item.get("type")
                if name:
                    lines.append(f"{indent}- **{name}:**")
                    remaining = {k: v for k, v in item.items() if k not in {"name", "type"}}
                    lines.extend(_format_value(remaining, level + 1, max_items=max_items))
                else:
                    lines.extend(_format_value(item, level, max_items=max_items))
            else:
                lines.append(f"{indent}- {item}")
        return lines

    lines.append(f"{indent}- {value}")
    return lines


def _format_facility_response(facility_key: str, data: dict) -> str:
    name = data.get("name", _humanize_key(facility_key)) if isinstance(data, dict) else _humanize_key(facility_key)
    lines = [f"**{name} at HBTU Kanpur**", ""]
    lines.extend(_format_value(data))
    return "\n".join(lines)


def _has_any_query(query: str, phrases: list[str]) -> bool:
    normalized = _normalize_text(query or "")
    padded = f" {normalized} "
    for phrase in phrases:
        phrase_norm = _normalize_text(phrase)
        if phrase_norm and (f" {phrase_norm} " in padded or (len(phrase_norm) > 5 and phrase_norm in normalized)):
            return True
    return False


def _get_nested(data: dict, path: tuple[str, ...]):
    current = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _format_brief_value(label: str, value, max_items: int = 50) -> list[str]:
    if value in (None, "", [], {}):
        return []

    value = _redact_sensitive_value(label, value)
    title = _humanize_key(label)

    if isinstance(value, dict):
        lines = [f"- **{title}:**"]
        shown_items = list(value.items())[:max_items]
        for key, item in shown_items:
            item = _redact_sensitive_value(key, item)
            if isinstance(item, list):
                preview = ", ".join(_compact_list_item(x) for x in item[:max_items])
                lines.append(f"  - **{_humanize_key(key)}:** {preview}")
            elif isinstance(item, dict):
                compact = ", ".join(f"{_humanize_key(k)}: {_redact_sensitive_value(k, v)}" for k, v in list(item.items())[:max_items])
                lines.append(f"  - **{_humanize_key(key)}:** {compact}")
            else:
                lines.append(f"  - **{_humanize_key(key)}:** {item}")
        return lines

    if isinstance(value, list):
        lines = [f"- **{title}:**"]
        for item in value[:max_items]:
            if isinstance(item, dict):
                lines.append(f"  - {_compact_list_item(item)}")
            else:
                lines.append(f"  - {item}")
        return lines

    return [f"- **{title}:** {value}"]


def _compact_list_item(item) -> str:
    if not isinstance(item, dict):
        return str(item)

    name = item.get("name") or item.get("type")
    detail_keys = ["contact", "email", "timings", "location", "status", "food_type", "count", "bedding"]
    details = [
        f"{_humanize_key(key)}: {_redact_sensitive_value(key, item[key])}"
        for key in detail_keys
        if key in item and item[key] not in (None, "", [], {})
    ]
    if name and details:
        return f"{name} ({'; '.join(details)})"
    if name:
        return str(name)
    return ", ".join(
        f"{_humanize_key(k)}: {_redact_sensitive_value(k, v)}"
        for k, v in list(item.items())[:3]
    )


def _format_brief_response(title: str, fields: list[tuple[str, object]]) -> str:
    lines = [f"**{title}**", ""]
    for label, value in fields:
        lines.extend(_format_brief_value(label, value))
    return "\n".join(lines).strip()


def _format_hostel_response(query: str) -> str:
    data = HOSTEL_FACILITY
    east_boys = [h["name"] for h in data["east_campus"]["boys_hostels"]]
    east_girls = [h["name"] for h in data["east_campus"]["girls_hostels"]]
    west_boys = [h["name"] for h in data["west_campus"]["boys_hostels"]]

    if _has_any_query(query, ["list", "names", "which hostel", "hostel name", "boys hostel", "girls hostel"]):
        return _format_brief_response(
            "Hostels at HBTU Kanpur",
            [
                ("total_hostels", data["total_hostels"]),
                ("east_campus_boys_hostels", east_boys),
                ("east_campus_girls_hostels", east_girls),
                ("west_campus_boys_hostels", west_boys),
            ],
        )

    if _has_any_query(query, ["mess", "mess fee", "mess charges", "food"]):
        return _format_brief_response("HBTU Hostel Mess Details", list(data["mess_rules"].items()))

    if _has_any_query(query, ["rule", "rules", "allowed", "not allowed"]):
        return _format_brief_response("HBTU Hostel Rules", [("rules_summary", data["hostel_rules_summary"])])

    return _format_brief_response(
        "Hostel Facility at HBTU Kanpur",
        [
            ("total_hostels", data["total_hostels"]),
            ("east_campus", "Boys and girls hostels are available."),
            ("west_campus", "Boys hostels are available."),
            ("key_amenities", data["amenities"][:6]),
            ("mess_deposit", data["mess_rules"].get("annual_deposit")),
        ],
    )


def _format_library_response(query: str) -> str:
    data = CENTRAL_LIBRARY
    if _has_any_query(query, ["time", "timing", "open", "close", "hours"]):
        return _format_brief_response("Tagore Central Library Timings", list(data["timings"].items()))

    if _has_any_query(query, ["book", "books", "collection", "journal", "journals", "e book", "ebooks"]):
        return _format_brief_response("Tagore Central Library Collection", list(data["collection"].items()))

    if _has_any_query(query, ["opac", "digital", "online", "e journal", "j gate", "j-gate", "turnitin", "plagiarism"]):
        return _format_brief_response(
            "Tagore Central Library Digital Resources",
            [
                ("e_journals_platforms", data["digital_resources"]["e_journals_platforms"]),
                ("subscriptions", data["digital_resources"]["subscriptions"]),
                ("anti_plagiarism", data["digital_resources"]["anti_plagiarism"]),
                ("web_opac", data["digital_resources"]["web_opac"]),
            ],
        )

    return _format_brief_response(
        "Tagore Central Library at HBTU Kanpur",
        [
            ("location", data["location"]),
            ("building", data["building"]),
            ("total_collection", data["collection"]["total_collection"]),
            ("timings", data["timings"]),
            ("services", data["services"]),
        ],
    )


def _format_health_response(query: str) -> str:
    data = HEALTH_CENTRE
    if _has_any_query(query, ["contact", "doctor", "medical officer", "staff", "phone", "number"]):
        return _format_brief_response(
            "HBTU Health Centre Contacts",
            [
                ("medical_officer", data.get("medical_officer")),
                ("professor_incharge", data.get("professor_incharge")),
                ("additional_staff", data.get("additional_staff")),
            ],
        )

    return _format_brief_response(
        "Health Centre at HBTU Kanpur",
        [
            ("location", data.get("location")),
            ("medical_officer", data.get("medical_officer")),
            ("facilities", data.get("facilities")),
            ("services", data.get("services")),
        ],
    )


def _format_bank_response(query: str) -> str:
    data = BANK
    if _has_any_query(query, ["atm", "cash withdrawal", "nearby"]):
        return _format_brief_response(
            "Bank and ATM Facilities at HBTU Kanpur",
            [
                ("east_campus", data.get("east_campus")),
                ("west_campus", data.get("west_campus")),
                ("nearby_atms", data.get("nearby_atms")),
            ],
        )

    return _format_brief_response(
        "Banking Facility at HBTU Kanpur",
        [
            ("east_campus", data.get("east_campus")),
            ("west_campus", data.get("west_campus")),
            ("services", data.get("services")),
        ],
    )


def _format_sports_response(query: str) -> str:
    data = GYMNASIUM_SPORTS
    if _has_any_query(query, ["gym", "gymnasium", "equipment"]):
        return _format_brief_response(
            "Gymnasium Facility at HBTU Kanpur",
            [
                ("location", data["gymnasium"].get("location")),
                ("equipment", data["gymnasium"].get("equipment")),
                ("supervision", data["gymnasium"].get("supervision")),
            ],
        )

    return _format_brief_response(
        "Sports Facilities at HBTU Kanpur",
        [
            ("sports_grounds", data.get("sports_grounds")),
            ("outdoor_games", data.get("outdoor_games")),
            ("indoor_games", data.get("indoor_games")),
        ],
    )


def _format_auditorium_canteen_response(query: str) -> str:
    data = AUDITORIUM_CANTEEN
    if _has_any_query(query, ["canteen", "food", "meal", "snack", "timing", "timings"]):
        return _format_brief_response("Canteen Facilities at HBTU Kanpur", [("canteens", data.get("canteens"))])

    return _format_brief_response(
        "Auditorium and Canteen Facilities at HBTU Kanpur",
        [
            ("auditoriums", data.get("auditoriums")),
            ("seminar_halls", data.get("seminar_halls")),
            ("canteens", data.get("canteens")),
        ],
    )


def _format_facility_response_for_query(facility_key: str, query: str = "") -> str:
    catalog = _facility_catalog()
    data = catalog.get(facility_key, {})
    name = data.get("name", _humanize_key(facility_key)) if isinstance(data, dict) else _humanize_key(facility_key)

    if facility_key == "hostel_facility":
        return _format_hostel_response(query)
    if facility_key == "central_library":
        return _format_library_response(query)
    if facility_key == "health_centre":
        return _format_health_response(query)
    if facility_key == "bank":
        return _format_bank_response(query)
    if facility_key == "gymnasium_sports":
        return _format_sports_response(query)
    if facility_key == "auditorium_canteen":
        return _format_auditorium_canteen_response(query)

    focus_paths = []
    if _has_any_query(query, ["time", "timing", "timings", "open", "close", "hours"]):
        focus_paths = [("timings",), ("working_hours",), ("hours",)]
    elif _has_any_query(query, ["contact", "phone", "mobile", "number", "email", "person", "incharge"]):
        focus_paths = [("contact",), ("contacts",), ("key_personnel",), ("professor_incharge",), ("medical_officer",)]
    elif _has_any_query(query, ["where", "location", "located", "campus"]):
        focus_paths = [("location",), ("locations",), ("east_campus",), ("west_campus",)]
    elif _has_any_query(query, ["charge", "charges", "fee", "fees", "booking", "book room"]):
        focus_paths = [("booking",), ("charges",), ("room_types",)]
    elif _has_any_query(query, ["service", "services", "amenity", "amenities"]):
        focus_paths = [("services",), ("facilities",), ("amenities",), ("responsibilities",)]
    elif _has_any_query(query, ["equipment", "lab", "laboratory", "instrument"]):
        focus_paths = [("equipment",), ("laboratories",), ("labs",), ("facilities",)]

    if focus_paths:
        fields = []
        for path in focus_paths:
            value = _get_nested(data, path)
            if value not in (None, "", [], {}):
                fields.append((_humanize_key(path[-1]), value))
        if fields:
            return _format_brief_response(f"{name} at HBTU Kanpur", fields)

    summary_fields = [
        ("location", data.get("location")),
        ("purpose", data.get("purpose")),
        ("services", data.get("services")),
        ("facilities", data.get("facilities")),
        ("amenities", data.get("amenities")),
        ("timings", data.get("timings")),
        ("contact", data.get("contact")),
    ]
    summary_fields = [(label, value) for label, value in summary_fields if value not in (None, "", [], {})]
    if not summary_fields:
        summary_fields = list(data.items())[:4] if isinstance(data, dict) else [("details", data)]

    return _format_brief_response(f"{name} at HBTU Kanpur", summary_fields[:5])


def detect_central_facilities_intent(message: str):
    """
    Detect central-facility questions.
    Returns (facility_key, confidence). facility_key can be "overview".
    """
    normalized = _normalize_text(message)
    padded = f" {normalized} "

    overview_phrases = [
        "central facilities", "campus facilities", "facilities at hbtu",
        "hbtu facilities", "facilities available", "university facilities",
        "campus infrastructure", "infrastructure at hbtu"
    ]
    if any(f" {_normalize_text(phrase)} " in padded for phrase in overview_phrases):
        return "overview", 1.0

    best_key = None
    best_score = 0
    for facility_key, aliases in FACILITY_ALIASES.items():
        score = 0
        for alias in aliases:
            alias_norm = _normalize_text(alias)
            if alias_norm and f" {alias_norm} " in padded:
                score += 2 if len(alias_norm) > 4 else 1
        if score > best_score:
            best_key = facility_key
            best_score = score

    if best_key:
        return best_key, min(best_score / 2.0, 1.0)

    facility_context = ["facility", "facilities", "campus", "infrastructure", "amenities"]
    if any(f" {word} " in padded for word in facility_context):
        return "overview", 0.5

    return None, 0.0


def get_central_facilities_response(intent: str, user_message: str = "") -> str:
    """Return a chatbot-friendly central facilities answer."""
    catalog = _facility_catalog()

    if intent == "overview" or intent not in catalog:
        lines = [
            "**Central Facilities at HBTU Kanpur**",
            "",
            "HBTU facilities are grouped into these main areas:",
            "",
        ]
        for category, facilities in CENTRAL_FACILITIES.items():
            preview = ", ".join(facilities)
            lines.append(f"- **{_humanize_key(category)}:** {preview}")
        lines.append("")
        lines.append("Ask about one facility, for example: library timings, hostel names, health centre contact, bank/ATM, sports, guest house, computer centre, or incubation centre.")
        return "\n".join(lines).strip()

    return _format_facility_response_for_query(intent, user_message)


def get_facility_info(facility_name: str) -> dict:
    """
    Retrieve detailed information about a specific central facility.
    
    Args:
        facility_name: Name of the facility (case-insensitive, flexible matching)
    
    Returns:
        Dictionary containing facility details or empty dict if not found
    """
    facility_key, confidence = detect_central_facilities_intent(facility_name)
    if facility_key and confidence > 0:
        return _facility_catalog().get(facility_key, {})
    return {}


def get_all_facility_names() -> list:
    """Return a list of all available central facility names."""
    names = []
    for facilities in CENTRAL_FACILITIES.values():
        names.extend(facilities)
    return names


def search_facilities_by_keyword(keyword: str) -> list:
    """
    Search facilities containing the given keyword.
    
    Args:
        keyword: Search term
    
    Returns:
        List of matching facility names
    """
    keyword = keyword.lower()
    matches = []
    
    for key, data in _facility_catalog().items():
        if keyword in str(data).lower():
            matches.append(data.get("name", _humanize_key(key)) if isinstance(data, dict) else _humanize_key(key))
    
    return matches


def get_hostel_details(hostel_name: str = None) -> dict:
    """
    Get details about hostels.
    
    Args:
        hostel_name: Optional specific hostel name
    
    Returns:
        Hostel information dictionary
    """
    if hostel_name:
        all_hostels = (
            HOSTEL_FACILITY["east_campus"]["boys_hostels"] +
            HOSTEL_FACILITY["east_campus"]["girls_hostels"] +
            HOSTEL_FACILITY["west_campus"]["boys_hostels"]
        )
        for hostel in all_hostels:
            if hostel_name.lower() in hostel["name"].lower():
                return hostel
        return {}
    return HOSTEL_FACILITY


def get_library_timings() -> dict:
    """Return library operating hours."""
    return CENTRAL_LIBRARY["timings"]


def get_health_centre_contacts() -> dict:
    """Return health centre contact information."""
    return {
        "medical_officer": HEALTH_CENTRE["medical_officer"],
        "professor_incharge": HEALTH_CENTRE["professor_incharge"],
        "staff": HEALTH_CENTRE["additional_staff"]
    }


# =============================================================================
# MODULE METADATA
# =============================================================================

__version__ = "1.0.0"
__author__ = "HBTU Chatbot Knowledge Base"
__source__ = "https://hbtu.ac.in"
__last_updated__ = "May 2026"
__description__ = "Comprehensive central facilities data for HBTU Kanpur"

if __name__ == "__main__":
    print("HBTU Central Facilities Data Module")
    print(f"Version: {__version__}")
    print(f"Total Facilities: {len(CENTRAL_FACILITIES)}")
    print(f"Source: {__source__}")
    print("\\nAvailable facilities:")
    for category, facilities in CENTRAL_FACILITIES.items():
        print(f"  [{category.upper()}]")
        for facility in facilities:
            print(f"    - {facility}")
