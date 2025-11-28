
# Baza de date simplificata pentru ISO 286 (Interval 18-50mm)
# Valorile sunt in microni (um)

def get_it_grade(grade, diameter):
    """Returneaza valoarea tolerantei standard (IT) in microni."""
    # Intervalele standard ISO: (18, 30], (30, 50]
    # Daca diameter = 30, intra la 18-30.
    
    if 18 < diameter <= 30:
        range_key = '18-30'
    elif 30 < diameter <= 50:
        range_key = '30-50'
    else:
        return None

    # Valori IT standard (selectie comuna)
    it_values = {
        '18-30': {5: 9, 6: 13, 7: 21, 8: 33, 9: 52, 10: 84, 11: 130},
        '30-50': {5: 11, 6: 16, 7: 25, 8: 39, 9: 62, 10: 100, 11: 160}
    }
    
    try:
        return it_values[range_key][int(grade)]
    except (KeyError, ValueError):
        return None

def get_fundamental_deviation(letter, diameter, it_grade):
    """
    Returneaza abaterea fundamentala in microni.
    Pentru Alezaje (Litere Mari): Returneaza EI (Abaterea Inferioara) sau ES in cazuri speciale.
    Pentru Arbori (Litere Mici): Returneaza es (Abaterea Superioara) sau ei in cazuri speciale.
    """
    if 18 < diameter <= 30:
        range_key = '18-30'
    elif 30 < diameter <= 50:
        range_key = '30-50'
    else:
        return None

    # Simplificare: Abateri fundamentale comune (microni)
    # H/h au abatere 0.
    
    # Arbori (es pentru a-h, ei pentru j-zc) - Aici simplificam logica de baza
    # Valorile de mai jos sunt aproximari standard pentru pozitiile campurilor
    
    # Dictionar: 'litera': {'range': valoare_fundamentala}
    # Pentru arbori (shafts) - litere mici
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
        'r': {'18-30': 28,  '30-50': 34},  # ei (valori medii geometrice approx pt demo)
        's': {'18-30': 35,  '30-50': 43},  # ei
    }

    # Alezaje (holes) - litere mari (Regula generala: Simetric fata de arbori pt aceeasi litera)
    # H: EI = 0
    # F: EI = +valoare (de la f)
    # P: ES = -valoare (de la p) -> Aici e mai complicat, folosim regula generala ISO:
    # Hole Fundamental Dev = - Shaft Fundamental Dev (cu exceptii, dar pt demo e ok)
    
    letter_base = letter.lower()
    is_hole = letter.isupper()
    
    if letter_base not in shaft_devs:
        return 0 # Default fallback

    val = shaft_devs[letter_base][range_key]

    if is_hole:
        # Pentru H, EI = 0.
        if letter == 'H': return 0
        
        # Pentru A-H (Gap), EI = -es(shaft)
        # Pentru J-ZC (Press), ES = -ei(shaft) + Delta (Delta e complex, ignoram pt simplificare tema)
        # Simplificare majora pentru tema scolara:
        if letter_base in ['d', 'e', 'f', 'g']:
            return -val # EI = -es
        elif letter_base in ['k', 'm', 'n', 'p', 'r', 's']:
            # Aici e mai nuantat. De obicei se calculeaza ES.
            # Dar pentru a determina tipul ajustajului, ne bazam pe pozitia relativa.
            # Vom returna o valoare de referinta "fundamentala" inversata.
            return -val 
            
    return val

def calculate_fit_details(nominal, hole_str, shaft_str):
    """
    Calculeaza detaliile ajustajului.
    Ex: nominal=30, hole_str="H7", shaft_str="g6"
    """
    # Parse inputs
    hole_letter = ''.join([c for c in hole_str if c.isalpha()])
    hole_grade = int(''.join([c for c in hole_str if c.isdigit()]))
    
    shaft_letter = ''.join([c for c in shaft_str if c.isalpha()])
    shaft_grade = int(''.join([c for c in shaft_str if c.isdigit()]))

    # 1. Valori IT (Toleranta)
    tol_hole = get_it_grade(hole_grade, nominal)
    tol_shaft = get_it_grade(shaft_grade, nominal)

    if tol_hole is None or tol_shaft is None:
        return {"error": "Grad de toleranta sau diametru in afara intervalului suportat."}

    # 2. Abateri Fundamentale
    # Alezaj (Hole)
    # Daca e H, EI = 0, ES = EI + IT
    # Daca e P (presat), ES = val_fundamentala (negativa), EI = ES - IT
    
    # Calcul Alezaj
    if hole_letter == 'H':
        EI = 0
        ES = tol_hole
    elif hole_letter in ['F', 'G']: # Joc
        EI = get_fundamental_deviation(hole_letter, nominal, hole_grade) # returneaza val pozitiva
        ES = EI + tol_hole
    elif hole_letter in ['M', 'N', 'P', 'R', 'S']: # Intermediar/Presat
        # Aici regula ISO e complexa (ES = -ei + delta). 
        # Folosim o aproximare didactica: ES este definit de abaterea fundamentala (negativa)
        fund_dev = get_fundamental_deviation(hole_letter, nominal, hole_grade) # va fi negativ
        ES = fund_dev
        EI = ES - tol_hole
    else:
        EI = 0; ES = tol_hole # Fallback

    # Calcul Arbore
    if shaft_letter == 'h':
        es = 0
        ei = -tol_shaft
    elif shaft_letter in ['d', 'e', 'f', 'g']: # Joc
        es = get_fundamental_deviation(shaft_letter, nominal, shaft_grade) # negativ
        ei = es - tol_shaft
    elif shaft_letter in ['k', 'm', 'n', 'p', 'r', 's']: # Intermediar/Presat
        ei = get_fundamental_deviation(shaft_letter, nominal, shaft_grade) # pozitiv
        es = ei + tol_shaft
    else:
        es = 0; ei = -tol_shaft

    # 3. Calcul Jocuri / Strangeri
    # Joc Maxim (Jmax) = ES - ei
    # Joc Minim (Jmin) = EI - es
    # Strangere Maxima (Smax) = es - EI (negativul lui Jmin)
    # Strangere Minima (Smin) = ei - ES (negativul lui Jmax)

    val1 = ES - ei
    val2 = EI - es

    fit_type = "Nedeterminat"
    
    if val1 >= 0 and val2 >= 0:
        fit_type = "Cu Joc (Clearance)"
    elif val1 < 0 and val2 < 0:
        fit_type = "Cu Strangere (Interference/Press)"
    else:
        fit_type = "Intermediar (Transition)"

    # 4. Sistem
    system = "Necunoscut"
    if hole_letter == 'H':
        system = "Alezaj Unitar (Hole Basis)"
    elif shaft_letter == 'h':
        system = "Arbore Unitar (Shaft Basis)"
    else:
        system = "Combinat / Nestandard"

    # 5. Preferential
    # Lista ajustaje preferentiale uzuale (ISO 286)
    preferred_fits = [
        "H7/f7", "H7/g6", "H7/h6", "H7/k6", "H7/n6", "H7/p6", "H7/s6", # Alezaj unitar
        "F7/h6", "G7/h6", "H7/h6", "K7/h6", "N7/h6", "P7/h6", "S7/h6"  # Arbore unitar
    ]
    
    current_fit = f"{hole_letter}{hole_grade}/{shaft_letter}{shaft_grade}"
    is_preferred = current_fit in preferred_fits

    suggestion = ""
    if not is_preferred:
        # Sugestie simpla: pastreaza sistemul si cauta cel mai apropiat
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
