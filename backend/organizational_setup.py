from __future__ import annotations

import re


SOURCE_TITLE = "Organizational Setup of HBTU Kanpur"


ORG_ENTRIES = [
    {
        "id": "chancellor",
        "group": "Top Office",
        "role": "Chancellor",
        "name": "Smt. Anandiben Patel",
        "detail": "Hon'ble Governor, Uttar Pradesh",
        "email": None,
        "contact": None,
        "aliases": ["chancellor", "governor", "honble governor", "hon'ble governor"],
    },
    {
        "id": "vice_chancellor",
        "group": "Top Office",
        "role": "Vice Chancellor",
        "name": "Prof. Samsher",
        "detail": None,
        "email": "vc@hbtu.ac.in",
        "contact": "0512-2534000",
        "aliases": [
            "vice chancellor",
            "vc",
            "kulpati",
            "कुलपति",
        ],
    },
    {
        "id": "pro_vice_chancellor",
        "group": "Top Office",
        "role": "Pro Vice Chancellor",
        "name": "Prof. Dipteek Parmar",
        "detail": None,
        "email": "provc@hbtu.ac.in",
        "contact": "+91-7081300505",
        "aliases": [
            "pro vice chancellor",
            "pro vc",
            "pvc",
            "provc",
            "उप कुलपति",
        ],
    },
    {
        "id": "dean_academic_affairs",
        "group": "Office of Dean of Academic Affairs",
        "role": "Dean Academic Affairs",
        "name": "Prof. Vandana Dixit Kaushik",
        "detail": None,
        "email": "daa@hbtu.ac.in",
        "contact": "9554449900",
        "aliases": [
            "dean academic affairs",
            "dean of academic affairs",
            "daa",
            "academic affairs",
        ],
    },
    {
        "id": "assoc_dean_academic_affairs",
        "group": "Office of Dean of Academic Affairs",
        "role": "Associate Dean Academic Affairs",
        "name": "Dr. Amit Kumar Rathoure",
        "detail": None,
        "email": "arathoure@hbtu.ac.in",
        "contact": "9616428049",
        "aliases": [
            "associate dean academic affairs",
            "assoc dean academic affairs",
            "academic affairs associate dean",
        ],
    },
    {
        "id": "nodal_officer_scholarship",
        "group": "Office of Dean of Academic Affairs",
        "role": "Nodal Officer Scholarship",
        "name": "Dr. Rashi Agarwal",
        "detail": None,
        "email": "rashi@hbtu.ac.in",
        "contact": "+91 9839223922",
        "aliases": ["nodal officer scholarship", "scholarship", "scholarship officer"],
    },
    {
        "id": "assistant_dean_academic_affairs_1",
        "group": "Office of Dean of Academic Affairs",
        "role": "Assistant Dean, Academic Affairs",
        "name": "Dr. Nand Kishore",
        "detail": None,
        "email": "nkishore@hbtu.ac.in",
        "contact": "6392693468",
        "aliases": ["assistant dean academic affairs", "nand kishore"],
    },
    {
        "id": "assistant_dean_academic_affairs_2",
        "group": "Office of Dean of Academic Affairs",
        "role": "Assistant Dean, Academic Affairs",
        "name": "Dr. Rajkamal Kushwaha",
        "detail": None,
        "email": "rajkamal.k@hbtu.ac.in",
        "contact": "7081300606",
        "aliases": ["rajkamal kushwaha", "assistant dean academic affairs"],
    },
    {
        "id": "dean_student_welfare",
        "group": "Office of Dean of Student Welfare",
        "role": "Dean Student Welfare",
        "name": "Dr. Chhagan Lal Gehlot",
        "detail": None,
        "email": "dsw@hbtu.ac.in",
        "contact": "9721456007",
        "aliases": ["dean student welfare", "student welfare", "dsw"],
    },
    {
        "id": "assoc_dean_student_welfare_1",
        "group": "Office of Dean of Student Welfare",
        "role": "Associate Dean Student Welfare",
        "name": "Dr. Anurag Singh",
        "detail": None,
        "email": "a.singh@hbtu.ac.in",
        "contact": "8199990641",
        "aliases": ["anurag singh", "associate dean student welfare"],
    },
    {
        "id": "assoc_dean_student_welfare_2",
        "group": "Office of Dean of Student Welfare",
        "role": "Associate Dean Student Welfare",
        "name": "Dr. Shina Gautam",
        "detail": None,
        "email": "shinaiitd@gmail.com",
        "contact": "9617294626",
        "aliases": ["shina gautam", "associate dean student welfare"],
    },
    {
        "id": "assoc_dean_student_welfare_3",
        "group": "Office of Dean of Student Welfare",
        "role": "Associate Dean Student Welfare",
        "name": "Dr. Dan Bahadur Pal",
        "detail": None,
        "email": "dbpal@hbtu.ac.in",
        "contact": "9336709751",
        "aliases": ["dan bahadur pal", "associate dean student welfare"],
    },
    {
        "id": "registrar",
        "group": "Office of the Registrar",
        "role": "Registrar",
        "name": "Shri Amit Kumar Rathore PCS",
        "detail": None,
        "email": "registrar@hbtu.ac.in",
        "contact": "+91 9721456002",
        "aliases": ["registrar", "kulsachiv", "कुलसचिव"],
    },
    {
        "id": "deputy_registrar_legal",
        "group": "Office of the Registrar",
        "role": "Deputy Registrar (Legal)",
        "name": "Dr. Saurabh Sanghal",
        "detail": None,
        "email": "Saurabh.s@hbtu.ac.in",
        "contact": "+91 9897360294",
        "aliases": ["deputy registrar legal", "legal", "saurabh sanghal"],
    },
    {
        "id": "finance_controller",
        "group": "Finance Office",
        "role": "Finance Controller",
        "name": "Shri. Sahitya Kumar Katiyar",
        "detail": None,
        "email": "fc@hbtu.ac.in",
        "contact": "7081300501",
        "aliases": ["finance controller", "fc", "finance office"],
    },
    {
        "id": "finance_account_officer",
        "group": "Finance Office",
        "role": "Finance & Account Officer",
        "name": "Shri Pranjal Nagayach",
        "detail": None,
        "email": "fao@hbtu.ac.in",
        "contact": "8800962034",
        "aliases": ["finance and account officer", "finance account officer", "fao"],
    },
    {
        "id": "dean_research_development",
        "group": "Dean of Research & Development",
        "role": "Dean, Research & Development",
        "name": "Dr. Rajesh Kumar Verma",
        "detail": None,
        "email": "dord@hbtu.ac.in",
        "contact": "8400444068",
        "aliases": ["research and development", "research & development", "r and d", "dord"],
    },
    {
        "id": "assoc_dean_research_development",
        "group": "Dean of Research & Development",
        "role": "Associate Dean, Research & Development",
        "name": "Dr. Nishant Kumar Singh",
        "detail": None,
        "email": "nsingh@hbtu.ac.in",
        "contact": None,
        "aliases": ["associate dean research", "associate dean r and d", "nishant kumar singh"],
    },
    {
        "id": "asst_dean_research_development",
        "group": "Dean of Research & Development",
        "role": "Asstt. Dean, Research & Development",
        "name": "Dr. Shivam Shreevastava",
        "detail": None,
        "email": "shivam.s@hbtu.ac.in",
        "contact": "8627904993",
        "aliases": ["assistant dean research", "asst dean research", "shivam shreevastava"],
    },
    {
        "id": "dean_planning_resource_generation",
        "group": "Office of Dean of Planning & Resource Generation",
        "role": "Dean Planning & Resource Generation",
        "name": "Prof. Vivek Kumar",
        "detail": None,
        "email": "dprg@hbtu.ac.in",
        "contact": "7081300539",
        "aliases": [
            "planning and resource generation",
            "planning resource generation",
            "dean of planning and resource generation",
            "dean of resource generation",
            "dean of resource",
            "resource generation dean",
            "planning",
            "resource generation",
            "dprg",
        ],
    },
    {
        "id": "assoc_dean_planning_resource_generation",
        "group": "Office of Dean of Planning & Resource Generation",
        "role": "Associate Dean, Planning & Resource Generation",
        "name": "Prof. Anita Yadav",
        "detail": None,
        "email": "ayadav@hbtu.ac.in",
        "contact": "9721456045",
        "aliases": ["associate dean planning", "anita yadav"],
    },
    {
        "id": "prof_training_placement",
        "group": "Office of Dean of Planning & Resource Generation",
        "role": "Professor Training & Placement",
        "name": "Prof. Naveen Kumar Gupta",
        "detail": None,
        "email": "ngupta@hbtu.ac.in",
        "contact": "9557705108",
        "aliases": [
            "training and placement",
            "training placement",
            "placement officer",
            "placement head",
            "placement incharge",
            "placement in-charge",
            "placement in charge",
            "incharge of placement",
            "in-charge of placement",
            "in charge of placement",
            "head of placement",
            "head placement",
            "training and placement officer",
            "training and placement incharge",
            "training and placement in-charge",
            "training and placement in charge",
            "training placement incharge",
            "training placement in-charge",
            "training placement in charge",
            "naveen kumar gupta",
        ],
    },
    {
        "id": "incharge_training_internship",
        "group": "Office of Dean of Planning & Resource Generation",
        "role": "Incharge Training/Internship",
        "name": "Prof. S. K. S. Yadav",
        "detail": None,
        "email": "sksyadav@hbtu.ac.in",
        "contact": "7081300522",
        "aliases": ["training internship", "internship", "sks yadav"],
    },
    {
        "id": "dean_incubation_hub",
        "group": "Dean of Incubation Hub",
        "role": "Dean, Incubation Hub",
        "name": "Prof. Jitendra Bhaskar",
        "detail": None,
        "email": "dih@hbtu.ac.in",
        "contact": "9140824510",
        "aliases": ["incubation hub", "jitendra bhaskar"],
    },
    {
        "id": "assoc_dean_incubation_hub",
        "group": "Dean of Incubation Hub",
        "role": "Associate Dean, Incubation Hub",
        "name": "Dr. Bharat Bhushan Sagar",
        "detail": None,
        "email": "bbsagar@hbtu.ac.in",
        "contact": "9999590179",
        "aliases": ["associate dean incubation", "bharat bhushan sagar"],
    },
    {
        "id": "dean_international_student_affairs",
        "group": "Office of Dean of International Student Affair",
        "role": "Dean, International Student Affairs",
        "name": "Prof. Sanjiv Kumar",
        "detail": None,
        "email": "disa@hbtu.ac.in",
        "contact": "7081300678",
        "aliases": ["international student affairs", "international affairs", "sanjiv kumar", "nri"],
    },
    {
        "id": "assoc_dean_international_student_affairs",
        "group": "Office of Dean of International Student Affair",
        "role": "Associate Dean, International Student Affairs",
        "name": "Dr. Santosh Kumar",
        "detail": None,
        "email": "santoshk@hbtu.ac.in",
        "contact": "6307657521",
        "aliases": ["associate dean international", "santosh kumar"],
    },
    {
        "id": "coordinator_hrd_cell",
        "group": "Coordinator HRD Cell",
        "role": "Coordinator HRD Cell",
        "name": "Prof. Sanjiv Kumar",
        "detail": None,
        "email": "hrdc@hbtu.ac.in",
        "contact": "+91 7081300678",
        "aliases": ["hrd cell", "hrd", "training and placement cell"],
    },
    {
        "id": "incharge_guest_house",
        "group": "Guest House",
        "role": "Incharge Guest House",
        "name": "Sri Akshay Kumar Singh",
        "detail": None,
        "email": "guesthouse@hbtu.ac.in",
        "contact": "+91 7081300578 | 0512-2534001",
        "aliases": [
            "guest house",
            "guesthouse",
            "incharge guest house",
            "incharge of guest house",
            "guest house incharge",
        ],
    },
    {
        "id": "dean_school_engineering",
        "group": "Deans of Schools",
        "office_group": "School of Engineering",
        "role": "Dean, School of Engineering",
        "name": "Prof. Vinay Pratap Singh",
        "detail": None,
        "email": "dsoe@hbtu.ac.in",
        "contact": "+91 9721456084",
        "aliases": ["school of engineering", "dean engineering", "vinay pratap singh"],
    },
    {
        "id": "assoc_dean_school_engineering",
        "group": "Deans of Schools",
        "office_group": "School of Engineering",
        "role": "Associate Dean, School of Engineering",
        "name": "Dr. Nishant Kumar Singh",
        "detail": None,
        "email": "nsingh@hbtu.ac.in",
        "contact": "997582969",
        "aliases": ["associate dean engineering", "nishant kumar singh"],
    },
    {
        "id": "dean_school_chemical_technology",
        "group": "Deans of Schools",
        "office_group": "School of Chemical Technology",
        "role": "Dean School of Chemical Technology",
        "name": "Prof. Praveen Kumar Singh Yadav",
        "detail": None,
        "email": "dsoct@hbtu.ac.in",
        "contact": "7081300577",
        "aliases": ["school of chemical technology", "chemical technology", "dsoct"],
    },
    {
        "id": "assoc_dean_school_chemical_technology",
        "group": "Deans of Schools",
        "office_group": "School of Chemical Technology",
        "role": "Associate Dean, School of Chemical Technology",
        "name": "Dr. Sachin Kumar",
        "detail": None,
        "email": "sachin.kumar@hbtu.ac.in",
        "contact": "99888 64647",
        "aliases": ["sachin kumar", "associate dean chemical technology"],
    },
    {
        "id": "asst_dean_school_chemical_technology",
        "group": "Deans of Schools",
        "office_group": "School of Chemical Technology",
        "role": "Assistant Dean, School of Chemical Technology",
        "name": "Mr. Sanjay Kumar Singh",
        "detail": None,
        "email": "sanjayiitb50@gmail.com",
        "contact": "9807850755",
        "aliases": ["assistant dean chemical technology", "sanjay kumar singh"],
    },
    {
        "id": "dean_school_basic_applied_sciences",
        "group": "Deans of Schools",
        "office_group": "School of Basic & Applied Sciences",
        "role": "Dean School of Basic & Applied Sciences",
        "name": "Dr. Manoj Kumar",
        "detail": None,
        "email": "dsobas@hbtu.ac.in",
        "contact": "+91-7827861662",
        "aliases": ["basic and applied sciences", "basic sciences", "dsobas", "manoj kumar"],
    },
    {
        "id": "dean_school_humanities_social_sciences",
        "group": "Deans of Schools",
        "office_group": "School of Humanities & Social Sciences",
        "role": "Dean, School of Humanities & Social Sciences",
        "name": "Prof. S K Sharma",
        "detail": None,
        "email": "dsohss@hbtu.ac.in",
        "contact": "+91 9721456080",
        "aliases": ["humanities and social sciences", "hss dean", "dsohss", "s k sharma"],
    },
    {
        "id": "dean_school_entrepreneurship_management",
        "group": "Deans of Schools",
        "office_group": "School of Entrepreneurship & Management",
        "role": "Dean, School of Entrepreneurship & Management",
        "name": "Prof. Ram Naresh Tripathi",
        "detail": None,
        "email": "deansoem@hbtu.ac.in",
        "contact": "+91 7081300544",
        "aliases": ["entrepreneurship and management", "management school", "deansoem"],
    },
    {
        "id": "dean_school_pharmaceutical_biological_sciences",
        "group": "Deans of Schools",
        "office_group": "School of Pharmaceutical & Biological Sciences",
        "role": "Dean of School of Pharmaceutical & Biological Sciences",
        "name": "Dr. Lalit Kumar Singh",
        "detail": None,
        "email": None,
        "contact": "7081300565",
        "aliases": ["pharmaceutical and biological sciences", "pharmaceutical sciences", "pbs"],
    },
    {
        "id": "hod_cse",
        "group": "Head of Departments",
        "role": "HoD of Computer Science and Engineering",
        "name": "Dr. Anita Yadav",
        "detail": None,
        "email": "hodcse@hbtu.ac.in",
        "contact": "9721456045",
        "branch_aliases": ["cse", "computer science", "computer science and engineering", "cs", "comp sci", "computer engg"],
        "aliases": ["hod cse", "computer science and engineering", "computer science", "cse hod"],
    },
    {
        "id": "hod_civil",
        "group": "Head of Departments",
        "role": "HoD of Civil Engineering",
        "name": "Dr. Deepesh Singh",
        "detail": None,
        "email": "dsingh@hbtu.ac.in",
        "contact": "7081300521",
        "branch_aliases": ["civil", "civil engineering", "civil engg", "ce"],
        "aliases": ["hod civil", "civil engineering", "civil hod"],
    },
    {
        "id": "hod_electronics",
        "group": "Head of Departments",
        "role": "HoD of Electronics Engineering",
        "name": "Dr. Ashutosh Singh",
        "detail": None,
        "email": "ashutoshs@hbtu.ac.in",
        "contact": "7081300517",
        "branch_aliases": ["electronics", "electronics engineering", "ece", "et", "electronics engg"],
        "aliases": ["hod electronics", "electronics engineering", "ece hod"],
    },
    {
        "id": "hod_electrical",
        "group": "Head of Departments",
        "role": "HoD of Electrical Engineering",
        "name": "Dr. Archana Singh",
        "detail": None,
        "email": "hodee@hbtu.ac.in",
        "contact": "9721456047",
        "branch_aliases": ["electrical", "electrical engineering", "ee", "elec", "electrical engg"],
        "aliases": ["hod electrical", "electrical engineering", "ee hod"],
    },
    {
        "id": "hod_mechanical",
        "group": "Head of Departments",
        "role": "HoD of Mechanical Engineering",
        "name": "Dr. Vinay Pratap Singh",
        "detail": None,
        "email": "hodme@hbtu.ac.in",
        "contact": "9721456084",
        "branch_aliases": ["mechanical", "mechanical engineering", "mech", "me", "mechanical engg"],
        "aliases": ["hod mechanical", "mechanical engineering", "me hod"],
    },
    {
        "id": "hod_management_studies",
        "group": "Head of Departments",
        "role": "HoD of Management Studies",
        "name": "Dr. Asheesh Trivedi",
        "detail": None,
        "email": "hoddoms@hbtu.ac.in",
        "contact": None,
        "branch_aliases": ["management studies", "management", "doms"],
        "aliases": ["hod management studies", "management studies", "doms"],
    },
    {
        "id": "hod_biochemical",
        "group": "Head of Departments",
        "role": "HoD of Biochemical Engineering",
        "name": "Dr. Ajay Kumar Singh",
        "detail": None,
        "email": "aksingh11@hbtu.ac.in",
        "contact": "+91-9935686230",
        "branch_aliases": ["biochemical", "bio chemical", "biochemical engineering", "biochem", "be"],
        "aliases": ["hod biochemical", "biochemical engineering", "biochemical tech", "bio chemical"],
    },
    {
        "id": "hod_chemical",
        "group": "Head of Departments",
        "role": "HoD of Chemical Engineering",
        "name": "Dr. G L Devnani",
        "detail": None,
        "email": "hodch@hbtu.ac.in",
        "contact": "8318694566",
        "branch_aliases": ["chemical", "chemical engineering", "chem", "chemical engg", "che"],
        "aliases": ["hod chemical", "chemical engineering", "chemical tech", "chem hod"],
    },
    {
        "id": "hod_food_technology",
        "group": "Head of Departments",
        "role": "HoD of Food Technology",
        "name": "Dr. Vivek Kumar",
        "detail": None,
        "email": "hodft@hbtu.ac.in",
        "contact": "7081300539",
        "branch_aliases": ["food", "food technology", "food tech", "ft"],
        "aliases": ["hod food", "food technology", "food tech", "hod of food tech"],
    },
    {
        "id": "hod_leather_technology",
        "group": "Head of Departments",
        "role": "HoD of Leather Technology",
        "name": "Dr. G L Devnani",
        "detail": None,
        "email": "hodlt@hbtu.ac.in",
        "contact": "8318694566",
        "branch_aliases": ["leather", "leather technology", "leather tech", "lft", "lt"],
        "aliases": ["hod leather", "leather technology", "leather tech", "lft"],
    },
    {
        "id": "hod_oil_technology",
        "group": "Head of Departments",
        "role": "HoD of Oil Technology",
        "name": "Dr. Praveen Kumar Singh Yadav",
        "detail": None,
        "email": "pksyadav@hbtu.ac.in",
        "contact": "7081300577",
        "branch_aliases": ["oil", "oil technology", "oil tech", "ot"],
        "aliases": ["hod oil", "oil technology", "oil tech", "hod of oil tech"],
    },
    {
        "id": "hod_paint_technology",
        "group": "Head of Departments",
        "role": "HoD of Paint Technology",
        "name": "Dr. Arun Maithani",
        "detail": None,
        "email": "hodpt@hbtu.ac.in",
        "contact": "7081300524",
        "branch_aliases": ["paint", "paint technology", "paint tech", "pt"],
        "aliases": ["hod paint", "paint technology", "paint tech", "paint dept", "paint department"],
    },
    {
        "id": "hod_plastic_technology",
        "group": "Head of Departments",
        "role": "HoD of Plastic Technology",
        "name": "Dr. Praveen Kumar Singh Yadav",
        "detail": None,
        "email": "hodpl@hbtu.ac.in",
        "contact": "7081300577",
        "branch_aliases": ["plastic", "plastic technology", "plastic tech", "pl"],
        "aliases": ["hod plastic", "plastic technology", "plastic tech"],
    },
    {
        "id": "hod_chemistry",
        "group": "Head of Departments",
        "role": "HoD of Chemistry",
        "name": "Dr. Santosh Kumar",
        "detail": None,
        "email": "santoshk@hbtu.ac.in",
        "contact": "6307657521",
        "branch_aliases": ["chemistry", "chem"],
        "aliases": ["hod chemistry", "chemistry hod"],
    },
    {
        "id": "hod_mathematics",
        "group": "Head of Departments",
        "role": "HoD of Mathematics",
        "name": "Dr. Ram Naresh Tripathi",
        "detail": None,
        "email": "hodmath@hbtu.ac.in",
        "contact": "7081300544",
        "branch_aliases": ["mathematics", "maths", "math"],
        "aliases": ["hod mathematics", "mathematics hod"],
    },
    {
        "id": "hod_physics",
        "group": "Head of Departments",
        "role": "HoD of Physics",
        "name": "Dr. Manoj Kumar",
        "detail": None,
        "email": "manoj.k@hbtu.ac.in",
        "contact": "7827861662",
        "branch_aliases": ["physics"],
        "aliases": ["hod physics", "physics hod"],
    },
    {
        "id": "hod_humanities_social_sciences",
        "group": "Head of Departments",
        "role": "HoD of Humanities & Social Sciences",
        "name": "Dr. S.K. Sharma",
        "detail": None,
        "email": "sksharma@hbtu.ac.in",
        "contact": "9721456080",
        "branch_aliases": ["humanities and social sciences", "humanities", "hss"],
        "aliases": ["hod humanities", "humanities and social sciences hod", "hss hod"],
    },
    {
        "id": "hod_pharmaceutical_biological_sciences",
        "group": "Head of Departments",
        "role": "HoD of Pharmaceutical & Biological Sciences",
        "name": "Dr. Lalit Kumar Singh",
        "detail": None,
        "email": "dsopbs@hbtu.ac.in",
        "contact": "7081300565",
        "branch_aliases": [
            "pharmaceutical and biological sciences",
            "pharmaceutical sciences",
            "pharmaceutical",
            "pbs",
            "pharma",
        ],
        "aliases": ["hod pharmaceutical", "pharmaceutical and biological sciences", "pbs hod"],
    },
    {
        "id": "hod_biotechnology",
        "group": "Head of Departments",
        "role": "HoD of Biotechnology",
        "name": "Dr. Lalit Kumar Singh",
        "detail": None,
        "email": "dsopbs@hbtu.ac.in",
        "contact": "7081300565",
        "branch_aliases": ["biotechnology", "biotech"],
        "aliases": ["hod biotechnology", "biotechnology hod", "biotech hod"],
    },
]


