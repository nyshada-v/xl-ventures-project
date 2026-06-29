"""Realistic mock responses for every tool. Active when MOCK_MODE=true."""

MOCK_TRIGGER_EVENTS = [
    {
        "company_name": "Meridian Health Systems",
        "domain": "meridianhealth.com",
        "signal": "Hired new CHRO — Sarah Chen appointed Chief HR Officer",
        "source": "news",
        "published_at": "2024-12-01",
    },
    {
        "company_name": "Vantage Logistics",
        "domain": "vantagelogistics.io",
        "signal": "Series B $45M raised — expanding headcount by 200",
        "source": "news",
        "published_at": "2024-11-28",
    },
    {
        "company_name": "ClearPath Fintech",
        "domain": "clearpathfintech.com",
        "signal": "Job posting: Head of People Operations",
        "source": "jobs",
        "published_at": "2024-11-30",
    },
]

MOCK_COMPANY_DATA = {
    "meridianhealth.com": {
        "name": "Meridian Health Systems",
        "industry": "Healthtech",
        "headcount": 320,
        "funding_stage": "Series B",
        "country": "US",
        "description": "Digital health platform modernising care coordination.",
        "tech_stack": ["ADP", "Workday"],
        "linkedin_url": "https://linkedin.com/company/meridian-health",
    },
    "vantagelogistics.io": {
        "name": "Vantage Logistics",
        "industry": "SaaS",
        "headcount": 180,
        "funding_stage": "Series B",
        "country": "US",
        "description": "AI-powered freight management for mid-market shippers.",
        "tech_stack": ["Paychex", "BambooHR"],
        "linkedin_url": "https://linkedin.com/company/vantage-logistics",
    },
    "clearpathfintech.com": {
        "name": "ClearPath Fintech",
        "industry": "Fintech",
        "headcount": 95,
        "funding_stage": "Series A",
        "country": "US",
        "description": "Embedded finance APIs for SMB banking.",
        "tech_stack": ["Gusto"],
        "linkedin_url": "https://linkedin.com/company/clearpath-fintech",
    },
}

MOCK_CONTACTS = {
    "meridianhealth.com": [
        {
            "name": "Sarah Chen",
            "title": "Chief HR Officer",
            "email": "s.chen@meridianhealth.com",
            "phone": "+1-415-555-0101",
            "linkedin": "linkedin.com/in/sarahchen-chro",
            "seniority": "c-suite",
        },
        {
            "name": "James Okafor",
            "title": "VP People Operations",
            "email": "j.okafor@meridianhealth.com",
            "phone": "+1-415-555-0102",
            "linkedin": "linkedin.com/in/jamesokafor",
            "seniority": "vp",
        },
    ],
    "vantagelogistics.io": [
        {
            "name": "Priya Nair",
            "title": "Head of HR",
            "email": "p.nair@vantagelogistics.io",
            "phone": "+1-512-555-0201",
            "linkedin": "linkedin.com/in/priyanair-hr",
            "seniority": "director",
        },
    ],
    "clearpathfintech.com": [
        {
            "name": "Marcus Webb",
            "title": "Director of People Ops",
            "email": "m.webb@clearpathfintech.com",
            "phone": "+1-646-555-0301",
            "linkedin": "linkedin.com/in/marcuswebb",
            "seniority": "director",
        },
    ],
}

MOCK_ICP_SCORES = {
    "meridianhealth.com": 0.88,
    "vantagelogistics.io": 0.75,
    "clearpathfintech.com": 0.62,
}