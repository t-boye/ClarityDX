import logging
import os
import joblib
import requests
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Set, Dict, Any, Union, Optional # Keep these imports

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- NLTK Setup ---
# Ensure NLTK data is ready when this module is imported.
# This runs once when the module is imported.
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
    logger.info("✅ NLTK data for SymScan prediction module confirmed.")
except LookupError as e:
    logger.error(f"❌ Missing NLTK data for symscan_prediction module: {e}. Attempting to download...")
    try:
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        logger.info("✅ NLTK data successfully downloaded by symscan_prediction module.")
    except Exception as download_error:
        logger.error(f"Failed to download NLTK data in symscan_prediction module: {download_error}")
        # Re-raise the exception to fail startup if NLTK data is crucial
        raise RuntimeError("Failed to set up NLTK dependencies for SymScan.") from download_error

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# --- Medical Symptom Synonyms Mapping ---
SYMPTOM_SYNONYMS = {
    "migraine": "headache",
    "pressure in head": "headache",
    "facial pain": "facial pain",
    "pain behind eyes": "eye pain",
    "eye ache": "eye pain",
    "jaw pain": "jaw pain",
    "painful joints": "arthralgia",
    "bone pain": "bone pain",
    "feeling unwell": "malaise",
    "general weakness": "weakness",
    "lack of energy": "fatigue",
    "tired all the time": "fatigue",
    "always tired": "fatigue",
    "weight gain": "weight gain", # Explicit for consistency
    "unexplained weight gain": "weight gain",
    "feverish": "fever",
    "low grade fever": "fever",
    "sweating": "sweating", # Ensure consistency if 'sweats' is mapped here
    "excessive thirst": "polydipsia", # Or "increased thirst" if preferred
    "frequent urination": "polyuria", # Or "frequent urination" if preferred
    "loss of consciousness": "syncope", # More general than fainting
    "unresponsive": "loss of consciousness",

    # Respiratory Symptoms (More variants)
    "nasal discharge": "runny nose",
    "post-nasal drip": "throat irritation",
    "difficulty talking": "hoarseness",
    "voice hoarseness": "hoarseness",
    "hoarse voice": "hoarseness",
    "tight chest": "chest tightness",
    "labored breathing": "dyspnea",
    "gasping for air": "dyspnea",
    "nasal congestion": "nasal congestion", # Ensure consistency with 'blocked nose', 'stuffy nose'
    "postnasal drip": "postnasal drip", # Keeping distinct if it's treated separately in data
    "sore throat": "sore throat", # Can be canonical vs 'throat irritation'
    "irritated throat": "sore throat",
    "swallowing difficulty": "dysphagia",
    "stridor": "stridor", # High-pitched breathing sound
    "rales": "rales", # Crackling lung sounds (medical)
    "rhonchi": "rhonchi", # Low-pitched lung sounds (medical)
    "pleuritic chest pain": "pleuritic pain", # Pain on breathing
    

    # Cardiovascular/Neurological
    "chest pressure": "chest pain",
    "palpitations": "heart palpitations",
    "irregular heartbeat": "arrhythmia",
    "fainting": "syncope",
    "passing out": "syncope",
    "seizure": "seizures",
    "convulsion": "seizures",
    "tremor": "shaking",
     "abdominal tenderness": "abdominal pain", # Could be distinct, but often implies pain
    "vomiting blood": "hematemesis",
    "blood in vomit": "hematemesis",
    "bloody stools": "melena", # Dark, tarry stools
    "fresh blood in stool": "hematochezia", # Bright red blood
    "black stools": "melena",
    "pale stools": "pale stools",
    "greasy stools": "steatorrhea", # Medical term for fatty stools
    "bowel changes": "change in bowel habits",
    "change in bowel habits": "change in bowel habits",
    "difficulty passing stool": "constipation",
    "stomach upset": "indigestion",
    "loss of taste": "ageusia",
    "loss of smell": "anosmia",
    "bad breath": "halitosis",
    "foul breath": "halitosis",

    # Gastrointestinal (Extended)
    "gas": "flatulence",
    "bloating": "bloating",
    "abdominal bloating": "bloating",
    "cramps": "abdominal cramps",
    "stomach cramps": "abdominal cramps",
    "food intolerance": "indigestion",
    "burping": "belching",
    "belch": "belching",
    "throwing up": "vomiting",
    "nausea and vomiting": "vomiting",
    "spitting blood": "hemoptysis", # Blood from cough
    "coughing up blood": "hemoptysis",
    "blister": "blisters", # Plural vs singular
    "skin lesion": "skin lesions",
    "redness": "erythema", # Medical term for redness
    "bruising": "bruising",
    "easy bruising": "bruising",
    "petechiae": "petechiae", # Tiny red spots
    "purpura": "purpura", # Larger purplish spots
    "jaundice": "jaundice", # Consistent with yellow skin/eyes
    "pale mucous membranes": "pallor",
    "dry skin": "dry skin",
    "hair loss": "hair loss",
    "brittle nails": "nail changes",
    "nail discoloration": "nail changes",

    # Urinary & Genital
    "cloudy urine": "urine discoloration",
    "dark urine": "urine discoloration",
    "painful bladder": "bladder pain",
    "urinary urgency": "urinary urgency",
    "involuntary urination": "incontinence",
    "genital sores": "genital ulcers",
    "frequent urge to urinate": "urinary urgency",
    "blood in urine": "hematuria",
    "pain in flank": "flank pain", # Often kidney related
    "testicular pain": "testicular pain",
    "vaginal discharge": "vaginal discharge",
    "penile discharge": "penile discharge",
    "painful intercourse": "dyspareunia", # Medical term
    "sexual dysfunction": "sexual dysfunction",

    # Skin & Mucous Membranes
    "skin ulcers": "skin lesions",
    "open wounds": "skin lesions",
    "scaly skin": "scaling",
    "peeling skin": "skin peeling",
    "discoloration of skin": "skin discoloration",
    "cyanosis": "blue skin",
    "cold": "chills",
    "cold skin": "cold extremities",
    "cold intolerance": "cold intolerance",
    "bluish lips": "cyanosis",

    # Eye/Ear Specific
    "eye discharge": "eye discharge",
    "watery eyes": "tearing",
    "dry eyes": "dry eyes",
    "ear discharge": "ear discharge",
    "ear fullness": "ear pressure",
    "blocked ears": "ear blockage",
    "red eyes": "red eyes",
    "itchy eyes": "itchy eyes",
    "blurred vision": "blurred vision",
    "double vision": "diplopia",
    "vision loss": "vision loss",
    "photophobia": "photophobia", # Sensitivity to light
    "ear ringing": "tinnitus",
    "hearing loss": "hearing loss",
    "runny ears": "ear discharge",
    "sore tongue": "tongue soreness",
    "mouth sores": "oral lesions",
    "oral ulcers": "oral lesions",
    "nasal bleeding": "epistaxis", # Nosebleed
    "nosebleed": "epistaxis",

# --- Neurological/Psychological (Deeper) ---
    "drowsiness": "drowsiness",
    "lethargy": "lethargy",
    "irritability": "irritability",
    "agitation": "agitation",
    "delusion": "delusions", # Plural
    "hallucination": "hallucinations", # Plural
    "difficulty concentrating": "cognitive dysfunction",
    "forgetfulness": "memory impairment",
    "disorientation": "disorientation",
    "slurred speech": "dysarthria",
    "difficulty speaking": "dysphasia", # Or 'aphasia' if severe
    "vertigo": "vertigo", # Specific type of dizziness
    "loss of balance": "balance problems",
    "gait disturbance": "balance problems",
    "numbness in limbs": "numbness",
    "paralysis": "paralysis",
    
    
    # Psychosocial/Mental Symptoms
    "feeling anxious": "anxiety",
    "nervousness": "anxiety",
    "panic attack": "panic attack",
    "low mood": "depression",
    "feeling sad": "depression",
    "lack of interest": "anhedonia",
    "confusion": "confusion",
    "memory loss": "memory impairment",
    "brain fog": "cognitive dysfunction",
    "irritability": "irritability",

 # --- Musculoskeletal (More) ---
    "stiff joints": "joint stiffness",
    "joint swelling": "joint swelling",
    "muscle cramps": "muscle cramps",
    "muscle weakness": "muscle weakness",
    "reduced range of motion": "limited range of motion",
    
# --- Lymphatic/Endocrine ---
    "swollen lymph nodes": "swollen lymph nodes",
    "gland swelling": "swollen lymph nodes",
    "neck swelling": "neck swelling",
    "thyroid swelling": "goiter", # Specific swelling
    "increased appetite": "polyphagia",
    "excessive hunger": "polyphagia",
    
    
    # Endocrine/Metabolic
    "heat intolerance": "heat intolerance",
    "cold intolerance": "cold intolerance",
    "excessive hunger": "polyphagia",
    "sugar craving": "polyphagia",

    # Reproductive System
    "irregular periods": "menstrual irregularities",
    "missed periods": "amenorrhea",
    "heavy periods": "menorrhagia",
    "pelvic pain": "pelvic pain",
    "painful periods": "dysmenorrhea",

    # Systemic / Generalized
    "flu-like symptoms": "flu-like symptoms",
    "malaise": "malaise",
    "general discomfort": "malaise",
    "inflammation": "inflammation",
    "swelling": "swelling",
    "edema": "swelling",
    "dehydration": "dehydration",
    "heat stroke": "heat exhaustion",
     "poor appetite": "anorexia",
    "unintentional weight loss": "weight loss",
    "night sweats": "night sweats", # Standardized as plural
    "chills": "chills",
    "body aches": "body ache",
    "flu like symptoms": "flu-like symptoms", # ensure hyphenated consistency
    "general aches": "body ache",
    "malaise": "malaise",
    "fainting spell": "syncope",
    "collapsed": "syncope", # Could imply syncopal episode
    "dizzy spell": "dizziness",
    "numbness and tingling": "paresthesia",
    "pins and needles sensation": "paresthesia",
    "weakness in arm": "muscle weakness",
    "weakness in leg": "muscle weakness",
    "burning in chest": "heartburn", # Could be reflux
    "swollen feet": "edema",
    "swollen ankles": "edema",
    "swollen face": "facial swelling",
    "rash on skin": "rash",
    "skin irritation": "skin irritation",
    "itchy rash": "pruritic rash",
    "blisters on skin": "blisters",
    "open sore": "ulcer",
    "lesion": "skin lesions",
    "lump": "lump",
    "mass": "lump",
    "bruise": "bruising",
    "swollen tongue": "tongue swelling",
    "dry mouth": "dry mouth",
    "excessive salivation": "sialorrhea",
    "difficulty moving": "mobility limitation",
    "stiffness": "stiffness", # General
    "trembling": "shaking",
    "shaking hands": "tremor", # More specific
    "involuntary movements": "involuntary movements",
    "loss of reflexes": "areflexia",
    "abnormal reflexes": "abnormal reflexes",
    "sensitivity to sound": "hyperacusis",
    "ringing ears": "tinnitus",
    "ear ache": "ear pain",
    "ear pressure": "ear fullness", # Consolidate
    "runny nose": "runny nose",
    "stuffy nose": "nasal congestion",
    "sneezing": "sneezing",
    "cough": "cough",
    "sore throat": "sore throat",
    "difficulty swallowing": "dysphagia",
    "hoarse voice": "hoarseness",
    "voice change": "hoarseness",
    "chest pain on breathing": "pleuritic pain",
    "shortness of breath at rest": "dyspnea",
    "worse shortness of breath with exertion": "dyspnea",
    "abdominal distention": "bloating",
    "gas and bloating": "bloating",
    "heartburn": "heartburn",
    "acid taste in mouth": "acid reflux",
    "reflux": "acid reflux",
    "nausea and vomiting": "nausea", # Prioritize Nausea if both
    "vomiting and diarrhea": "vomiting", # Prioritize Vomiting
    "frequent loose stools": "diarrhea",
    "abdominal cramps": "abdominal cramps",
    "constipation": "constipation",
    "bloody diarrhea": "bloody diarrhea",
    "mucus in stool": "mucus in stool",
    "jaundice": "jaundice",
    "dark urine": "urine discoloration",
    "pale urine": "urine discoloration",
    "frequent urination at night": "nocturia",
    "painful urination": "dysuria",
    "difficulty urinating": "dysuria", # Often implies pain or straining
    "urinary incontinence": "incontinence",
    "loss of bladder control": "incontinence",
    "genital itching": "genital itching",
    "vaginal itching": "genital itching",
    "penile itching": "genital itching",
    "rash in groin": "groin rash",
    "lesions on genitals": "genital ulcers",
    "swollen testicles": "testicular swelling",
    "vaginal bleeding": "vaginal bleeding",
    "intermenstrual bleeding": "menstrual irregularities",
    "pain during intercourse": "dyspareunia",
    "loss of libido": "sexual dysfunction",
    "erectile dysfunction": "sexual dysfunction",
    "hair thinning": "hair loss",
    "brittle nails": "nail changes",
    "skin dryness": "dry skin",
    "peeling skin": "skin peeling",
    "easy bruising": "bruising",
    "skin pallor": "pallor",
    "yellowing of skin": "jaundice",
    "yellowing of eyes": "jaundice",
    "rash with fever": "rash", # Still maps to 'rash', context is for ML
    "hives": "hives",
    "urticaria": "hives", # Medical term
    "skin bumps": "skin rash", # Map 'skin bumps' to the most commonly recognized equivalent
    "skin bump": "skin rash",  # Also map singular to the canonical
    "blister": "blisters",     # Keep this if 'blisters' is a valid canonical, or change to 'skin rash'/'skin lesions'
    "nodule": "skin lump",
     "skin lesions": "skin lesions", # Ensure this is present if used as canonical
    "red patches of skin": "red patches of skin", # This is also a canonical from your rules.
    "skin redness": "skin redness", 
    "skin lump": "skin lump",
    "blistering": "blisters",
    "swollen glands in neck": "swollen lymph nodes",
    "tender glands": "swollen lymph nodes",
    "fatigue with fever": "fatigue", # Context for ML
    "generalized fatigue": "fatigue",
    "profound fatigue": "fatigue",
    "chronic fatigue": "fatigue",
    "dizziness on standing": "orthostatic hypotension",
    "postural dizziness": "orthostatic hypotension",
    "vertigo attacks": "vertigo",
    "lightheaded": "lightheadedness", # Canonical consistency
    "head pressure": "headache",
    "sore eyes": "eye pain",
    "eye redness": "red eyes",
    "gritty eyes": "dry eyes",
    "blurred vision in one eye": "blurred vision",
    "tunnel vision": "vision loss",
    "hearing loss in one ear": "hearing loss",
    "ringing in one ear": "tinnitus",
    "muffled hearing": "hearing loss",
    "ear ache and fever": "ear pain", # Context for ML
    "mouth sores": "oral ulcers",
    "canker sore": "oral ulcers",
    "cold sore": "oral lesions", # Can be specific if you distinguish
    "gingivitis": "gum inflammation",
    "bleeding gums": "gum bleeding",
    "swollen gums": "gum swelling",
    "facial swelling": "facial swelling",
    "swollen lips": "lip swelling",
    "tongue swelling": "tongue swelling",
    "difficulty opening mouth": "trismus", # Lockjaw variant
    "soreness in jaw": "jaw pain",
    "numbness in face": "facial numbness",
    "tingling in face": "facial paresthesia",
    "facial droop": "facial weakness",
    "difficulty moving arm": "limited arm movement",
    "difficulty moving leg": "limited leg movement",
    "muscle spasms": "muscle spasms",
    "muscle weakness": "muscle weakness",
    "loss of sensation": "sensory loss",
    "abnormal sensations": "paresthesia",
    "difficulty speaking words": "dysphasia",
    "unable to speak": "aphasia",
    "loss of voice": "aphonia",
    "stuttering": "stuttering", # Keep distinct if in data
    "confusion and disorientation": "confusion",
    "memory problems": "memory impairment",
    "poor concentration": "cognitive dysfunction",
    "difficulty thinking": "cognitive dysfunction",
    "mood swings": "mood swings",
    "irritability and mood changes": "irritability",
    "agitation and restlessness": "agitation",
    "panic attacks": "panic attack",
    "anxiety and worry": "anxiety",
    "depression and sadness": "depression",
    "loss of pleasure": "anhedonia",
    "suicidal thoughts": "suicidal ideation", # Critical - requires handling outside this system
    "hallucinations": "hallucinations",
    "delusions": "delusions",
    "paranoid thoughts": "paranoia",
    "trouble sleeping": "insomnia",
    "difficulty falling asleep": "insomnia",
    "waking up frequently": "sleep disturbance",
    "excessive sleepiness": "hypersomnia",
    "daytime sleepiness": "hypersomnia",
    "sleep disturbance": "sleep disturbance",
    "low body temperature": "hypothermia",
    "cold hands and feet": "cold extremities",
    "sweating profusely": "hyperhidrosis",
    "dry mouth": "dry mouth",
    "metallic taste": "metallic taste in mouth",
    "excessive thirst": "polydipsia",
    "frequent urination": "polyuria",
    "increased hunger": "polyphagia",
    "blurred vision in diabetes": "blurred vision", # Context
    "numbness in feet in diabetes": "numbness", # Context
    "slow wound healing": "slow healing",
    "hair loss": "hair loss",
    "brittle nails": "nail changes",
    "muscle weakness": "muscle weakness",
    "joint stiffness in morning": "morning stiffness",
    "joint redness": "joint inflammation",
    "swelling around joints": "joint swelling",
    "skin rash and itching": "pruritic rash",
    "skin peeling": "skin peeling",
    "dry scaly skin": "scaling",
    "red patches": "erythema",
    "skin ulcer": "ulcer",
    "sores that won't heal": "non-healing ulcer",
    "fever and chills": "fever", # Prioritize fever, context for ML
    "runny nose and cough": "runny nose", # Prioritize first, context for ML
    "nausea and dizziness": "nausea", # Prioritize first, context for ML
    "chest pain on exertion": "chest pain", # Context
    "irregular heart rate": "arrhythmia",
    "skipped heart beats": "palpitations",
    "lightheadedness when standing": "orthostatic hypotension",
    "spinning sensation": "vertigo",
    "tremors": "tremor",
    "muscle twitching": "muscle fasciculations",
    "muscle spasms": "muscle spasms",
    "difficulty walking": "gait disturbance",
    "loss of balance": "balance problems",
    "coordination problems": "ataxia",
    "unsteady": "gait disturbance",
    "vision loss in one eye": "vision loss",
    "flashing lights in vision": "visual disturbances",
    "floaters in vision": "visual disturbances",
    "ringing in ears": "tinnitus",
    "ear pain": "ear pain",
    "ear discharge": "ear discharge",
    "nasal congestion": "nasal congestion",
    "sore throat": "sore throat",
    "hoarseness": "hoarseness",
    "difficulty swallowing": "dysphagia",
    "heartburn after eating": "heartburn",
    "acid reflux after meals": "acid reflux",
    "bloating after eating": "bloating",
    "stomach cramps and diarrhea": "abdominal cramps",
    "constipation and straining": "constipation",
    "blood in stool": "hematochezia",
    "dark tarry stools": "melena",
    "jaundice": "jaundice",
    "dark urine": "urine discoloration",
    "frequent urination and thirst": "polyuria", # Prioritize polyuria
    "painful urination": "dysuria",
    "blood in urine": "hematuria",
    "pelvic pain in women": "pelvic pain",
    "abnormal vaginal bleeding": "menstrual irregularities",
    "pain during sex": "dyspareunia",
    "genital rash": "genital rash",
    "lumps in breast": "breast lump",
    "nipple discharge": "nipple discharge",
    "swollen testicles": "testicular swelling",
    "penile discharge": "penile discharge",
    "prolonged fever": "fever",
    "recurrent fever": "fever",
    "chills and sweats": "chills",
    "general malaise": "malaise",
    "difficulty sleeping": "insomnia",
    "waking up at night": "sleep disturbance",
    "excessive daytime sleepiness": "hypersomnia",
    "low energy": "fatigue",
    "anxious thoughts": "anxiety",
    "nervous feelings": "anxiety",
    "feeling overwhelmed": "anxiety",
    "sadness": "depression",
    "loss of interest in hobbies": "anhedonia",
    "difficulty concentrating": "cognitive dysfunction",
    "brain fog": "cognitive dysfunction",
    "confusion and disorientation": "confusion",
    "memory loss": "memory impairment",
    "irritability and anger": "irritability",
    "paranoia": "paranoia",
    "seeing things": "hallucinations",
    "hearing voices": "hallucinations",
    "loss of balance": "balance problems",
    "unsteady walk": "gait disturbance",
    "numbness or tingling": "paresthesia",
    "shooting pains": "nerve pain",
    "muscle aches and pains": "myalgia",
    "joint pain and swelling": "arthralgia",
    "stiffness in joints": "joint stiffness",
    "skin discoloration": "skin discoloration",
    "pale skin": "pallor",
    "red patches on skin": "erythema",
    "itchy skin rash": "pruritic rash",
    "peeling skin on hands": "skin peeling",
    "hair thinning": "hair loss",
    "brittle nails": "nail changes",
    "swollen feet and ankles": "edema",
    "swollen lymph nodes in groin": "swollen lymph nodes",
    "excessive thirst and urination": "polyuria",
    "unexplained weight loss": "weight loss",
    "increased hunger": "polyphagia",
    "cold intolerance": "cold intolerance",
    "heat intolerance": "heat intolerance",
    "swollen thyroid": "goiter",
    "dry mouth and eyes": "dry mouth", # Prioritize dry mouth
    "metallic taste in mouth": "metallic taste in mouth",
    "changes in taste": "dysgeusia",
    "loss of taste": "ageusia",
    "bad breath": "halitosis",
    "frequent infections": "recurrent infections",
    "slow healing wounds": "slow healing",
    "night sweats": "night sweats",
    "chills and fever": "chills",
    "general discomfort": "malaise",
    "feeling tired all the time": "fatigue",
    "constant fatigue": "fatigue",
    "exhaustion": "fatigue",
    "dizziness and lightheadedness": "dizziness",
    "vertigo and nausea": "vertigo",
    "chest pressure": "chest pain",
    "heart palpitations": "heart palpitations",
    "shortness of breath on exertion": "dyspnea",
    "cough with phlegm": "cough",
    "sore throat and cough": "sore throat",
    "stuffy nose and headache": "nasal congestion",
    "abdominal bloating and gas": "bloating",
    "stomach cramps and nausea": "abdominal cramps",
    "constipation and abdominal pain": "constipation",
    "diarrhea and fever": "diarrhea",
    "blood in stool with diarrhea": "bloody diarrhea",
    "jaundice and dark urine": "jaundice",
    "painful and frequent urination": "dysuria",
    "blood in urine and pain": "hematuria",
    "pelvic pain and discharge": "pelvic pain",
    "irregular periods and heavy bleeding": "menstrual irregularities",
    "skin rash and itching": "pruritic rash",
    "skin lesions and pain": "skin lesions",
    "dry cracked skin": "dry skin",
    "hair loss and thinning": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swollen feet and legs": "edema",
    "swollen lymph nodes in neck": "swollen lymph nodes",
    "increased thirst and hunger": "polydipsia",
    "weight loss despite eating": "weight loss",
    "fatigue and weakness": "fatigue",
    "muscle aches and joint pain": "myalgia",
    "joint swelling and stiffness": "joint swelling",
    "numbness and tingling in hands": "paresthesia",
    "muscle cramps and spasms": "muscle cramps",
    "difficulty walking and balance problems": "gait disturbance",
    "vision changes and blurred vision": "blurred vision",
    "eye pain and redness": "eye pain",
    "ear pain and discharge": "ear pain",
    "ringing in ears and hearing loss": "tinnitus",
    "sore throat and difficulty swallowing": "sore throat",
    "hoarse voice and cough": "hoarseness",
    "chest tightness and wheezing": "chest tightness",
    "abdominal pain and vomiting": "abdominal pain",
    "nausea and diarrhea": "nausea",
    "frequent urination and painful urination": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and pain": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and redness": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry skin": "nail changes",
    "swelling and pain": "swelling",
    "lymph node swelling and fever": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and fatigue": "muscle weakness",
    "joint pain and stiffness": "arthralgia",
    "numbness and tingling in feet": "paresthesia",
    "difficulty walking and falling": "gait disturbance",
    "blurred vision and eye pain": "blurred vision",
    "earache and hearing loss": "ear pain",
    "nasal congestion and runny nose": "nasal congestion",
    "sore throat and difficulty talking": "sore throat",
    "chest pain and shortness of breath": "chest pain",
    "abdominal pain and diarrhea": "abdominal pain",
    "nausea and vomiting": "nausea",
    "frequent urination and urgency": "urinary urgency",
    "vaginal itching and discharge": "genital itching",
    "genital sores and itching": "genital ulcers",
    "skin rash and body aches": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and redness": "swelling",
    "lymph node swelling and pain": "swollen lymph nodes",
    "excessive thirst and dry mouth": "polydipsia",
    "unexplained weight loss and increased hunger": "weight loss",
    "muscle weakness and muscle aches": "muscle weakness",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "ggait disturbance", # Typo here
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "chest pain and cough": "chest pain",
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and muscle aches": "muscle weakness",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "gait disturbance",
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "chest pain and cough": "chest pain",
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and muscle aches": "muscle weakness",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "gait disturbance", # Typo fixed from 'ggait disturbance'
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "chest pain and cough": "chest pain",
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and muscle aches": "muscle weakness",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "gait disturbance", # Corrected typo
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "chest pain and cough": "chest pain",
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and muscle aches": "muscle weakness",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "gait disturbance", # Corrected typo
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "chest pain and cough": "chest pain",
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and urination": "polydipsia",
    "unexplained weight loss and fatigue": "weight loss",
    "muscle weakness and muscle aches": "muscle aches",
    "joint pain and swelling": "arthralgia",
    "numbness and tingling in hands and feet": "paresthesia",
    "difficulty walking and balance problems": "gait disturbance",
    "blurred vision and light sensitivity": "blurred vision",
    "ear pain and ringing": "ear pain",
    "nasal congestion and sore throat": "nasal congestion",
    "sore throat and hoarseness": "sore throat",
    "chest tightness and cough": "chest tightness",
    "abdominal pain and constipation": "abdominal pain",
    "nausea and heartburn": "nausea",
    "frequent urination and blood in urine": "polyuria",
    "vaginal discharge and pelvic pain": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and joint pain": "rash",
    "itchy skin and swelling": "pruritus",
    "hair loss and fatigue": "hair loss",
    "brittle nails and dry hair": "nail changes",
    "swelling and warmth": "swelling",
    "lymph node swelling and tenderness": "swollen lymph nodes",
    "excessive thirst and polyuria": "polydipsia",
    "unexplained weight loss and frequent urination": "weight loss",
    "muscle weakness and joint pain": "muscle weakness",
    "joint pain and redness": "arthralgia",
    "numbness and tingling in face": "facial numbness",
    "difficulty walking and numbness": "gait disturbance",
    "blurred vision and double vision": "blurred vision",
    "ear pain and fullness": "ear pain",
    "nasal congestion and facial pain": "nasal congestion",
    "sore throat and difficulty swallowing": "sore throat",
    "chest pain and palpitations": "chest pain",
    "abdominal pain and nausea": "abdominal pain",
    "frequent urination and pelvic pain": "polyuria",
    "vaginal discharge and painful intercourse": "vaginal discharge",
    "genital sores and discharge": "genital ulcers",
    "skin rash and swelling": "rash",
    "itchy skin and warmth": "pruritus",
    "hair loss and dry skin": "hair loss",
    "brittle nails and hair loss": "nail changes",
    "swelling and discoloration": "swelling",
    "lymph node swelling and redness": "swollen lymph nodes",
    "excessive thirst and weight loss": "polydipsia",
    "unexplained weight gain and fatigue": "weight gain",
    "muscle weakness and stiffness": "muscle weakness",
    "joint pain and limited movement": "arthralgia",
    "numbness and tingling in arm": "paresthesia",
    "difficulty walking and muscle weakness": "gait disturbance", 
    
    "blurred vision and headaches": "blurred vision",
    "ear pain and ringing in ears": "ear pain",
    "nasal congestion and sneezing": "nasal congestion",
    "sore throat and swollen glands": "sore throat",
    "dry eyes": "dry eyes",  
    "chest pain and cough": "chest pain",
    "high temperature": "fever", 
    "feverish": "fever",  
    "abdominal pain and vomiting": "abdominal pain",
    "frequent urination and urgency": "polyuria",
    "vaginal discharge and itching": "vaginal discharge",
    "genital sores and itching": "genital ulcers",
    "skin rash and fever": "rash",
    "itchy skin and dry skin": "pruritus",
    "hair loss and brittle nails": "hair loss",
    "swelling and pain": "swelling",
     "throwing up": "vomiting",  # Map "throwing up" (user input) to canonical "vomiting"
    "spitting up": "vomiting",  # Another potential synonym to add
    "vomiting blood": "hematemesis", # Keep this as you have it, if 'hematemesis' is a separate canonical
    "vomiting": "vomiting", 
    "lymph node swelling and tenderness": "swollen lymph nodes",

    # Rare/Niche
    "lockjaw": "jaw stiffness",
    "muscle wasting": "muscle atrophy",
    "clumsiness": "coordination problems",
    "unsteady gait": "balance problems",
    "loss of coordination": "ataxia",
    "flushing": "skin flushing",
    "excessive sweating": "hyperhidrosis",
    "frequent infections": "recurrent infections",
}