OVERVIEW_TRIGGERS = [
    "organizational setup",
    "organization setup",
    "organizational structure",
    "office bearers",
    "full setup",
    "full organizational setup",
    "show all",
    "list all",
    "all offices",
    "entire setup",
    "complete setup",
]

GROUP_ALIASES = {
    "Top Office": [
        "top office",
    ],
    "Office of Dean of Academic Affairs": [
        "office of dean of academic affairs",
        "dean academic affairs office",
        "daa office",
    ],
    "Office of Dean of Student Welfare": [
        "office of dean of student welfare",
        "student welfare office",
        "dsw office",
    ],
    "Office of the Registrar": [
        "office of the registrar",
        "registrar office",
        "office of registrar",
    ],
    "Finance Office": [
        "finance office",
        "fao office",
        "fc office",
    ],
    "Dean of Research & Development": [
        "research and development office",
        "research & development office",
        "rd office",
        "dord office",
    ],
    "Office of Dean of Planning & Resource Generation": [
        "planning and resource generation office",
        "dprg office",
        "training and placement office",
    ],
    "Dean of Incubation Hub": [
        "incubation hub office",
        "dih office",
    ],
    "Office of Dean of International Student Affair": [
        "international student affairs office",
        "international student affair office",
        "disa office",
    ],
    "Coordinator HRD Cell": [
        "hrd cell",
        "hrd office",
    ],
    "Deans of Schools": [
        "deans of schools",
        "school deans",
        "school office",
    ],
    "Head of Departments": [
        "head of departments",
        "hod office",
        "department office",
    ],
}

