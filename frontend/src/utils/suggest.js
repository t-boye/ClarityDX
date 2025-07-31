// src/utils/suggest.js

export const SYMPTOM_SUGGESTIONS = [
  // General Symptoms
  "abdominal cramps",
  "abdominal pain",
  "malaise",
  "weakness",
  "fatigue",
  "weight gain",
  "weight loss",
  "fever",
  "chills",
  "sweating",
  "headache",
  "dizziness",
  "lightheadedness",
  "confusion",
  "memory impairment",
  "disorientation",
  "seizures",
  "syncope", // fainting, loss of consciousness
  "irritability",
  "agitation",
  "anxiety",
  "depression",
  "panic attack",
  "insomnia",
  "hypersomnia",
  "sleep disturbance",
  "night sweats",
  "body ache",
  "muscle aches", // Added from your list
  "muscle weakness",
  "muscle cramps",
  "muscle spasms",
  "joint pain", // arthralgia
  "joint swelling",
  "joint stiffness",
  "morning stiffness",
  "paresthesia", // numbness and tingling
  "numbness", // From your list
  "tingling", // From your list
  "tremor", // shaking
  "involuntary movements",
  "balance problems",
  "gait disturbance", // difficulty walking
  "vertigo", // spinning sensation
  "ataxia", // coordination problems
  "swelling", // edema
  "edema", // Specific for swelling
  "inflammation",
  "dehydration",
  "heat intolerance",
  "cold intolerance",
  "cold extremities", // From your list

  // Respiratory Symptoms
  "runny nose",
  "sore throat",
  "cough",
  "sneezing",
  "nasal congestion",
  "postnasal drip",
  "hoarseness",
  "chest tightness",
  "shortness of breath", // dyspnea
  "dyspnea", // specific medical term
  "wheezing",
  "stridor",
  "rales",
  "rhonchi",
  "pleuritic pain", // chest pain on breathing
  "mucus production", // From your list
  "chest discomfort", // From your list

  // Cardiovascular Symptoms
  "chest pain",
  "heart palpitations",
  "arrhythmia", // irregular heartbeat
  "nosebleeds", // epistaxis
  "epistaxis", // specific medical term

  // Gastrointestinal Symptoms
  "nausea",
  "vomiting",
  "diarrhea",
  "constipation",
  "abdominal cramps",
  "bloating",
  "heartburn",
  "acid reflux",
  "indigestion",
  "belching",
  "loss of appetite", // anorexia
  "anorexia", // specific medical term
  "polydipsia", // increased thirst
  "polyphagia", // increased hunger
  "halitosis", // bad breath
  "ageusia", // loss of taste
  "anosmia", // loss of smell
  "dysgeusia", // changes in taste
  "metallic taste in mouth",
  "hematemesis", // vomiting blood
  "melena", // black stools
  "hematochezia", // fresh blood in stool
  "pale stools",
  "steatorrhea", // greasy stools
  "change in bowel habits",
  "mucus in stool", // From your list

  // Urinary & Genital Symptoms
  "frequent urination", // polyuria
  "polyuria", // specific medical term
  "nocturia", // frequent urination at night
  "burning urination", // dysuria
  "dysuria", // specific medical term
  "pelvic pain",
  "blood in urine", // hematuria
  "hematuria", // specific medical term
  "urinary urgency",
  "incontinence",
  "flank pain",
  "testicular pain",
  "testicular swelling",
  "vaginal discharge",
  "vaginal itching", // genital itching
  "penile discharge",
  "genital itching",
  "genital ulcers", // genital sores
  "dyspareunia", // painful intercourse
  "sexual dysfunction",
  "menstrual irregularities", // irregular/heavy/missed periods
  "dysmenorrhea", // painful periods
  "abnormal bleeding", // From your list
  "nipple discharge",
  "breast lump", // From your list

  // Skin & Hair Symptoms
  "rash",
  "skin rash", // consolidate with rash if possible, or decide primary
  "pruritus", // itching
  "itchy skin", // from your list
  "pruritic rash", // itchy rash
  "skin redness", // erythema
  "erythema", // specific medical term
  "blisters",
  "skin lesions",
  "skin peeling",
  "dry skin",
  "skin cracking",
  "skin discoloration",
  "jaundice", // yellow skin/eyes
  "yellow skin", // from your list
  "yellow eyes", // from your list
  "pallor", // pale skin
  "bruising",
  "petechiae",
  "purpura",
  "hives", // urticaria
  "urticaria", // specific medical term
  "skin lump", // nodule, mass
  "ulcer", // open sore, skin ulcer
  "non-healing ulcer",
  "hair loss",
  "nail changes", // brittle nails, nail discoloration
  "acne", // from your list (acne vulgaris)
  "skin inflammation", // from your list (acne vulgaris)
  "facial swelling", // from your list
  "lip swelling", // from your list
  "tongue swelling", // from your list
  "trismus", // difficulty opening mouth
  "facial numbness", // from your list
  "facial paresthesia", // from your list
  "facial weakness", // from your list
  "groin rash", // from your list

  // Eye/Ear/Mouth Symptoms
  "eye pain",
  "red eyes",
  "itchy eyes",
  "dry eyes",
  "blurred vision",
  "diplopia", // double vision
  "vision loss",
  "photophobia", // light sensitivity
  "visual disturbances", // flashing lights, floaters
  "ear pain",
  "ear discharge",
  "hearing loss",
  "tinnitus", // ringing in ears
  "ear fullness", // ear pressure
  "ear blockage", // from your list
  "oral lesions", // mouth sores, oral ulcers
  "tongue soreness",
  "gum inflammation", // gingivitis
  "gum bleeding",
  "gum swelling",

  // Other specific
  "goiter", // thyroid swelling
  "recurrent infections", // frequent infections
  "slow healing", // slow wound healing
  "suicidal ideation", // Critical - mental health
  "paranoia",
  "anhedonia", // lack of interest
  "dysarthria", // slurred speech
  "dysphasia", // difficulty speaking
  "aphasia", // unable to speak
  "aphonia", // loss of voice
  "stuttering", // from your list
  "myalgia", // muscle aches and pains
  "gait disturbance", // fix typo from 'ggait disturbance'
  "nerve pain", // shooting pains
  "cold sore", // if distinct from oral lesions

  // Combined/Contextual (Only include if you want to suggest these exact phrases)
  // Generally, it's better to suggest single canonical terms and let user combine.
  // "flu-like symptoms",
  // "burning stomach pain",
  // "pain in left arm",
  // "loss of taste", // already above as ageusia, decide canonical
  // "loss of smell", // already above as anosmia, decide canonical
  // "body ache", // already above
  // "joint pain (psoriatic arthritis)", // too specific for suggestion
  // "pain in left arm or jaw", // too specific for suggestion
  // "difficulty speaking", // already above as dysphasia
  // "trouble speaking", // already above as dysphasia
  // "burning urination", // already above as dysuria
  // "difficulty urinating", // already above as dysuria
  // "excess hair growth", // hirsutism (if you add this canonical)
  // "breast pain", // already above
  // "skin dimpling", // too specific for suggestion
  // "coughing up blood", // already above as hemoptysis
  // "pain in left arm", // from heart attack
  // "abdominal discomfort",
  // "numbness and tingling in hands and feet", // Suggest 'paresthesia' instead
  // "difficulty walking and balance problems", // Suggest 'gait disturbance', 'balance problems'
  // "blurred vision and light sensitivity", // Suggest 'blurred vision', 'photophobia'
  // "ear pain and ringing", // Suggest 'ear pain', 'tinnitus'
  // "nasal congestion and sore throat", // Suggest individual
  // "sore throat and hoarseness", // Suggest individual
  // "chest tightness and cough", // Suggest individual
  // "abdominal pain and constipation", // Suggest individual
  // "nausea and heartburn", // Suggest individual
  // "frequent urination and blood in urine", // Suggest individual
  // "vaginal discharge and pelvic pain", // Suggest individual
  // "genital sores and itching", // Suggest individual
  // "skin rash and joint pain", // Suggest individual
  // "itchy skin and swelling", // Suggest individual
  // "hair loss and fatigue", // Suggest individual
  // "brittle nails and dry hair", // Suggest individual
  // "swelling and warmth", // Suggest individual
  // "lymph node swelling and tenderness", // Suggest individual
  // "excessive thirst and polyuria", // Suggest individual
  // "unexplained weight loss and frequent urination", // Suggest individual
  // "muscle weakness and joint pain", // Suggest individual
  // "joint pain and redness", // Suggest individual
  // "numbness and tingling in face", // Suggest individual
  // "difficulty walking and numbness", // Suggest individual
  // "blurred vision and double vision", // Suggest individual
  // "ear pain and fullness", // Suggest individual
  // "nasal congestion and facial pain", // Suggest individual
  // "sore throat and difficulty swallowing", // Suggest individual
  // "chest pain and palpitations", // Suggest individual
  // "abdominal pain and nausea", // Suggest individual
  // "frequent urination and pelvic pain", // Suggest individual
  // "vaginal discharge and painful intercourse", // Suggest individual
  // "genital sores and discharge", // Suggest individual
  // "skin rash and swelling", // Suggest individual
  // "itchy skin and warmth", // Suggest individual
  // "hair loss and dry skin", // Suggest individual
  // "brittle nails and hair loss", // Suggest individual
  // "swelling and discoloration", // Suggest individual
  // "lymph node swelling and redness", // Suggest individual
  // "excessive thirst and weight loss", // Suggest individual
  // "unexplained weight gain and fatigue", // Suggest individual
  // "muscle weakness and stiffness", // Suggest individual
  // "joint pain and limited movement", // Suggest individual
  // "numbness and tingling in arm", // Suggest individual
  // "difficulty walking and muscle weakness", // Suggest individual
  // "blurred vision and headaches", // Suggest individual
  // "ear pain and ringing in ears", // Suggest individual
  // "nasal congestion and sneezing", // Suggest individual
  // "sore throat and swollen glands", // Suggest individual
  // "chest pain and cough", // Suggest individual
  // "abdominal pain and vomiting", // Suggest individual
];
