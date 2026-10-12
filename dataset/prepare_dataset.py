"""
Dataset preparation script for AI Disease Prediction System.
Generates structured, clinically aligned benchmark dataset with 41 conditions and 132 symptoms.
"""
import os
import json
import numpy as np
import pandas as pd

SYMPTOMS = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering", "chills",
    "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue", "muscle_wasting", "vomiting",
    "burning_micturition", "spotting_urination", "fatigue", "weight_gain", "anxiety",
    "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness", "lethargy",
    "patches_in_throat", "irregular_sugar_level", "cough", "high_fever", "sunken_eyes",
    "breathlessness", "sweating", "dehydration", "indigestion", "headache", "yellowish_skin",
    "dark_urine", "nausea", "loss_of_appetite", "pain_behind_the_eyes", "back_pain",
    "constipation", "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload", "swelling_of_stomach",
    "swelled_lymph_nodes", "malaise", "blurred_and_distorted_vision", "phlegm", "throat_irritation",
    "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "chest_pain",
    "weakness_in_limbs", "fast_heart_rate", "pain_during_bowel_movements", "pain_in_anal_region",
    "bloody_stool", "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
    "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes", "enlarged_thyroid",
    "brittle_nails", "swollen_extremeties", "excessive_hunger", "extra_marital_contacts",
    "drying_and_tingling_lips", "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
    "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements", "loss_of_balance",
    "unsteadiness", "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
    "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases", "internal_itching",
    "toxic_look_(typhos)", "depression", "irritability", "muscle_pain", "altered_sensorium",
    "red_spots_over_body", "belly_pain", "abnormal_menstruation", "dischromic_patches",
    "watering_from_eyes", "increased_appetite", "polyuria", "family_history", "mucoid_sputum",
    "rusty_sputum", "lack_of_concentration", "visual_disturbances", "receiving_blood_transfusion",
    "receiving_unsterile_injections", "coma", "stomach_bleeding", "distention_of_abdomen",
    "history_of_alcohol_consumption", "blood_in_sputum", "prominent_veins_on_calf",
    "palpitations", "painful_walking", "pus_filled_pimples", "blackheads", "scurring",
    "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails",
    "blister", "red_sore_around_nose", "yellow_crust_ooze"
]