AMBIGUOUS_TRIGGERS = [
    "official",
    "officials",
    "officer",
    "dean",
    "hod",
    "head of department",
    "vice chancellor",
    "registrar",
    "finance controller",
    "assistant dean",
    "associate dean",
]


def _normalize(text: str) -> str:
    normalized = re.sub(r"\btechs?\b", "technology", (text or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\u0900-\u097f]+", " ", normalized)).strip()


def _has_phrase(message: str, phrases: list[str]) -> bool:
    normalized = _normalize(message)
    return any(_normalize(phrase) in normalized for phrase in phrases)


def _alias_in_text(alias: str, text: str) -> bool:
    alias_norm = _normalize(alias)
    text_norm = _normalize(text)
    if not alias_norm:
        return False
    if len(alias_norm) <= 3 and alias_norm.isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(alias_norm)}(?![a-z0-9])", text_norm) is not None
    return alias_norm in text_norm


def _role_priority(message: str) -> str | None:
    normalized = _normalize(message)
    if _has_phrase(normalized, ["associate dean", "assoc dean", "assoc. dean"]):
        return "associate dean"
    if _has_phrase(normalized, ["assistant dean", "asst dean", "asstt dean", "asst. dean"]):
        return "assistant dean"
    if _has_phrase(normalized, ["pro vice chancellor", "pro vc", "pvc", "provc"]):
        return "pro vice chancellor"
    if _has_phrase(normalized, ["vice chancellor", "vc"]):
        return "vice chancellor"
    if _has_phrase(normalized, ["head of department", "hod"]):
        return "hod"
    if _has_phrase(normalized, ["finance controller", "fao", "finance and account officer"]):
        return "finance"
    if _has_phrase(normalized, ["dean"]):
        return "dean"
    return None