# --- Expert System Rules: Critical Symptoms for Specific Diseases ---
# This dictionary maps a normalized disease name to a list of its critical normalized symptoms.
# If a disease is predicted by the ML model, and these critical symptoms are present in the user's input,
# it can reinforce the prediction. This is a simple rule. More complex rules (e.g., scoring, exclusions)
# could be added.
CRITICAL_SYMPTOMS_RULES = {
   'malaria': ['fever', 'high temperature', 'headache', 'vomiting', 'chills'],
    'common cold': ['runny nose', 'sore throat', 'cough', 'sneezing', 'nasal congestion'],
    'influenza': ['fever', 'high temperature', 'body ache', 'cough', 'fatigue', 'chills'],
    'dengue': ['high fever', 'joint pain', 'rash', 'nausea', 'muscle ache'],
    'chicken pox': ['rash', 'fever', 'itchy skin', 'blisters'],
    'jaundice': ['yellow skin', 'yellow eyes', 'dark urine', 'fatigue'],
    'hepatitis a': ['fatigue', 'nausea', 'abdominal pain', 'yellow skin'],
    'typhoid': ['fever', 'headache', 'abdominal pain', 'weakness', 'loss of appetite'],
    'tuberculosis': ['persistent cough', 'weight loss', 'night sweats', 'fever', 'chest pain'],
    'pneumonia': ['cough', 'fever', 'shortness of breath', 'chest pain', 'fatigue'],
    'covid-19': ['fever', 'dry cough', 'fatigue', 'loss of taste', 'loss of smell', 'breathlessness'],
    'measles': ['high fever', 'runny nose', 'red eyes', 'rash', 'cough'],
    'hepatitis b': ['fatigue', 'abdominal pain', 'loss of appetite', 'joint pain', 'jaundice'],
    'hiv': ['fever', 'swollen lymph nodes', 'sore throat', 'rash', 'muscle aches'],
    'lyme disease': ['rash', 'fever', 'fatigue', 'headache', 'joint pain'],
    'meningitis': ['fever', 'stiff neck', 'headache', 'nausea', 'light sensitivity'],
    'bronchitis': ['cough', 'mucus production', 'fatigue', 'shortness of breath', 'chest discomfort'],
    'sinusitis': ['facial pain', 'nasal congestion', 'headache', 'postnasal drip'],
    'otitis media': ['ear pain', 'fever', 'hearing loss', 'ear drainage'],
    'asthma': ['shortness of breath', 'wheezing', 'chest tightness', 'coughing'],
    'gastroenteritis': ['diarrhea', 'vomiting', 'abdominal cramps', 'fever', 'nausea'],
    'peptic ulcer': ['burning stomach pain', 'bloating', 'nausea', 'heartburn'],
    'appendicitis': ['abdominal pain', 'nausea', 'loss of appetite', 'fever'],
    'gallstones': ['abdominal pain', 'nausea', 'vomiting', 'jaundice'],
    'kidney stones': ['severe flank pain', 'nausea', 'blood in urine', 'frequent urination'],
    'urinary tract infection': ['burning urination', 'frequent urination', 'pelvic pain', 'cloudy urine'],
    'anemia': ['fatigue', 'pale skin', 'shortness of breath', 'dizziness'],
    'diabetes': ['increased thirst', 'frequent urination', 'unexplained weight loss', 'fatigue'],
    'hypertension': ['headache', 'blurred vision', 'chest pain', 'nosebleeds'],
    'hypothyroidism': ['fatigue', 'weight gain', 'cold intolerance', 'dry skin'],
    'hyperthyroidism': ['weight loss', 'rapid heartbeat', 'nervousness', 'sweating'],
    'rheumatoid arthritis': ['joint pain', 'joint swelling', 'morning stiffness', 'fatigue'],
    'lupus': ['joint pain', 'skin rash', 'fatigue', 'fever', 'light sensitivity'],
    'psoriasis': ['red patches of skin', 'silvery scales', 'itching', 'joint pain'],
    'migraine': ['severe headache', 'nausea', 'light sensitivity', 'visual disturbances'],
    'epilepsy': ['seizures', 'confusion', 'loss of consciousness', 'staring spells'],
    'stroke': ['sudden numbness', 'confusion', 'speech difficulty', 'loss of balance', 'severe headache'],
    'heart attack': ['chest pain', 'shortness of breath', 'nausea', 'pain in left arm', 'sweating'],
    'allergic rhinitis': ['sneezing', 'runny nose', 'nasal congestion', 'itchy eyes'],
    'eczema': ['itchy skin', 'red rash', 'dry skin', 'skin cracking'],
    'food poisoning': ['vomiting', 'diarrhea', 'stomach cramps', 'nausea', 'fever'],
    'tonsillitis': ['sore throat', 'fever', 'difficulty swallowing', 'swollen tonsils'],
    'gout': ['joint pain', 'joint swelling', 'redness', 'warmth in joint'],
    'polio': ['fever', 'fatigue', 'headache', 'stiff neck', 'muscle weakness'],
    'whooping cough': ['severe coughing', 'whooping sound', 'vomiting', 'runny nose'],
    'cholera': ['watery diarrhea', 'vomiting', 'dehydration', 'leg cramps'],
    'zika virus': ['fever', 'rash', 'joint pain', 'conjunctivitis', 'headache'],
    'yellow fever': ['fever', 'chills', 'muscle pain', 'nausea', 'vomiting', 'jaundice'],
    'ebola': ['fever', 'severe headache', 'muscle pain', 'vomiting', 'unexplained bleeding'],
    'rabies': ['fever', 'headache', 'excessive salivation', 'muscle spasms', 'paralysis'],
    'mononucleosis': ['extreme fatigue', 'sore throat', 'swollen lymph nodes', 'fever', 'headache'],
    'fibromyalgia': ['widespread pain', 'fatigue', 'sleep disturbance', 'cognitive dysfunction'],
    'celiac disease': ['diarrhea', 'abdominal pain', 'bloating', 'weight loss', 'fatigue', 'malabsorption'],
    'crohns disease': ['abdominal pain', 'diarrhea', 'weight loss', 'fever', 'fatigue', 'bloody stools'],
    'ulcerative colitis': ['bloody diarrhea', 'abdominal pain', 'rectal bleeding', 'fatigue', 'weight loss'],
    'diverticulitis': ['abdominal pain', 'fever', 'nausea', 'constipation', 'bloating', 'tenderness in left lower abdomen'],
    'peripheral artery disease': ['leg pain with exertion', 'leg numbness', 'leg weakness', 'cold feet', 'non-healing sores on feet'], # PAD
    'deep vein thrombosis': ['leg pain', 'leg swelling', 'redness', 'warmth in leg'], # DVT
    'pulmonary embolism': ['sudden shortness of breath', 'chest pain', 'cough', 'rapid heartbeat', 'dizziness'], # PE - Medical emergency
    'addisons disease': ['fatigue', 'weight loss', 'nausea', 'vomiting', 'abdominal pain', 'darkening of skin'], # Adrenal insufficiency
    'bells palsy': ['facial weakness', 'facial droop', 'difficulty closing eye', 'loss of taste'],
    'trigeminal neuralgia': ['severe facial pain', 'electric shock sensation', 'pain triggered by touch'],
    'gastroesophageal reflux disease': ['heartburn', 'regurgitation', 'chest pain', 'dysphagia', 'acid reflux', 'halitosis'], # Adding this explicitly
    'irritable bowel syndrome': ['abdominal pain', 'bloating', 'diarrhea', 'constipation', 'change in bowel habits'], # IBS
    'anaphylaxis': ['difficulty breathing', 'hives', 'swelling of face/throat', 'rapid heartbeat', 'dizziness', 'low blood pressure'], # Severe allergic reaction - Medical emergency
    'sepsis': ['fever', 'chills', 'rapid heartbeat', 'confusion', 'shortness of breath', 'extreme pain'], # Life-threatening infection - Medical emergency
    'lupus': ['arthralgia', 'skin rash', 'fatigue', 'fever', 'photosensitivity', 'butterfly rash'], # Enhanced, specified 'butterfly rash'
    'sjogrens syndrome': ['dry eyes', 'dry mouth', 'fatigue', 'joint pain', 'swollen glands'], # Autoimmune
    'ankylosing spondylitis': ['back pain', 'stiffness in back', 'worse pain at rest', 'improved with exercise', 'fatigue'], # Autoimmune, specific back pain pattern
    'parkinsons disease': ['tremor', 'bradykinesia', 'rigidity', 'postural instability', 'gait disturbance'], # Neurological, used 'bradykinesia', 'rigidity'
    'multiple sclerosis': ['fatigue', 'numbness', 'tingling', 'muscle weakness', 'vision changes', 'balance problems', 'vertigo'], # Neurological
    'dementia': ['memory impairment', 'confusion', 'disorientation', 'difficulty concentrating', 'speech difficulty', 'personality changes'], # Neurological
    'schizophrenia': ['hallucinations', 'delusions', 'disorganized speech', 'social withdrawal', 'impaired cognitive function'], # Mental Health (be cautious with ML for this)
    'bipolar disorder': ['mood swings', 'mania', 'depression', 'changes in energy levels', 'sleep disturbance'], # Mental Health
    'panic disorder': ['panic attack', 'rapid heartbeat', 'shortness of breath', 'chest pain', 'dizziness', 'fear of dying'], # Mental Health, specific attack
    'post-traumatic stress disorder': ['flashbacks', 'nightmares', 'avoidance', 'hypervigilance', 'mood swings', 'anxiety'], # Mental Health
    'cirrhosis': ['fatigue', 'nausea', 'weight loss', 'jaundice', 'edema', 'ascites'], # Liver condition, used 'ascites' (abdominal fluid)
    'gout': ['arthralgia', 'joint swelling', 'erythema', 'warmth in joint', 'uric acid crystals'], # Emphasized 'uric acid crystals' if available
    'c diff infection': ['severe diarrhea', 'abdominal cramps', 'fever', 'nausea', 'recent antibiotic use'], # Infectious, specific to antibiotic history
    'mastitis': ['breast pain', 'breast redness', 'breast swelling', 'fever', 'chills'], # Women's health
    'endometriosis': ['pelvic pain', 'painful periods', 'pain during intercourse', 'heavy periods', 'infertility'], # Women's health
    'polycystic ovary syndrome': ['irregular periods', 'acne', 'hirsutism', 'weight gain', 'hair loss'], # Women's health (PCOS)
    'benign prostatic hyperplasia': ['frequent urination', 'difficulty urinating', 'weak urine stream', 'nocturia', 'urinary urgency'], # Men's health (BPH)
    'prostatitis': ['pelvic pain', 'painful urination', 'frequent urination', 'painful ejaculation', 'fever'], # Men's health
    'migraine with aura': ['severe headache', 'visual disturbances', 'nausea', 'light sensitivity', 'phonophobia', 'aura'], # Specific migraine type
    'tension headache': ['headache', 'head pressure', 'neck pain', 'muscle tension'], # Common headache
    'cluster headache': ['severe headache', 'eye pain', 'tearing', 'nasal congestion', 'eye redness', 'restlessness'], # Distinct headache type
    'fibrocystic breast changes': ['breast pain', 'breast lumps', 'breast tenderness', 'lumpiness worse before period'], # Women's health
    'galactorrhea': ['nipple discharge', 'milky discharge from nipple'], # Endocrine/Reproductive
    'renal failure chronic': ['fatigue', 'nausea', 'loss of appetite', 'edema', 'changes in urination', 'pruritus'], # Kidney disease
    'glomerulonephritis': ['blood in urine', 'dark urine', 'swelling', 'hypertension', 'fatigue'], # Kidney disease
    'polycystic kidney disease': ['back pain', 'abdominal pain', 'hematuria', 'hypertension', 'frequent urination'], # Kidney disease
    'chronic fatigue syndrome': ['severe fatigue', 'sleep disturbance', 'post-exertional malaise', 'muscle aches', 'joint pain', 'cognitive dysfunction'], # Distinct fatigue syndrome
    'vertigo benign paroxysmal positional': ['vertigo', 'dizziness with head movement', 'nausea', 'nystagmus'], # Specific type of vertigo
    'menieres disease': ['vertigo', 'tinnitus', 'hearing loss', 'ear fullness'], # Inner ear disorder
    'hypoglycemia': ['dizziness', 'shaking', 'sweating', 'confusion', 'hunger', 'rapid heartbeat'], # Low blood sugar
    'hyperglycemia': ['increased thirst', 'frequent urination', 'fatigue', 'blurred vision', 'sweet breath odor'], # High blood sugar
    'thyroiditis': ['neck pain', 'thyroid swelling', 'fever', 'fatigue', 'symptoms of hyper/hypothyroidism'], # Thyroid inflammation
    'herpes simplex': ['oral lesions', 'genital ulcers', 'blisters', 'painful sores', 'itching'], # Viral infection
    'shingles': ['painful rash', 'blisters', 'burning pain', 'itching', 'unilateral rash', 'nerve pain'], # Reactivated varicella zoster
    'impetigo': ['skin blisters', 'crusted sores', 'itchy skin', 'red patches of skin'], # Bacterial skin infection
    'cellulitis': ['skin redness', 'skin swelling', 'warmth in skin', 'skin tenderness', 'fever'], # Bacterial skin infection
    'mrsa infection': ['skin boil', 'skin abscess', 'redness', 'swelling', 'warmth in skin', 'fever'], # Specific bacterial infection (skin)
    'gingivitis': ['gum inflammation', 'gum bleeding', 'bad breath'], # Oral health
    'periodontitis': ['gum bleeding', 'gum inflammation', 'loose teeth', 'bad breath', 'gum recession'], # Oral health
    'halitosis primary': ['bad breath', 'dry mouth', 'white coating on tongue'], # Direct rule for chronic bad breath
    
    

    # ---- Additional Diseases ----
    'bronchitis': ['cough', 'mucus production', 'fatigue', 'shortness of breath', 'chest discomfort'],
    'sinusitis': ['facial pain', 'nasal congestion', 'headache', 'postnasal drip'],
    'otitis media': ['ear pain', 'fever', 'hearing loss', 'ear drainage'],
    'asthma': ['shortness of breath', 'wheezing', 'chest tightness', 'coughing'],
    'gastroenteritis': ['diarrhea', 'vomiting', 'abdominal cramps', 'fever', 'nausea'],
    'peptic ulcer': ['burning stomach pain', 'bloating', 'nausea', 'heartburn'],
    'appendicitis': ['abdominal pain', 'nausea', 'loss of appetite', 'fever'],
    'gallstones': ['abdominal pain', 'nausea', 'vomiting', 'jaundice'],
    'kidney stones': ['severe flank pain', 'nausea', 'blood in urine', 'frequent urination'],
    'urinary tract infection': ['burning urination', 'frequent urination', 'pelvic pain', 'cloudy urine'],
    'anemia': ['fatigue', 'pale skin', 'shortness of breath', 'dizziness'],
    'diabetes mellitus': ['increased thirst', 'frequent urination', 'unexplained weight loss', 'fatigue'],
    'hypertension': ['headache', 'blurred vision', 'chest pain', 'nosebleeds'],
    'hypothyroidism': ['fatigue', 'weight gain', 'cold intolerance', 'dry skin'],
    'hyperthyroidism': ['weight loss', 'rapid heartbeat', 'nervousness', 'sweating'],
    'rheumatoid arthritis': ['joint pain', 'joint swelling', 'morning stiffness', 'fatigue'],
    'lupus': ['joint pain', 'skin rash', 'fatigue', 'fever', 'photosensitivity'],
    'psoriasis': ['red patches of skin', 'silvery scales', 'itching', 'joint pain (psoriatic arthritis)'],
    'migraine': ['severe headache', 'nausea', 'sensitivity to light', 'visual disturbances'],
    'epilepsy': ['seizures', 'confusion', 'loss of consciousness', 'staring spells'],
    'stroke': ['sudden numbness', 'confusion', 'trouble speaking', 'loss of balance', 'severe headache'],
    'heart attack': ['chest pain', 'shortness of breath', 'nausea', 'pain in left arm or jaw', 'sweating'],
    'angina': ['chest pain', 'shortness of breath', 'nausea', 'fatigue'],
    'congestive heart failure': ['shortness of breath', 'fatigue', 'swelling in legs', 'rapid weight gain'],
    'pericarditis': ['sharp chest pain', 'fever', 'fatigue', 'shortness of breath'],
    'gastroesophageal reflux disease': ['heartburn', 'chest pain', 'regurgitation', 'difficulty swallowing'],
    'pancreatitis': ['abdominal pain', 'nausea', 'vomiting', 'fever'],
    'hepatitis c': ['fatigue', 'joint pain', 'abdominal pain', 'jaundice'],
    'hepatitis e': ['fever', 'nausea', 'abdominal pain', 'jaundice'],
    'cholangitis': ['fever', 'jaundice', 'right upper abdominal pain', 'chills'],
    'cirrhosis': ['fatigue', 'jaundice', 'abdominal swelling', 'easy bruising'],
    'celiac disease': ['diarrhea', 'weight loss', 'bloating', 'fatigue'],
    'irritable bowel syndrome': ['abdominal pain', 'bloating', 'diarrhea', 'constipation'],
    'crohn’s disease': ['abdominal pain', 'diarrhea', 'weight loss', 'fatigue'],
    'ulcerative colitis': ['bloody diarrhea', 'abdominal cramps', 'weight loss', 'fatigue'],
    'glomerulonephritis': ['blood in urine', 'facial swelling', 'high blood pressure', 'fatigue'],
    'nephrotic syndrome': ['swelling in legs', 'protein in urine', 'fatigue', 'weight gain'],
    'prostatitis': ['pelvic pain', 'painful urination', 'frequent urination', 'fever'],
    'benign prostatic hyperplasia': ['frequent urination', 'weak urine stream', 'incomplete emptying', 'nocturia'],
    'polycystic ovarian syndrome': ['irregular periods', 'acne', 'weight gain', 'excess hair growth'],
    'endometriosis': ['pelvic pain', 'painful periods', 'pain during intercourse', 'infertility'],
    'pelvic inflammatory disease': ['pelvic pain', 'vaginal discharge', 'fever', 'painful intercourse'],
    'ovarian cysts': ['pelvic pain', 'bloating', 'pain during intercourse', 'frequent urination'],
    'bacterial vaginosis': ['vaginal discharge', 'fishy odor', 'itching', 'burning urination'],
    'cervical cancer': ['abnormal bleeding', 'pelvic pain', 'pain during intercourse', 'vaginal discharge'],
    'prostate cancer': ['difficulty urinating', 'weak urine stream', 'blood in urine', 'pelvic discomfort'],
    'breast cancer': ['breast lump', 'breast pain', 'nipple discharge', 'skin dimpling'],
    'lung cancer': ['persistent cough', 'chest pain', 'coughing up blood', 'weight loss'],
    'leukemia': ['fatigue', 'frequent infections', 'bruising easily', 'pale skin'],
    'lymphoma': ['swollen lymph nodes', 'night sweats', 'weight loss', 'fatigue'],
    'multiple sclerosis': ['vision problems', 'muscle weakness', 'numbness', 'balance issues'],
    'parkinson’s disease': ['tremor', 'muscle rigidity', 'slow movements', 'balance problems'],
    'alzheimer’s disease': ['memory loss', 'confusion', 'difficulty speaking', 'personality changes'],
    'amyotrophic lateral sclerosis': ['muscle weakness', 'difficulty speaking', 'difficulty swallowing', 'muscle cramps'],
    'chronic obstructive pulmonary disease': ['chronic cough', 'shortness of breath', 'wheezing', 'fatigue'],
    'sleep apnea': ['loud snoring', 'daytime sleepiness', 'gasping during sleep', 'morning headache'],
    'mononucleosis': ['fatigue', 'sore throat', 'swollen lymph nodes', 'fever'],
    'ebola': ['fever', 'bleeding', 'severe headache', 'muscle pain'],
    'zika virus': ['fever', 'rash', 'joint pain', 'conjunctivitis'],
    'cholera': ['severe diarrhea', 'vomiting', 'dehydration', 'muscle cramps'],
    'leptospirosis': ['high fever', 'muscle aches', 'red eyes', 'jaundice'],
    'schistosomiasis': ['rash', 'fever', 'chills', 'muscle aches'],
    'filariasis': ['swelling in limbs', 'fever', 'skin thickening', 'lymph node swelling'],
    'onchocerciasis': ['itchy skin', 'skin nodules', 'vision changes', 'rash'],
    'toxoplasmosis': ['fever', 'swollen lymph nodes', 'muscle aches', 'blurred vision'],
    'giardiasis': ['diarrhea', 'abdominal cramps', 'bloating', 'nausea'],
    'amoebiasis': ['bloody diarrhea', 'abdominal pain', 'fever', 'weight loss'],
    'trichomoniasis': ['vaginal discharge', 'itching', 'painful urination', 'discomfort during intercourse'],
    'syphilis': ['painless sore', 'skin rash', 'fever', 'swollen lymph nodes'],
    'gonorrhea': ['painful urination', 'discharge', 'pelvic pain', 'testicular pain'],
    'chlamydia': ['painful urination', 'discharge', 'pelvic pain', 'bleeding after intercourse'],
    'herpes simplex virus': ['painful sores', 'itching', 'fever', 'swollen glands'],
    'human papillomavirus': ['genital warts', 'itching', 'bleeding after intercourse'],
    'scabies': ['intense itching', 'rash', 'burrow tracks', 'skin sores'],
    'lice infestation': ['itchy scalp', 'visible nits', 'red bumps on scalp', 'irritability'],
    'eczema': ['dry skin', 'itching', 'red patches', 'skin cracking'],
    'dermatitis': ['red rash', 'itching', 'swelling', 'blisters'],
    'vitiligo': ['loss of skin color', 'white patches', 'premature graying of hair'],
    'acne vulgaris': ['pimples', 'blackheads', 'whiteheads', 'skin inflammation'],
}


