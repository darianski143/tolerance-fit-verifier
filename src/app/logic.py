def get_it_grade(grade, diameter):
    """Returns the standard tolerance (IT) value in millimeters."""
    # ISO standard ranges: (18, 30], (30, 50]
    
    if 18 < diameter <= 30:
        range_key = '18-30'
    elif 30 < diameter <= 50:
        range_key = '30-50'
    else:
        return None

    # Standard IT values (common selection)
    it_values = {
        '18-30': {5: 9, 6: 13, 7: 21, 8: 33, 9: 52, 10: 84, 11: 130},
        '30-50': {5: 11, 6: 16, 7: 25, 8: 39, 9: 62, 10: 100, 11: 160}
    }
    
    try:
        return it_values[range_key][int(grade)] / 1000.0
    except (KeyError, ValueError):
        return None

def get_fundamental_deviation(letter, diameter, it_grade):
    """
    Returns the fundamental deviation in millimeters.
    For Holes (Uppercase): Returns EI (Lower Deviation) or ES in special cases.
    For Shafts (Lowercase): Returns es (Upper Deviation) or ei in special cases.
    """
    if 18 < diameter <= 30:
        range_key = '18-30'
    elif 30 < diameter <= 50:
        range_key = '30-50'
    else:
        return None

    # Fundamental deviations (microns)
    # H/h have 0 deviation.
    
    # Shafts (es for a-h, ei for j-zc)
    # Dictionary: 'letter': {'range': fundamental_value}
    shaft_devs = {
        'd': {'18-30': -65, '30-50': -80}, # es
        'e': {'18-30': -40, '30-50': -50}, # es
        'f': {'18-30': -20, '30-50': -25}, # es
        'g': {'18-30': -7,  '30-50': -9},  # es
        'h': {'18-30': 0,   '30-50': 0},   # es
        'k': {'18-30': 2,   '30-50': 2},   # ei
        'm': {'18-30': 8,   '30-50': 9},   # ei
        'n': {'18-30': 15,  '30-50': 17},  # ei
        'p': {'18-30': 22,  '30-50': 26},  # ei
        'r': {'18-30': 28,  '30-50': 34},  # ei
        's': {'18-30': 35,  '30-50': 43},  # ei
    }

    # Holes (uppercase) - General rule: Symmetric to shafts for the same letter
    
    letter_base = letter.lower()
    is_hole = letter.isupper()
    
    if letter_base not in shaft_devs:
        return 0 # Default fallback

    val = shaft_devs[letter_base][range_key] / 1000.0

    if is_hole:
        # For H, EI = 0.
        if letter == 'H': return 0
        
        # For A-H (Gap), EI = -es(shaft)
        # For J-ZC (Press), ES = -ei(shaft) + Delta (Delta ignored for simplicity)
        if letter_base in ['d', 'e', 'f', 'g']:
            return -val # EI = -es
        elif letter_base in ['k', 'm', 'n', 'p', 'r', 's']:
            # Simplified: returning inverted fundamental reference value
            return -val 
            
    return val

def calculate_fit_details(nominal, hole_str, shaft_str):
    """
    Calculates fit details.
    Ex: nominal=30, hole_str="H7", shaft_str="g6"
    """
    # Parse inputs
    hole_letter = ''.join([c for c in hole_str if c.isalpha()])
    hole_grade = int(''.join([c for c in hole_str if c.isdigit()]))
    
    shaft_letter = ''.join([c for c in shaft_str if c.isalpha()])
    shaft_grade = int(''.join([c for c in shaft_str if c.isdigit()]))

    # 1. IT Values (Tolerance)
    tol_hole = get_it_grade(hole_grade, nominal)
    tol_shaft = get_it_grade(shaft_grade, nominal)

    if tol_hole is None or tol_shaft is None:
        return {"error": "Tolerance grade or diameter out of supported range."}

    # 2. Fundamental Deviations
    # Hole Calculation
    if hole_letter == 'H':
        EI = 0
        ES = tol_hole
    elif hole_letter in ['F', 'G']: # Clearance
        EI = get_fundamental_deviation(hole_letter, nominal, hole_grade) # positive value
        ES = EI + tol_hole
    elif hole_letter in ['M', 'N', 'P', 'R', 'S']: # Transition/Press
        # Simplified approximation: ES defined by fundamental deviation (negative)
        fund_dev = get_fundamental_deviation(hole_letter, nominal, hole_grade) # negative
        ES = fund_dev
        EI = ES - tol_hole
    else:
        EI = 0; ES = tol_hole # Fallback

    # Shaft Calculation
    if shaft_letter == 'h':
        es = 0
        ei = -tol_shaft
    elif shaft_letter in ['d', 'e', 'f', 'g']: # Clearance
        es = get_fundamental_deviation(shaft_letter, nominal, shaft_grade) # negative
        ei = es - tol_shaft
    elif shaft_letter in ['k', 'm', 'n', 'p', 'r', 's']: # Transition/Press
        ei = get_fundamental_deviation(shaft_letter, nominal, shaft_grade) # positive
        es = ei + tol_shaft
    else:
        es = 0; ei = -tol_shaft

    # 3. Calculate Clearance / Interference
    # Max Clearance (Jmax) = ES - ei
    # Min Clearance (Jmin) = EI - es
    # Max Interference (Smax) = es - EI (negative of Jmin)
    # Min Interference (Smin) = ei - ES (negative of Jmax)

    val1 = ES - ei
    val2 = EI - es

    fit_type = "Nedeterminat"
    
    if val1 >= 0 and val2 >= 0:
        fit_type = "Cu Joc (Clearance)"
    elif val1 < 0 and val2 < 0:
        fit_type = "Cu Strangere (Interference/Press)"
    else:
        fit_type = "Intermediar (Transition)"

    # 4. System
    system = "Necunoscut"
    if hole_letter == 'H':
        system = "Alezaj Unitar (Hole Basis)"
    elif shaft_letter == 'h':
        system = "Arbore Unitar (Shaft Basis)"
    else:
        system = "Combinat / Nestandard"

    # 5. Preferred Fits
    # Common preferred fits (ISO 286)
    preferred_fits = [
        "H7/f7", "H7/g6", "H7/h6", "H7/k6", "H7/n6", "H7/p6", "H7/s6", # Hole Basis
        "F7/h6", "G7/h6", "H7/h6", "K7/h6", "N7/h6", "P7/h6", "S7/h6"  # Shaft Basis
    ]
    
    current_fit = f"{hole_letter}{hole_grade}/{shaft_letter}{shaft_grade}"
    is_preferred = current_fit in preferred_fits

    suggestion = ""
    if not is_preferred:
        # Simple suggestion based on system
        if system == "Alezaj Unitar (Hole Basis)":
            suggestion = "Incearca un ajustaj preferential: H7/g6 (Joc), H7/k6 (Intermediar) sau H7/p6 (Strangere)."
        elif system == "Arbore Unitar (Shaft Basis)":
            suggestion = "Incearca un ajustaj preferential: G7/h6 (Joc) sau P7/h6 (Strangere)."
        else:
            suggestion = "Se recomanda utilizarea sistemului Alezaj Unitar (ex: H7/x)."

    return {
        "nominal": nominal,
        "fit_str": current_fit,
        "hole_dims": {"ES": ES, "EI": EI},
        "shaft_dims": {"es": es, "ei": ei},
        "fit_type": fit_type,
        "system": system,
        "is_preferred": is_preferred,
        "suggestion": suggestion
    }