def _is_overview_query(message: str) -> bool:
    normalized = _normalize(message)
    return any(term in normalized for term in OVERVIEW_TRIGGERS)


def _entry_matches(message: str, entry: dict) -> bool:
    normalized = _normalize(message)
    for alias in entry.get("aliases", []):
        if _alias_in_text(alias, normalized):
            return True
    return False


def _entry_scope(entry: dict) -> str:
    return entry.get("office_group") or entry.get("group") or ""


def _detect_group_request(message: str) -> str | None:
    normalized = _normalize(message)
    for group_name, aliases in GROUP_ALIASES.items():
        if any(_alias_in_text(alias, normalized) for alias in aliases):
            return group_name
    return None


def _detect_hod_branch_entry(message: str) -> dict | None:
    normalized = _normalize(message)
    if not _has_phrase(normalized, ["hod", "head of", "head of department", "head of departments"]):
        return None

    candidates: list[dict] = []
    for entry in ORG_ENTRIES:
        if not entry.get("id", "").startswith("hod_"):
            continue
        branch_aliases = entry.get("branch_aliases", [])
        if any(_alias_in_text(alias, normalized) for alias in branch_aliases):
            candidates.append(entry)

    if not candidates:
        return None

    candidates.sort(key=lambda entry: len(entry.get("branch_aliases", [])), reverse=True)
    return candidates[0]