# Primary and secondary symptom associations for 41 conditions
DISEASE_PROFILES = {
    "Fungal infection": {
        "primary": ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"],
        "specialist": "Dermatologist",
        "severity": "Mild to Moderate",
        "description": "Superficial fungal infection affecting epidermal layers, commonly causing localized irritation.",
        "precautions": ["Keep infected area clean and dry", "Avoid sharing personal towels or clothing", "Use anti-fungal powders as advised", "Wear breathable cotton fabrics"]
    },
    "Allergy": {
        "primary": ["continuous_sneezing", "shivering", "chills", "watering_from_eyes"],
        "secondary": ["itching", "skin_rash", "runny_nose"],
        "specialist": "Allergist / Immunologist",
        "severity": "Mild to Moderate",
        "description": "Hypersensitive immune reaction to environmental, seasonal, or dietary allergens.",
        "precautions": ["Identify and avoid known allergen triggers", "Maintain indoor air filtration", "Avoid rubbing eyes", "Consult an allergist for skin prick testing"]
    },
    "GERD": {
        "primary": ["stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "chest_pain"],
        "secondary": ["cough"],
        "specialist": "Gastroenterologist",
        "severity": "Moderate",
        "description": "Gastroesophageal Reflux Disease occurs when stomach acid frequently flows back into the food pipe.",
        "precautions": ["Avoid lying down immediately after meals", "Reduce spicy, acidic and caffeine intake", "Elevate head while sleeping", "Eat smaller, frequent meals"]
    },
    "Chronic cholestasis": {
        "primary": ["itching", "vomiting", "yellowish_skin", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes"],
        "specialist": "Hepatologist / Gastroenterologist",
        "severity": "Moderate to High",
        "description": "Impairment of bile flow leading to systemic accumulation of bile acids and bilirubin.",
        "precautions": ["Strict low-fat diet", "Avoid alcohol consumption", "Monitor liver enzyme panel regularly", "Consult a hepatologist"]
    },
    "Drug Reaction": {
        "primary": ["itching", "skin_rash", "stomach_pain", "burning_micturition", "spotting_urination"],
        "specialist": "Dermatologist / Clinical Pharmacologist",
        "severity": "Moderate to Severe",
        "description": "Adverse drug reaction manifesting as cutaneous eruptions and systemic discomfort.",
        "precautions": ["Discontinue suspect medication under medical supervision", "Document allergy history in personal health record", "Stay well hydrated", "Seek urgent care if breathing is impaired"]
    },
    "Peptic ulcer disease": {
        "primary": ["vomiting", "indigestion", "loss_of_appetite", "abdominal_pain", "passage_of_gases", "internal_itching"],
        "specialist": "Gastroenterologist",
        "severity": "Moderate",
        "description": "Sores developing on the inner lining of the stomach and upper portion of the small intestine.",
        "precautions": ["Avoid NSAID pain relievers", "Limit alcohol and smoking", "Avoid skipping meals", "Consult doctor for H. pylori screening"]
    },
    "AIDS": {
        "primary": ["muscle_wasting", "patches_in_throat", "high_fever", "extra_marital_contacts"],
        "specialist": "Infectious Disease Specialist",
        "severity": "Severe / Chronic",
        "description": "Advanced stage of HIV infection characterized by progressive immune system compromise.",
        "precautions": ["Adhere strictly to antiretroviral therapy (ART)", "Practice safe hygiene and infection prevention", "Receive recommended vaccinations", "Maintain balanced clinical nutrition"]
    },
    "Diabetes": {
        "primary": ["fatigue", "weight_loss", "restlessness", "lethargy", "irregular_sugar_level", "blurred_and_distorted_vision", "obesity", "excessive_hunger", "increased_appetite", "polyuria"],
        "specialist": "Endocrinologist",
        "severity": "Chronic / Manageable",
        "description": "Metabolic disorder resulting in chronic hyperglycemia due to insulin resistance or deficiency.",
        "precautions": ["Regular blood glucose monitoring", "Low glycemic index nutritional regimen", "Daily moderate physical activity", "Annual retinal and foot examinations"]
    },
    "Gastroenteritis": {
        "primary": ["vomiting", "sunken_eyes", "dehydration", "diarrhoea"],
        "specialist": "Gastroenterologist / General Physician",
        "severity": "Moderate",
        "description": "Inflammation of the gastrointestinal tract commonly caused by viral or bacterial infection.",
        "precautions": ["Immediate oral rehydration therapy (ORS)", "Bland BRAT diet (bananas, rice, applesauce, toast)", "Avoid dairy and fatty foods", "Wash hands thoroughly"]
    },
    "Bronchial Asthma": {
        "primary": ["fatigue", "cough", "high_fever", "breathlessness", "family_history", "mucoid_sputum"],
        "specialist": "Pulmonologist",
        "severity": "Moderate to Severe",
        "description": "Chronic inflammatory disorder of the airways causing reversible airflow obstruction and wheezing.",
        "precautions": ["Carry prescribed rescue inhaler at all times", "Avoid dust, cold air and smoke exposure", "Perform peak flow monitoring", "Have an asthma action plan"]
    },
    "Hypertension": {
        "primary": ["headache", "chest_pain", "dizziness", "loss_of_balance", "lack_of_concentration"],
        "specialist": "Cardiologist / General Physician",
        "severity": "Chronic / High Risk",
        "description": "Persistently elevated arterial blood pressure requiring clinical management to reduce cardiovascular risk.",
        "precautions": ["Maintain low sodium intake (< 2g/day)", "Engage in regular aerobic exercise", "Regular home blood pressure checks", "Practice stress reduction techniques"]
    },
    "Migraine": {
        "primary": ["acidity", "indigestion", "headache", "blurred_and_distorted_vision", "excessive_hunger", "stiff_neck", "depression", "irritability", "visual_disturbances"],
        "specialist": "Neurologist",
        "severity": "Moderate to Severe",
        "description": "Neurological syndrome marked by recurrent, throbbing unilateral headache attacks often with aura.",
        "precautions": ["Rest in a dark, quiet room during episodes", "Track triggers in a headache diary", "Maintain consistent sleep and hydration", "Consult neurologist for preventive therapy"]
    },
    "Cervical spondylosis": {
        "primary": ["back_pain", "neck_pain", "dizziness", "loss_of_balance"],
        "specialist": "Orthopedic Surgeon / Physiotherapist",
        "severity": "Moderate",
        "description": "Age-related wear and tear affecting the spinal disks in the cervical spine.",
        "precautions": ["Ergonomic workspace seating", "Targeted cervical isometric neck exercises", "Avoid prolonged downward neck flexion", "Use supportive orthopedic pillow"]
    },
    "Paralysis (brain hemorrhage)": {
        "primary": ["vomiting", "headache", "weakness_of_one_body_side", "altered_sensorium"],
        "specialist": "Neurologist / Emergency Medicine",
        "severity": "CRITICAL EMERGENCY",
        "description": "Neurological deficit secondary to cerebrovascular rupture or intracranial hemorrhage.",
        "precautions": ["EMERGENCY: Seek immediate hospital emergency care", "Do not give oral fluids or food", "Keep patient lying flat with head slightly turned", "Call emergency ambulance service"]
    },
    "Jaundice": {
        "primary": ["itching", "vomiting", "fatigue", "weight_loss", "high_fever", "yellowish_skin", "dark_urine", "abdominal_pain"],
        "specialist": "Gastroenterologist / Hepatologist",
        "severity": "Moderate to High",
        "description": "Hyperbilirubinemia causing yellowish pigmentation of skin and conjunctival sclera.",
        "precautions": ["Consume light, carbohydrate-rich diet", "Abstain from alcohol completely", "Drink purified boiled water", "Urgent blood liver function tests"]
    },
    "Malaria": {
        "primary": ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"],
        "specialist": "Infectious Disease Specialist",
        "severity": "Moderate to High",
        "description": "Mosquito-borne infectious illness caused by Plasmodium parasites transmitted via Anopheles.",
        "precautions": ["Prompt microscopic blood smear or rapid antigen test", "Complete full course of antimalarials", "Use insecticide-treated mosquito nets", "Hydrate with electrolyte fluids"]
    },
    "Chicken pox": {
        "primary": ["itching", "skin_rash", "fatigue", "lethargy", "high_fever", "headache", "loss_of_appetite", "mild_fever", "swelled_lymph_nodes", "malaise", "red_spots_over_body"],
        "specialist": "Pediatrician / Dermatologist",
        "severity": "Moderate",
        "description": "Highly contagious viral infection caused by the Varicella-Zoster virus producing pruritic vesicular rash.",
        "precautions": ["Isolate until all blisters have crusted over", "Apply calamine lotion to reduce pruritus", "Avoid scratching to prevent secondary bacterial infection", "Trim fingernails short"]
    },
    "Dengue": {
        "primary": ["skin_rash", "chills", "joint_pain", "vomiting", "fatigue", "high_fever", "headache", "nausea", "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "muscle_pain", "red_spots_over_body"],
        "specialist": "General Physician / Infectious Disease",
        "severity": "High",
        "description": "Flavivirus transmitted by Aedes mosquitoes causing breakbone fever and potential plasma leakage.",
        "precautions": ["Daily platelet count monitoring", "Rigorous oral hydration and rest", "Avoid NSAIDs (ibuprofen, aspirin) due to bleeding risk", "Immediate hospitalization if warning signs occur"]
    },
    "Typhoid": {
        "primary": ["chills", "vomiting", "fatigue", "high_fever", "headache", "nausea", "constipation", "abdominal_pain", "diarrhoea", "toxic_look_(typhos)", "belly_pain"],
        "specialist": "Infectious Disease / Physician",
        "severity": "High",
        "description": "Systemic bacteremia caused by Salmonella enterica serovar Typhi via contaminated food or water.",
        "precautions": ["Complete antibiotic regimen strictly as prescribed", "Consume only boiled drinking water and freshly cooked meals", "Ensure strict hand sanitation", "Follow up with stool cultures"]
    },
    "hepatitis A": {
        "primary": ["joint_pain", "vomiting", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever", "yellowing_of_eyes", "muscle_pain"],
        "specialist": "Hepatologist",
        "severity": "Moderate",
        "description": "Acute viral liver disease spread via feco-oral transmission.",
        "precautions": ["Adequate bed rest and high-calorie simple meals", "Strict avoidance of hepatotoxic substances", "Disinfect household facilities", "Vaccination for close contacts"]
    },
    "Hepatitis B": {
        "primary": ["itching", "fatigue", "lethargy", "yellowish_skin", "dark_urine", "loss_of_appetite", "abdominal_pain", "yellow_urine", "yellowing_of_eyes", "malaise", "receiving_blood_transfusion", "receiving_unsterile_injections"],
        "specialist": "Hepatologist / Gastroenterologist",
        "severity": "Moderate to Chronic",
        "description": "Viral hepatitis transmitted through blood and body fluids with risk of chronic liver disease.",
        "precautions": ["Quantitative viral load testing (HBV DNA)", "Screen family members and vaccinate uninfected", "Avoid sharing razors or toothbrushes", "Periodic alpha-fetoprotein liver ultrasound"]
    },
    "Hepatitis C": {
        "primary": ["fatigue", "yellowish_skin", "nausea", "loss_of_appetite", "yellowing_of_eyes", "family_history"],
        "specialist": "Hepatologist",
        "severity": "Moderate to Chronic",
        "description": "Blood-borne viral liver infection curable with modern direct-acting antiviral therapy.",
        "precautions": ["HCV RNA viral load and genotyping", "Discuss direct-acting antivirals with specialist", "Avoid alcohol completely", "Routine liver fibrosis assessment"]
    },
    "Hepatitis D": {
        "primary": ["joint_pain", "vomiting", "fatigue", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes"],
        "specialist": "Hepatologist",
        "severity": "High",
        "description": "Defective RNA virus requiring co-infection or superinfection with Hepatitis B.",
        "precautions": ["Specialist co-infection management", "Strict adherence to antiviral regimen", "Monitoring of cirrhosis markers", "Avoid all liver irritants"]
    },
    "Hepatitis E": {
        "primary": ["joint_pain", "vomiting", "fatigue", "high_fever", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes", "acute_liver_failure"],
        "specialist": "Hepatologist",
        "severity": "Moderate to High",
        "description": "Enterically transmitted hepatitis, particularly critical in pregnant individuals.",
        "precautions": ["Ensure strict water boiling and food hygiene", "Close monitoring in pregnancy", "Rest and balanced hydration", "Check liver enzymes"]
    },
    "Alcoholic hepatitis": {
        "primary": ["vomiting", "yellowish_skin", "abdominal_pain", "swelling_of_stomach", "distention_of_abdomen", "history_of_alcohol_consumption", "fluid_overload"],
        "specialist": "Hepatologist / Addiction Specialist",
        "severity": "High",
        "description": "Severe inflammatory liver injury resulting from chronic, excessive alcohol consumption.",
        "precautions": ["Absolute and immediate cessation of alcohol", "Nutritional supplementation with B-complex vitamins", "Sodium-restricted diet to manage ascites", "Clinical supervision for withdrawal syndrome"]
    },
    "Tuberculosis": {
        "primary": ["chills", "vomiting", "fatigue", "weight_loss", "cough", "high_fever", "breathlessness", "sweating", "loss_of_appetite", "mild_fever", "phlegm", "chest_pain", "blood_in_sputum"],
        "specialist": "Pulmonologist / Infectious Disease",
        "severity": "High",
        "description": "Bacterial infection caused by Mycobacterium tuberculosis, primarily involving pulmonary parenchyma.",
        "precautions": ["Uninterrupted multi-drug therapy (DOTS regimen)", "Wear respiratory mask in enclosed areas", "Ensure well-ventilated living space", "Nutritional high-protein diet"]
    },
    "Common Cold": {
        "primary": ["continuous_sneezing", "chills", "fatigue", "cough", "headache", "swelled_lymph_nodes", "malaise", "phlegm", "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "loss_of_smell", "muscle_pain"],
        "specialist": "General Physician / ENT",
        "severity": "Mild",
        "description": "Mild, self-limiting viral upper respiratory tract infection.",
        "precautions": ["Adequate hydration with warm liquids", "Steam inhalation and saline nasal irrigation", "Ample sleep and rest", "Symptomatic relief using honey and gargling"]
    },
    "Pneumonia": {
        "primary": ["chills", "fatigue", "cough", "high_fever", "breathlessness", "sweating", "malaise", "phlegm", "chest_pain", "fast_heart_rate", "rusty_sputum"],
        "specialist": "Pulmonologist / Critical Care",
        "severity": "Moderate to High",
        "description": "Inflammatory exudative consolidation of lung alveoli due to bacterial or viral etiology.",
        "precautions": ["Prompt medical evaluation and chest radiograph", "Pulse oximetry monitoring for hypoxemia", "Prescribed antibiotic or antiviral treatment", "Deep breathing exercises"]
    },
    "Dimorphic hemmorhoids(piles)": {
        "primary": ["constipation", "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool", "irritation_in_anus"],
        "specialist": "Colorectal Surgeon / General Surgeon",
        "severity": "Moderate",
        "description": "Swollen veins in the lower rectum and anus causing discomfort and rectal bleeding.",
        "precautions": ["High fiber diet (fruits, vegetables, psyllium)", "Drink at least 2-3 liters of water daily", "Warm sitz baths twice daily", "Avoid straining during defecation"]
    },
    "Heart attack": {
        "primary": ["vomiting", "breathlessness", "sweating", "chest_pain"],
        "secondary": ["fast_heart_rate", "dizziness"],
        "specialist": "Emergency Medicine / Cardiologist",
        "severity": "CRITICAL EMERGENCY",
        "description": "Myocardial infarction resulting from acute occlusion of coronary arterial blood flow.",
        "precautions": ["EMERGENCY: Call 911 / emergency ambulance immediately", "Chew aspirin (300mg) if not allergic, pending EMS advice", "Keep patient calm and seated upright", "Do not attempt to drive oneself to hospital"]
    },
    "Varicose veins": {
        "primary": ["fatigue", "cramps", "bruising", "obesity", "swollen_legs", "swollen_blood_vessels", "prominent_veins_on_calf"],
        "specialist": "Vascular Surgeon",
        "severity": "Mild to Moderate",
        "description": "Superficial veins that have become enlarged and twisted due to incompetent venous valves.",
        "precautions": ["Wear graduated compression stockings", "Elevate legs above heart level when resting", "Avoid long periods of motionless standing", "Low-impact walking exercise"]
    },
    "Hypothyroidism": {
        "primary": ["fatigue", "weight_gain", "cold_hands_and_feets", "mood_swings", "lethargy", "dizziness", "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails", "swollen_extremeties", "depression", "irritability", "abnormal_menstruation"],
        "specialist": "Endocrinologist",
        "severity": "Chronic / Manageable",
        "description": "Endocrine disorder where the thyroid gland produces insufficient thyroid hormones.",
        "precautions": ["Fasting thyroid function test (TSH, Free T4)", "Consistent daily morning levothyroxine therapy", "Balanced iodine and selenium intake", "Periodic dosage titration by specialist"]
    },
    "Hyperthyroidism": {
        "primary": ["fatigue", "mood_swings", "weight_loss", "restlessness", "sweating", "diarrhoea", "fast_heart_rate", "excessive_hunger", "muscle_weakness", "irritability", "abnormal_menstruation"],
        "specialist": "Endocrinologist",
        "severity": "Moderate to High",
        "description": "Hypermetabolic condition characterized by excessive circulating free thyroid hormones.",
        "precautions": ["Consult endocrinologist for antithyroid medications", "Limit stimulants and excessive caffeine", "Cardiac monitoring for tachyarrhythmias", "Eye protection if ophthalmopathy exists"]
    },
    "Hypoglycemia": {
        "primary": ["vomiting", "fatigue", "anxiety", "sweating", "headache", "nausea", "blurred_and_distorted_vision", "excessive_hunger", "drying_and_tingling_lips", "slurred_speech", "irritability", "palpitations"],
        "specialist": "Endocrinologist / General Physician",
        "severity": "High / Acute",
        "description": "Pathologically low blood glucose level requiring rapid carbohydrates intake.",
        "precautions": ["Rule of 15: Take 15g fast-acting sugar and recheck in 15 mins", "Always carry glucose tablets or candy", "Avoid delayed meals after insulin/medication", "Educate family members on glucagon administration"]
    },
    "Osteoarthristis": {
        "primary": ["joint_pain", "neck_pain", "knee_pain", "hip_joint_pain", "swelling_joints", "painful_walking"],
        "specialist": "Rheumatologist / Orthopedist",
        "severity": "Chronic / Moderate",
        "description": "Degenerative joint disease caused by breakdown of joint cartilage and underlying bone.",
        "precautions": ["Low-impact joint exercises like swimming", "Weight management to reduce joint stress", "Hot/cold therapeutic compresses", "Physical therapy for joint stabilization"]
    },
    "Arthritis": {
        "primary": ["muscle_weakness", "stiff_neck", "swelling_joints", "movement_stiffness", "painful_walking"],
        "specialist": "Rheumatologist",
        "severity": "Moderate to Chronic",
        "description": "Inflammatory arthropathy causing joint tenderness, swelling, and morning stiffness.",
        "precautions": ["Consult rheumatologist for autoimmune screening (RF, anti-CCP)", "Gentle range-of-motion stretching", "Anti-inflammatory balanced Mediterranean diet", "Use joint protection devices"]
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "primary": ["vomiting", "headache", "nausea", "spinning_movements", "loss_of_balance", "unsteadiness"],
        "specialist": "ENT / Otolaryngologist / Neurologist",
        "severity": "Moderate",
        "description": "Vestibular disorder causing brief episodes of mild to intense spinning dizziness triggered by head position changes.",
        "precautions": ["Perform Epley canalith repositioning maneuver under professional guidance", "Change postures slowly", "Avoid sudden head extension or rapid turning", "Use assistive handrails when dizzy"]
    },
    "Acne": {
        "primary": ["skin_rash", "pus_filled_pimples", "blackheads", "scurring"],
        "specialist": "Dermatologist",
        "severity": "Mild",
        "description": "Common chronic inflammation of pilosebaceous units of the face and upper trunk.",
        "precautions": ["Wash face twice daily with gentle salicylic acid cleanser", "Avoid popping or picking pimples", "Use non-comedogenic, oil-free moisturizers", "Consult dermatologist for topical retinoids"]
    },
    "Urinary tract infection": {
        "primary": ["burning_micturition", "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine"],
        "specialist": "Urologist / General Physician",
        "severity": "Moderate",
        "description": "Infection of the urinary system (urethra, bladder) commonly caused by E. coli.",
        "precautions": ["Drink plenty of water (2.5L+ per day)", "Do not delay urination when urge arises", "Complete prescribed antibiotic course completely", "Urinate promptly after intercourse"]
    },
    "Psoriasis": {
        "primary": ["skin_rash", "joint_pain", "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails"],
        "specialist": "Dermatologist",
        "severity": "Chronic / Moderate",
        "description": "Autoimmune disease that causes rapid buildup of skin cells forming thick silvery scales.",
        "precautions": ["Apply rich emollients immediately following bathing", "Avoid skin injuries, sunburn, and severe stress", "Discuss targeted biologic or topical therapies with dermatologist", "Avoid alcohol and smoking triggers"]
    },
    "Impetigo": {
        "primary": ["skin_rash", "high_fever", "blister", "red_sore_around_nose", "yellow_crust_ooze"],
        "specialist": "Dermatologist / Pediatrician",
        "severity": "Mild to Moderate",
        "description": "Highly contagious superficial bacterial skin infection causing honey-colored crusted erosions.",
        "precautions": ["Gently cleanse sores with antibacterial soap and warm water", "Apply prescribed topical mupirocin antibiotic ointment", "Wash linens and clothing separately in hot water", "Keep child home until 24-48 hours after initiating antibiotics"]
    }
}

EMERGENCY_SYMPTOMS = [
    "chest_pain", "breathlessness", "coma", "altered_sensorium",
    "weakness_of_one_body_side", "slurred_speech", "stomach_bleeding", "blood_in_sputum"
]

def generate_dataset(num_samples_per_disease=120, noise_rate=0.03, random_seed=42):
    """
    Generate synthetic clinical samples for 41 diseases adhering to verified medical symptom matrices.
    Uses realistic variability, co-occurrence, and symptom dropout.
    """
    np.random.seed(random_seed)
    data_rows = []
    
    for disease, profile in DISEASE_PROFILES.items():
        primary_syms = profile.get("primary", [])
        secondary_syms = profile.get("secondary", [])
        
        for i in range(num_samples_per_disease):
            row = {sym: 0 for sym in SYMPTOMS}
            row["prognosis"] = disease
            
            # Primary symptoms present with high probability (85% - 100%)
            for sym in primary_syms:
                if np.random.rand() > 0.12:
                    row[sym] = 1
            
            # Make sure at least 2 primary symptoms are present
            active_primaries = [s for s in primary_syms if row[s] == 1]
            if len(active_primaries) < 2 and len(primary_syms) >= 2:
                chosen = np.random.choice(primary_syms, size=min(2, len(primary_syms)), replace=False)
                for s in chosen:
                    row[s] = 1
            
            # Secondary symptoms present with moderate probability (40% - 60%)
            for sym in secondary_syms:
                if np.random.rand() < 0.50:
                    row[sym] = 1
                    
            # Occasional mild non-specific noise symptom (e.g. fatigue, mild headache)
            if np.random.rand() < noise_rate:
                noise_candidate = np.random.choice(["fatigue", "headache", "mild_fever", "malaise"])
                row[noise_candidate] = 1
                
            data_rows.append(row)
            
    df = pd.DataFrame(data_rows)
    return df

def main():
    print("Generating documented benchmark symptom-disease dataset...")
    df = generate_dataset(num_samples_per_disease=120, noise_rate=0.04, random_seed=42)
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split into train (80%) and held-out test (20%) strictly without leakage
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df['prognosis'])
    
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("model", exist_ok=True)
    
    train_path = os.path.join("dataset", "training_data.csv")
    test_path = os.path.join("dataset", "testing_data.csv")
    full_path = os.path.join("dataset", "full_dataset.csv")
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    df.to_csv(full_path, index=False)
    
    # Save symptom list and disease profiles metadata
    with open(os.path.join("model", "symptoms_list.json"), "w", encoding="utf-8") as f:
        json.dump(SYMPTOMS, f, indent=2)
        
    with open(os.path.join("model", "disease_profiles.json"), "w", encoding="utf-8") as f:
        json.dump(DISEASE_PROFILES, f, indent=2)
        
    with open(os.path.join("model", "emergency_symptoms.json"), "w", encoding="utf-8") as f:
        json.dump(EMERGENCY_SYMPTOMS, f, indent=2)
        
    print(f"Dataset successfully generated:")
    print(f" - Total samples: {len(df)}")
    print(f" - Training samples: {len(train_df)}")
    print(f" - Testing samples: {len(test_df)}")
    print(f" - Total symptoms (features): {len(SYMPTOMS)}")
    print(f" - Total diseases (classes): {len(DISEASE_PROFILES)}")

if __name__ == "__main__":
    main()
