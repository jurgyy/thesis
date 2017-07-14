import datetime
import pickle

from breakdown import *
from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.medication_csv import get_medications
from csv_reader.mergers import *
from csv_reader.patients_csv import get_patients
from practioner_analysis.practitioner import analyze_practitioners
from simulations.simulations import compare_predictor_chads_vasc


def add_diseases(patients, diagnoses_dict):
    for patient_nr, diagnoses in diagnoses_dict.items():
        for diagnosis in diagnoses:
            patients[patient_nr].add_diagnosis(diagnosis)


def add_medications(patients, medications_dict):
    for patient_nr, medications in medications_dict.items():
        for medication in medications:
            try:
                patients[patient_nr].add_medication(medication)
            except KeyError:
                print("Missing data, patient {}".format(patient_nr))
                continue


def get_all_diseases(diagnoses):
    diseases = set()
    for patient_nr, diagnosis in diagnoses.items():
        for d in diagnosis:
            diseases.add(d.disease)

    return diseases


def get_disease_frequency(diseases, diagnoses):
    frequency = {d: 0 for d in diseases}

    for patient_diagnoses in diagnoses.values():
        for diagnosis in patient_diagnoses:
            if diagnosis.disease not in frequency:
                continue
            frequency[diagnosis.disease] += 1

    return frequency


def reduce_feature_space(diseases, diagnoses, min_frequency):
    frequency = get_disease_frequency(diseases, diagnoses)

    diseases = [d for d, f in frequency.items() if f >= min_frequency]
    return set(diseases)


def prepare_data(dir, sep='\t'):
    print("Reading CSV files...")
    patients = get_patients("data/{}/patient_general.csv".format(dir), sep)
    diagnoses = get_diagnoses("data/{}/patient_diagnoses.csv".format(dir), sep, merge=False)
    medications = get_medications("data/{}/patient_meds.csv".format(dir), sep)

    print("Linking data...")
    add_diseases(patients, diagnoses)
    add_medications(patients, medications)

    print("Finding events...")
    for p in patients.values():
        p.set_care_range(extra_months=12)
        p.find_strokes()
        p.find_chads_vasc_changes()

    return patients, diagnoses, medications


def pickle_data(data, fname):
    pickle.dump(data, open("output/{}.pkl".format(fname), "wb"))


def unpickle_data(fname):
    return pickle.load(open("output/{}.pkl".format(fname), "rb"))


def main(load_pickle=True):
    # compare_predictor_chads_vasc(None, None, None, None, load_from_file=True)
    # exit()
    if load_pickle:
        print("Loading data from Pickle files...")
        patients_A, diagnoses_A, medications_A = unpickle_data("data_A")
        patients_B, diagnoses_B, medications_B = unpickle_data("data_B")
        patients, diagnoses, medications = unpickle_data("data_combined")
        print("Done.")
    else:
        patients_A, diagnoses_A, medications_A = prepare_data("msc_A", sep='\t')
        patients_B, diagnoses_B, medications_B = prepare_data("msc_B", sep='\t')

        print("Merging data...")
        patients = merge_data(patients_A, patients_B)
        diagnoses = merge_data(diagnoses_A, diagnoses_B)
        medications = merge_data(medications_A, medications_B)

        print("Total number of patients: {}".format(len(patients.keys())))
        print("Number of female patients: {}".format(sum([1 if p.is_female() else 0 for p in patients.values()])))

        print("Pickling data...")
        pickle_data([patients_A, diagnoses_A, medications_A], "data_A")
        pickle_data([patients_B, diagnoses_B, medications_B], "data_B")
        pickle_data([patients, diagnoses, medications], "data_combined")

    diseases = get_all_diseases(diagnoses)
    plot_disease_frequency(diseases, diagnoses)
    breakdown(patients, datetime.date(2017, 1, 1))
    stroke_analysis(patients)
    plot_AF_count([patients_A, patients_B], datetime.date(2004, 1, 1), datetime.date(2017, 6, 1), ["Hospital A", "Hospital B"])
    exit()


    # Optionally remove rare disease which reduces the feature space roughly in half
    # diseases = reduce_feature_space(diseases, diagnoses, min_frequency=10)

    start = datetime.date(2013, 4, 1)
    end = datetime.date(2017, 6, 1)
    start_prac = datetime.date(2013, 4, 1)
    end_prac = datetime.date(2017, 6, 1)
    start_ml = datetime.date(2015, 1, 1)
    end_ml = datetime.date(2015, 12, 31)

    analyze_practitioners(patients_A, start_prac, end_prac, spec="CAR", diag="401", meds_start_with="B01",
                          plot=True, fname_prefix="A_")
    analyze_practitioners(patients_B, start_prac, end_prac, spec="CAR", diag="401", meds_start_with="B01",
                          plot=True, fname_prefix="B_")
    compare_predictor_chads_vasc(patients, diseases, start_ml, end_ml, load_from_file=False)


    # asr = find_adjusted_stroke_rate(patients, start, end)
    # print(asr)

if __name__ == "__main__":
    main()