def _is_office_related_query(message: str) -> bool:
    normalized = _normalize(message)
    if any(term in normalized for term in AMBIGUOUS_TRIGGERS):
        return True
    office_cues = [
        "office",
        "department",
        "dean of",
        "associate dean",
        "assistant dean",
        "hod",
        "head of department",
        "vice chancellor",
        "pro vice chancellor",
        "registrar",
        "finance controller",
        "finance officer",
        "student welfare",
        "academic affairs",
        "planning and resource generation",
        "research and development",
        "incubation hub",
        "international student affairs",
        "school of",
        "humanities and social sciences",
    ]
    return any(cue in normalized for cue in office_cues)


def _is_group_list_request(message: str) -> bool:
    normalized = _normalize(message)
    group_cues = [
        "office of",
        "all staff",
        "all members",
        "all people",
        "full office",
        "entire office",
        "list staff",
        "list members",
        "show staff",
        "show members",
        "who are in the office",
        "who works in",
        "members of",
        "staff of",
    ]
    return any(cue in normalized for cue in group_cues)


def detect_organizational_setup_query(user_message: str) -> bool:
    if not user_message:
        return False
    if _is_overview_query(user_message):
        return True
    normalized = _normalize(user_message)
    if _detect_group_request(normalized):
        return True
    if _detect_hod_branch_entry(normalized):
        return True
    if any(term in normalized for term in AMBIGUOUS_TRIGGERS):
        return True
    return any(_entry_matches(user_message, entry) for entry in ORG_ENTRIES)


