from disease import Disease

# Spec name and code
# Anastasis     ANE
# Cardiology    CAR
# Surgery       CHI
# Dietary       DIE
# Physiology    FYS
# Geriatrics    GER
# Internal      INT
# Lung          LON
# Gastro-entol. MDL
# Neurology     NEU
# Elderly Care  OGK
# Orthopedics   ORT
# Plastic Sur.  PLA
# Revalidation  REV

chads_vasc_c = [
    Disease("CAR", "21", description="aanwijzingen beperkt hartfalen"),
    Disease("CAR", "22", description="acuut hartfalen"),
    Disease("CAR", "25", description="hartfalen bij kleplijden"),
    Disease("CAR", "26", description="hartfalen bij CMP"),
    Disease("CAR", "27", description="chronisch hartfalen"),
    Disease("CAR", "301", description="Acuut hartfalen"),
    Disease("CAR", "302", description="Chronisch hartfalen"),
    Disease("DIE", "26", description="Hartfalen"),
    Disease("GER", "262", description="Decompensatio cordis"),
    Disease("INT", "107", description="decompensatio cordis")
]

chads_vasc_h = [
    Disease("CAR", "72", description="hypertensie"),
    Disease("CAR", "902", description="hypertensie"),
    Disease("DIE", "27", description="Hypertensie"),
    Disease("INT", "311", description="Hypertensie"),
    Disease("MDL", "901", description="Hypertensie"),
]

chads_vasc_d = [
    Disease("CHI", "432", description="diabetische voet(diabetes nno)"),
    Disease("DIE", "54", description="Diabetes type 1"),
    Disease("DIE", "55", description="Diabetes type  2"),
    Disease("GER", "222", description="Diabetes Mellitus"),
    Disease("INT", "221", description="DM znd secundaire complicaties"),
    Disease("INT", "222", description="DM met secundaire complicaties"),
    Disease("INT", "223", description="DM chronisch pomptherapie"),
    Disease("MDL", "902", description="Diabetes mellitus"),
    Disease("ORT", "2065", description="Diabetische voet")
]

chads_vasc_s = [
    Disease("GER", "263", description="CVA / TIA"),
    Disease("INT", "121", description="cerebrovasculair acc/TIA"),
    Disease("NEU", "1111", description="onbloedige beroerte"),
    Disease("NEU", "1112", description="TIA (incl amaurosis fugax)"),
    Disease("NEU", "1199", description="overige cerebrovasc aand"),
    Disease("NEU", "9927", description="Geen neur, werkdiag TIA"),
    Disease("OGK", "101", description="CVA"),
    Disease("REV", "313", description="CVA"),
    Disease("REV", "C31", description="CVA klasse 1"),
    Disease("REV", "C32", description="CVA klasse 2"),
    Disease("REV", "C33", description="CVA klasse 3"),
    Disease("REV", "C34", description="CVA klasse 4"),
    Disease("REV", "C36", description="CVA klasse 6"),
]

