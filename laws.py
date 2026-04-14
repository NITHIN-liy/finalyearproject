'''def suggest_law(problem):
    text = problem.lower()

    if "theft" in text or "stolen" in text:
        return {
            "type": "Criminal Case",
            "section": "IPC Section 379",
            "action": "File FIR at nearest police station",
            "authority": "Local Police"
        }

    elif "cyber" in text or "online" in text or "hack" in text:
        return {
            "type": "Cyber Crime",
            "section": "IT Act Section 66",
            "action": "Report to cyber crime cell",
            "authority": "Cyber Crime Department"
        }

    elif "accident" in text:
        return {
            "type": "Motor Vehicle Case",
            "section": "IPC Section 279",
            "action": "Inform traffic police",
            "authority": "Traffic Police"
        }

    elif "harassment" in text or "threat" in text:
        return {
            "type": "Criminal Case",
            "section": "IPC Section 506",
            "action": "File complaint",
            "authority": "Police Station"
        }

    else:
        return {
            "type": "Unknown",
            "section": "Not Found",
            "action": "Consult a legal professional",
            "authority": "Lawyer"
        }
'''


def suggest_law(problem):
    text = problem.lower()

    if "theft" in text or "stolen" in text:
        return {
            "type": "Criminal Case",
            "section": "IPC Section 379",
            "action": "File FIR at nearest police station",
            "authority": "Local Police"
        }

    elif "cyber" in text or "online" in text or "hack" in text:
        return {
            "type": "Cyber Crime",
            "section": "IT Act Section 66",
            "action": "Report to cyber crime cell",
            "authority": "Cyber Crime Department"
        }

    elif "accident" in text:
        return {
            "type": "Motor Vehicle Case",
            "section": "IPC Section 279",
            "action": "Inform traffic police",
            "authority": "Traffic Police"
        }

    elif "harassment" in text or "threat" in text:
        return {
            "type": "Criminal Case",
            "section": "IPC Section 506",
            "action": "File complaint",
            "authority": "Police Station"
        }

    else:
        return {
            "type": "Unknown",
            "section": "Not Found",
            "action": "Consult a legal professional",
            "authority": "Lawyer"
        }