def _score_entry(message: str, entry: dict) -> int:
    normalized = _normalize(message)
    score = 0
    for alias in entry.get("aliases", []):
        alias_norm = _normalize(alias)
        if not alias_norm:
            continue
        if _alias_in_text(alias_norm, normalized):
            score += len(alias_norm.split())
    if entry.get("group") and _normalize(entry["group"]) in normalized:
        score += 3
    if entry.get("office_group") and _normalize(entry["office_group"]) in normalized:
        score += 6
    if entry.get("role") and _normalize(entry["role"]) in normalized:
        score += 6
    if entry.get("name") and _normalize(entry["name"]) in normalized:
        score += 8
    priority = _role_priority(message)
    role_text = _normalize(entry.get("role", ""))
    if priority == "associate dean":
        if "associate dean" in role_text or "assoc dean" in role_text:
            score += 12
        elif "dean" in role_text:
            score -= 8
    elif priority == "assistant dean":
        if "assistant dean" in role_text or "asst" in role_text:
            score += 12
        elif "dean" in role_text:
            score -= 8
    elif priority == "vice chancellor":
        if "vice chancellor" in role_text:
            score += 12
    elif priority == "pro vice chancellor":
        if "pro vice chancellor" in role_text:
            score += 12
    elif priority == "hod":
        if "hod" in role_text:
            score += 10
    elif priority == "finance":
        if "finance" in role_text:
            score += 10
    elif priority == "dean":
        if role_text.startswith("dean"):
            score += 5
    return score