# --- Helper Functions (Cleaning & Normalization) ---
def clean_text(text: Union[str, Any]) -> Optional[str]:
    """Lowercase, strip spaces, and remove special characters."""
    if pd.isna(text) or text is None: # Added check for None
        return None
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_and_remove_stopwords(text: str) -> str:
    """Tokenize, lemmatize, and remove stopwords."""
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return ' '.join(tokens)

def normalize_symptom_name(symptom_name: str) -> Optional[str]:
    """Normalize symptom name with synonym mapping and NLP preprocessing."""
    if not symptom_name:
        return None
    cleaned = clean_text(symptom_name.replace('_', ' '))
    if not cleaned: # Handle cases where cleaning results in empty string
        return None
    lemmatized = lemmatize_and_remove_stopwords(cleaned)
    return SYMPTOM_SYNONYMS.get(lemmatized, lemmatized)



_symscan_classifier = None
_symscan_unique_symptoms = None
_symscan_unique_diseases = None
_symscan_int_to_disease = None
_symscan_precautions_map = None

def load_symscan_resources():
    """
    Loads all SymScan related models and auxiliary data.
    Raises RuntimeError if any essential file is missing or loading fails.
    """
    global _symscan_classifier, _symscan_unique_symptoms, _symscan_unique_diseases, _symscan_int_to_disease, _symscan_precautions_map
    if _symscan_classifier is None: # Load only if not already loaded
        try:
            _symscan_classifier = joblib.load(SYMSCAN_MODEL_PATH)
            _symscan_unique_symptoms = joblib.load(UNIQUE_SYMPTOMS_PATH)
            _symscan_unique_diseases = joblib.load(UNIQUE_DISEASES_PATH)
            _symscan_int_to_disease = joblib.load(INT_TO_DISEASE_MAP_PATH)
            _symscan_precautions_map = joblib.load(PRECAUTIONS_MAP_PATH)
            logger.info("SymScan models and auxiliary data loaded successfully by symscan_prediction module.")
        except FileNotFoundError as e:
            logger.error(f"SymScan model file not found in prediction module: {e}. Ensure training script was run and files exist at {os.path.dirname(SYMSCAN_MODEL_PATH)}")
            raise RuntimeError(f"SymScan model files are missing: {e}")
        except Exception as e:
            logger.error(f"Error loading SymScan models in prediction module: {e}")
            raise RuntimeError(f"Failed to load SymScan models: {e}")

