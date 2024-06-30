import re

def assess_severity(scan_output):
    critical_keywords = ["critical", "exploit", "vulnerable"]
    high_keywords = ["high", "dangerous", "unpatched"]
    medium_keywords = ["medium", "moderate"]
    low_keywords = ["low", "informational"]

    severity_level = "Low"  # Default to Low severity if no matches found

    # Convert scan_output to lowercase for case-insensitive matching
    scan_output_lower = scan_output.lower()

    # Check for critical severity keywords
    for keyword in critical_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', scan_output_lower):
            severity_level = "Critical"
            break

    # Check for high severity keywords if not already set to Critical
    if severity_level != "Critical":
        for keyword in high_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', scan_output_lower):
                severity_level = "High"
                break

    # Check for medium severity keywords if not already set to High or Critical
    if severity_level not in ["High", "Critical"]:
        for keyword in medium_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', scan_output_lower):
                severity_level = "Medium"
                break

    # Check for low severity keywords if not already set to Medium, High, or Critical
    if severity_level not in ["Medium", "High", "Critical"]:
        for keyword in low_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', scan_output_lower):
                severity_level = "Low"
                break

    return severity_level