def _best_matches(user_message: str) -> list[dict]:
    scored = []
    priority = _role_priority(user_message)
    for entry in ORG_ENTRIES:
        score = _score_entry(user_message, entry)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return []

    if priority in {"associate dean", "assistant dean", "pro vice chancellor", "vice chancellor", "hod", "finance"}:
        preferred = []
        for score, entry in scored:
            role_text = _normalize(entry.get("role", ""))
            if priority == "associate dean" and ("associate dean" in role_text or "assoc dean" in role_text):
                preferred.append((score + 50, entry))
            elif priority == "assistant dean" and ("assistant dean" in role_text or "asst" in role_text):
                preferred.append((score + 50, entry))
            elif priority == "pro vice chancellor" and "pro vice chancellor" in role_text:
                preferred.append((score + 50, entry))
            elif priority == "vice chancellor" and "vice chancellor" in role_text:
                preferred.append((score + 50, entry))
            elif priority == "hod" and "hod" in role_text:
                preferred.append((score + 50, entry))
            elif priority == "finance" and "finance" in role_text:
                preferred.append((score + 50, entry))
        if preferred:
            scored = preferred

    scored.sort(key=lambda item: (item[0], len(item[1]["role"])), reverse=True)
    best_score = scored[0][0]
    return [entry for score, entry in scored if score == best_score]


