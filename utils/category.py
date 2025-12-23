CATEGORY_KEYWORDS = {
    "food": ["lunch", "dinner", "restaurant", "meal", "coffee","drink"],
    "transport": ["taxi", "bus", "ride", "train", "fuel", "gas"],
    "shopping": ["mall", "clothes", "shoes", "electronics"],
    "salary": ["salary", "income", "paycheck"],
    "health": ["doctor", "medicine", "hospital", "pharmacy", "clinic", "dentist", "healthcare", "checkup", "therapy", "eyewear","braces"],
    "charity": ["donation", "charity", "fundraising", "sponsorship", "contribution"],
    "personal_care": ["haircut", "spa", "salon", "cosmetic", "massage", "skincare", "makeup", "barber"],
    "utilities": ["electricity", "water", "internet", "phone", "mobile", "gas bill", "utility", "broadband"],
    "housing": ["rent", "mortgage", "apartment", "house", "landlord", "property", "maintenance"],
    "entertainment": ["movie", "netflix", "game", "concert"],
}
def get_category_from_reason(reason: str) -> str:
    reason_lower = reason.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in reason_lower:
                return category
    return "miscellaneous"