chads_vasc_v = [
    Disease("ANE", "110", description="Ischaem pijn a/d extremiteiten"),
    Disease("CAR", "3", description="AP, geen ischemie aangetoond"),
    Disease("CAR", "4", description="AP, ischemie aangetoond"),
    Disease("CAR", "5", description="ischemie znd AP (stille isch)"),
    Disease("CAR", "7", description="onstabiele / progressieve AP"),
    Disease("CAR", "9", description="acuut MI (q/non-q) voorwand"),
    Disease("CAR", "11", description="acuut MI (q/non-q) elders"),
    Disease("CAR", "13", description="follow up na myocardinfarct"),
    Disease("CAR", "15", description="follow up na  PTCA en/of CABG"),
    Disease("CAR", "202", description="angina pectoris, stabiel"),
    Disease("CAR", "203", description="angina pectoris, onstabiel"),
    Disease("CAR", "204", description="ST elevatie hartinfarct"),
    Disease("CAR", "205", description="non ST elevatie hartinfarct"),
    Disease("CAR", "601", description="Arteriele vaatafw / stenose"),
    Disease("CAR", "801", description="Follow-up na acuut cor syndr"),
    Disease("CAR", "802", description="followup na PTCA e/o CABG/abl"),
    Disease("CAR", "808", description="f-up na vaatoper(arte/ven)"),
    Disease("CHI", "402", description="Carotispathologie"),
    Disease("CHI", "403", description="Aneurysma aorta thor, ruptuur"),
    Disease("CHI", "405", description="Aneurysma aorta iliacaal"),
    Disease("CHI", "406", description="Aneurysma aorta abd, ruptuur"),
    Disease("CHI", "408", description="nierarteriestenose"),
    Disease("CHI", "409", description="Vaat afw abdominaal / bekken"),
    Disease("CHI", "410", description="Vaatletsel bovenste extremit"),
    Disease("CHI", "412", description="P.A.O.D. arm"),
    Disease("CHI", "416", description="Aneurysma onderste extremiteit"),
    Disease("CHI", "418", description="P.A.O.D. 2, claudicatio interm"),
    Disease("CHI", "419", description="P.A.O.D. 3, rustpijn"),
    Disease("CHI", "420", description="P.A.O.D. 4, gangreen"),
    Disease("FYS", "2048", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "2540", description="Hart-, Vaat-, Lymfevataandoeningen - Hartaandoenin"),
    Disease("FYS", "2541", description="harftinfarct, myocard-infarct (AMI)"),
    Disease("FYS", "2544", description="Hart-, Vaat-, Lymfevataandoeningen - status na har"),
    Disease("FYS", "2548", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "6048", description="Algemeen vaatlijden, circulatiestoornissen"),
    Disease("FYS", "6948", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "7148", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "7948", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "9048", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "9248", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("FYS", "9346", description="Hart-, Vaat-, Lymfevataandoeningen - Lymfevataando"),
    Disease("FYS", "9348", description="Hart-, Vaat-, Lymfevataandoeningen - alg. vaatlijd"),
    Disease("GER", "261", description="Aandoeningen hartvaatstelsel"),
    Disease("INT", "101", description="sympt isch hartz, niet DBC-102"),
    Disease("INT", "102", description="Instabiele AP, myocardinfarct"),
    Disease("INT", "122", description="Arteriële trombose en embolie"),
    Disease("INT", "124", description="atheroscl extr/perif vaatlijd"),
    Disease("INT", "129", description="Aneurysma en ov arter vaat"),
    Disease("LON", "1102", description="Pijn op de borst"),
    Disease("REV", "F21", description="Hart/bloedvaten 1"),
    Disease("REV", "F22", description="Hart/bloedvaten 2"),
    Disease("REV", "F23", description="Hart/bloedvaten 3"),
    Disease("REV", "F24", description="Hart/bloedvaten 4"),
]

# Currently a copy of chads_vasc_s but might differ in the future
stroke_diseases = chads_vasc_s

atrial_fib = [Disease("CAR", "401"), Disease("INT", "106")]


def groups_to_LaTeX_table():
    file = ""
    groups = [chads_vasc_c, chads_vasc_h, chads_vasc_d, chads_vasc_s, chads_vasc_v]
    letters = ["C", "H", "D", "S", "V"]

    file += "\\begin{longtable}{l|l|l|l}\n"
    file += "\\caption{List of all \\chadsvasc{} diagnoses, " \
            "selected from all present diagnoses of the AF patients, selected by a cardiologist.} \\\\\n"
    file += "Category & Department & Code & Description (Dutch) \\\\\n"
    for l, g in zip(letters, groups):
        file += "\\hline\n"
        file += l
        for d in g:
            file += " & {} & {} & {} \\\\\n".format(d.spec, d.diag, d.description)

    file += "\\end{longtable}"

    f = open('output/diagnoses_table.tex', 'w')
    f.write(file)