# --- Main Prediction Function ---
def predict_symscan(raw_symptoms: List[str]) -> Dict[str, Any]:
    global _symscan_classifier, _symscan_unique_symptoms, _symscan_int_to_disease, _symscan_precautions_map

    # Ensure models are loaded
    if _symscan_classifier is None:
        try:
            load_symscan_resources() # Attempt to load if not already loaded
        except RuntimeError as e:
            logger.error(f"Failed to load SymScan resources in predict_symscan: {e}")
            return {
                "error": "SymScan model not available. Please contact support.",
                "details": str(e),
                "medical_disclaimer": "System is informational only, not substitute for professional medical advice."
            }

    MIN_CONFIDENCE_THRESHOLD = 0.50
    TOP_N_PREDICTIONS = 5 # Increased to 5 to show more potential diseases

    normalized_user_symptoms_present = set() # Renamed for clarity: symptoms actually used by the model
    unrecognized_symptoms_list = []

    for sym_raw in raw_symptoms:
        normalized_sym = normalize_symptom_name(sym_raw)
        if normalized_sym:
            if normalized_sym in _symscan_unique_symptoms:
                normalized_user_symptoms_present.add(normalized_sym)
            else:
                unrecognized_symptoms_list.append(f"'{sym_raw}' (normalized to '{normalized_sym}' but not in model vocabulary)")
                logger.warning(f"SymScan: Symptom '{sym_raw}' normalized to '{normalized_sym}' not in training vocabulary.")
        else:
            unrecognized_symptoms_list.append(f"'{sym_raw}' (could not be normalized)")
            logger.warning(f"SymScan: Could not normalize symptom: '{sym_raw}'")

    if not normalized_user_symptoms_present:
        return {
            "error": "No recognizable symptoms given after normalization. Please check your input.",
            "provided_symptoms": raw_symptoms,
            "unrecognized_symptoms": unrecognized_symptoms_list,
            "medical_disclaimer": "System is informational only, not medical advice."
        }

    logger.info(f"SymScan: Normalized symptoms used for prediction: {normalized_user_symptoms_present}")

    # Create input vector for the ML model
    input_vector = [1 if sym in normalized_user_symptoms_present else 0 for sym in _symscan_unique_symptoms]
    input_df = pd.DataFrame([input_vector], columns=list(_symscan_unique_symptoms)) # Ensure unique_symptoms is a list for DataFrame columns

    # --- ML Model Prediction ---
    prediction_proba_array = None
    try:
        # Get probabilities for all diseases
        prediction_proba_array = _symscan_classifier.predict_proba(input_df)[0]
    except AttributeError:
        logger.warning("SymScan classifier missing predict_proba, confidence unavailable. Cannot apply hybrid rules effectively.")

    primary_predicted_disease = "Uncertain Diagnosis"
    primary_confidence = None
    top_predictions = []

    if prediction_proba_array is not None:
        # Get top N predictions from ML model
        # Sort indices by probability in descending order
        sorted_indices = prediction_proba_array.argsort()[::-1]

        ml_raw_predictions = []
        for idx in sorted_indices:
            disease_name = _symscan_int_to_disease.get(idx, "Unknown Disease")
            conf = prediction_proba_array[idx]
            ml_raw_predictions.append({"disease": disease_name, "confidence": conf})

        logger.info(f"SymScan: ML Raw Top Predictions: {ml_raw_predictions[:TOP_N_PREDICTIONS]}")

        # --- Hybrid Logic: Apply Expert System Rules ---
        final_predictions_candidates = []
        for pred in ml_raw_predictions:
            disease = pred['disease']
            confidence = pred['confidence']
            rule_validation_score = 0 # Can be adjusted (e.g., 1 for match, 0 for no match)

            if disease in CRITICAL_SYMPTOMS_RULES:
                critical_symptoms_for_disease = set(CRITICAL_SYMPTOMS_RULES[disease])
                # Check if all critical symptoms for this disease are present in user's input
                if critical_symptoms_for_disease.issubset(normalized_user_symptoms_present):
                    rule_validation_score = 1 # Rule matched: all critical symptoms present
                    # Optional: Boost confidence for rule-matched diseases
                    confidence = min(1.0, confidence * 1.2) # Example boost
                    logger.info(f"Rule match for {disease}: all critical symptoms present. Confidence boosted to {confidence:.4f}.")
                else:
                    # Optional: Penalize confidence if critical symptoms are missing for a highly ranked ML prediction
                    # This needs careful tuning to avoid false negatives.
                    pass # For now, no penalty if not all critical symptoms are present.

            final_predictions_candidates.append({
                "disease": disease,
                "confidence": confidence,
                "rule_matched": bool(rule_validation_score) # True if all critical symptoms matched
            })

        # Re-sort predictions based on potentially adjusted confidence
        final_predictions_candidates.sort(key=lambda x: x['confidence'], reverse=True)

        # Populate top_predictions based on the refined list
        for i, pred_candidate in enumerate(final_predictions_candidates):
            if i >= TOP_N_PREDICTIONS and pred_candidate['confidence'] < MIN_CONFIDENCE_THRESHOLD:
                # Stop if we've reached TOP_N and confidence is too low
                break
            top_predictions.append({
                "disease": pred_candidate['disease'],
                "confidence": f"{pred_candidate['confidence']:.4f}",
                "rule_matched_critical_symptoms": pred_candidate['rule_matched']
            })

        # Determine primary prediction (highest confidence after rule adjustments)
        if final_predictions_candidates:
            primary_predicted_disease_obj = final_predictions_candidates[0]
            primary_predicted_disease = primary_predicted_disease_obj['disease']
            primary_confidence = primary_predicted_disease_obj['confidence']

            if primary_confidence < MIN_CONFIDENCE_THRESHOLD and not primary_predicted_disease_obj['rule_matched']:
                primary_predicted_disease = "Uncertain Diagnosis"
                logger.info(f"SymScan: Primary prediction confidence {primary_confidence:.4f} below threshold {MIN_CONFIDENCE_THRESHOLD} and no rule match.")
            elif primary_confidence < MIN_CONFIDENCE_THRESHOLD and primary_predicted_disease_obj['rule_matched']:
                logger.info(f"SymScan: Primary prediction {primary_predicted_disease} below threshold {primary_confidence:.4f} but validated by rule. Retaining diagnosis.")
                # We retain the diagnosis if a rule validated it, even if confidence is slightly low.
        else:
            primary_predicted_disease = "Uncertain Diagnosis" # No predictions generated
    else:
        # Fallback if predict_proba is not available
        logger.warning("SymScan classifier does not support predict_proba; relying on single prediction and no confidence.")
        # We can still use the `predict` method for a single primary prediction if absolutely necessary
        # but the hybrid system's effectiveness is reduced without probabilities.
        # For a robust system, predict_proba is essential.
        single_prediction_label_int = _symscan_classifier.predict(input_df)[0]
        primary_predicted_disease = _symscan_int_to_disease.get(single_prediction_label_int, "Unknown Disease")
        primary_confidence = "N/A"
        top_predictions.append({
            "disease": primary_predicted_disease,
            "confidence": "N/A",
            "rule_matched_critical_symptoms": False # Can't apply rule without probabilities for context
        })
        # If no probabilities, it's safer to mark as uncertain if no strong rule applies.
        if not (primary_predicted_disease in CRITICAL_SYMPTOMS_RULES and
                set(CRITICAL_SYMPTOMS_RULES[primary_predicted_disease]).issubset(normalized_user_symptoms_present)):
            primary_predicted_disease = "Uncertain Diagnosis"


    # --- Precaution Retrieval (Expert System Component) ---
    if primary_predicted_disease != "Uncertain Diagnosis" and primary_predicted_disease != "Unknown Disease":
        precautions = _symscan_precautions_map.get(primary_predicted_disease, ["No specific precautions found for this disease. Consult a medical professional."])
    else:
        # If diagnosis is uncertain or unknown, provide general advice
        precautions = ["Diagnosis is uncertain. It is crucial to consult a medical professional for a proper diagnosis and treatment plan.",
                       "Stay hydrated and rest. Avoid self-medication."]

    response_data = {
        "predicted_disease": primary_predicted_disease,
        "confidence_for_primary_prediction": f"{primary_confidence:.4f}" if isinstance(primary_confidence, float) else primary_confidence,
        "top_n_predictions": top_predictions,
        "precautions": precautions,
        "provided_raw_symptoms": raw_symptoms,
        "normalized_symptoms_used_by_model": sorted(list(normalized_user_symptoms_present)),
        "unrecognized_symptoms": unrecognized_symptoms_list,
        "medical_disclaimer": "This system is informational only and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment."
    }
    return response_data