def _format_entry(entry: dict) -> str:
    parts = [f"**{entry['role']}** - {entry['name']}"]
    if entry.get("detail"):
        parts.append(f"  - {entry['detail']}")
    if entry.get("email"):
        parts.append(f"  - Email: {entry['email']}")
    if entry.get("contact"):
        parts.append(f"  - Contact: {entry['contact']}")
    return "\n".join(parts)


def _group_entries(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        grouped.setdefault(_entry_scope(entry), []).append(entry)
    return grouped


def _overview_message() -> str:
    grouped = _group_entries(ORG_ENTRIES)
    sections = ["## HBTU Organizational Setup", f"Source: {SOURCE_TITLE}", ""]
    for group_name in [
        "Top Office",
        "Office of Dean of Academic Affairs",
        "Office of Dean of Student Welfare",
        "Office of the Registrar",
        "Finance Office",
        "Dean of Research & Development",
        "Office of Dean of Planning & Resource Generation",
        "Dean of Incubation Hub",
        "Office of Dean of International Student Affair",
        "Coordinator HRD Cell",
        "School of Engineering",
        "School of Chemical Technology",
        "School of Basic & Applied Sciences",
        "School of Humanities & Social Sciences",
        "School of Entrepreneurship & Management",
        "School of Pharmaceutical & Biological Sciences",
        "Head of Departments",
    ]:
        if group_name not in grouped:
            continue
        sections.append(f"### {group_name}")
        for entry in grouped[group_name]:
            sections.append(f"- {entry['role']}: {entry['name']}")
        sections.append("")
    return "\n".join(sections).strip()


def _build_specific_message(matches: list[dict]) -> str:
    grouped = _group_entries(matches)
    sections = ["## HBTU Organizational Setup", f"Source: {SOURCE_TITLE}", ""]
    for group_name, group_entries in grouped.items():
        sections.append(f"### {group_name}")
        for entry in group_entries:
            sections.append(_format_entry(entry))
        sections.append("")
    return "\n".join(sections).strip()


def get_organizational_setup_response(user_message: str) -> dict:
    normalized = _normalize(user_message)
    overview_requested = _is_overview_query(user_message)
    group_requested = _detect_group_request(normalized)
    priority = _role_priority(user_message)
    hod_entry = _detect_hod_branch_entry(normalized)
    matches = _best_matches(user_message)

    if overview_requested:
        matches = ORG_ENTRIES
    elif group_requested:
        matches = [entry for entry in ORG_ENTRIES if _entry_scope(entry) == group_requested]
    elif hod_entry:
        matches = [hod_entry]
    elif matches and _is_group_list_request(normalized) and priority != "hod":
        group_name = _entry_scope(matches[0])
        matches = [entry for entry in ORG_ENTRIES if _entry_scope(entry) == group_name]

    if not matches:
        return {
            "message": (
                "I can help with a specific HBTU official, but I need the exact office or department.\n\n"
                "Try asking for one person at a time, for example:\n"
                "- Vice Chancellor\n"
                "- Registrar\n"
                "- Dean Academic Affairs\n"
                "- HoD of Oil Technology"
            ),
            "data": {
                "source": SOURCE_TITLE,
                "ambiguous": True,
            },
            "actions": [
                {"label": "Vice Chancellor", "value": "Who is the Vice Chancellor of HBTU?"},
                {"label": "Registrar", "value": "Who is the Registrar of HBTU?"},
                {"label": "Dean Academic Affairs", "value": "Who is the Dean of Academic Affairs?"},
                {"label": "HoD Oil Tech", "value": "Who is the HoD of Oil Tech?"},
            ],
            "suggestions": [
                "Who is the Dean of Student Welfare?",
                "Who is the HoD of Mechanical Engineering?",
                "Who is the Finance Controller?",
            ],
        }

    if overview_requested:
        message = _overview_message()
    else:
        if not group_requested and not hod_entry and not (_is_group_list_request(normalized) and priority != "hod"):
            matches = matches[:1]
        message = _build_specific_message(matches)

    return {
        "message": message,
        "data": {
            "source": SOURCE_TITLE,
            "matches": [
                {
                    "group": entry["group"],
                    "role": entry["role"],
                    "name": entry["name"],
                    "email": entry.get("email"),
                    "contact": entry.get("contact"),
                }
                for entry in matches
            ],
        },
        "actions": [
            {"label": "Vice Chancellor", "value": "Who is the Vice Chancellor of HBTU?"},
            {"label": "Registrar", "value": "Who is the Registrar of HBTU?"},
            {"label": "Dean Academic Affairs", "value": "Who is the Dean of Academic Affairs?"},
            {"label": "HoD CSE", "value": "Who is the HoD of Computer Science and Engineering?"},
        ],
        "suggestions": [
            "Who is the Finance Controller?",
            "Who is the Dean of Student Welfare?",
            "Who is the HoD of Mechanical Engineering?",
            "Show the full organizational setup of HBTU",
        ],
    }
