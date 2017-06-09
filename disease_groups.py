from disease import Disease

# Spec name and code
# Cardiologie   CAR     3
# Interne       INT     2
# Gastro-ent    ???     7
# Neurologie    NEU     21
# Geriatrie     GER     33
# Oudere Gen.k. OGK     ???
# Plastic Sur.  PLA
# Surgery       CHI
# Revalidation  REV
# Anesasie      ANE

# TODO: Check the final diagnoses list for all possible diseases
chads_vasc_c = [Disease("INT", "107"),  # Decompensatio cordis
                Disease("CAR", "301"),  # Acuut hartfalen
                Disease("CAR", "302"),  # chronisch hartfalen
                Disease("CAR", "802"),  # followup na PTCA e/o CABG/abl
                Disease("GER", "262"),
                Disease("CAR", "203"),  # angina pectoris, onstabiel
                Disease("PLA", "352")]  # decompr overige compr syndr
chads_vasc_h = [Disease("7", "901"),
                Disease("CAR", "902"),  # hypertensie
                Disease("INT", "311")]  # Hypertensie
chads_vasc_d = [Disease("7", "902"),
                Disease("INT", "221"),  # DM znd secundaire complicaties
                Disease("INT", "222"),  # DM met secundaire complicaties
                Disease("INT", "223"),  # DM chronisch pomptherapie
                Disease("CHI", "432")]  # diabetische voet(diabetes nno)
chads_vasc_s = [Disease("INT", "101"),
                Disease("INT", "121"),  # cerebrovasculair acc/TIA
                Disease("OGK", "101"),  # CVA
                Disease("NEU", "1111"), # onbloedige beroerte
                Disease("NEU", "1112"), # TIA (incl amaurosis fugax)
                Disease("NEU", "1199"), # Overige cerebrovasc aand
                Disease("NEU", "9927"), # Geen neur, werkdiag TIA
                Disease("GER", "263"),  # CVA / TIA
                Disease("REV", "0313")] # CVA
chads_vasc_v = [Disease("INT", "102"),  # Instabiele AP, myocardinfarct
                Disease("INT", "104"),
                Disease("INT", "124"),  # atheroscl extr/perif vaatlijd
                Disease("OOG", "657"),  # vaatafsluiting
                Disease("ANE", "110"),  # Ischaem pijn a/d extremiteiten
                Disease("CHI", "406"),  # aneurysma aorta abd, ruptuur
                Disease("CHI", "402"),  # Carotispathologie
                Disease("CHI", "405"),  # Aneurysma aorta iliacaal
                Disease("CHI", "409"),  # Vaat afw abdominaal / bekken
                Disease("CHI", "412"),  # P.A.O.D. arm
                Disease("CHI", "417"),  # Arteriële embolie+trombose,336
                Disease("CHI", "418"),  # P.A.O.D. 2, claudicatio interm
                Disease("CHI", "419"),  # P.A.O.D. 3, rustpijn
                Disease("CHI", "420"),  # P.A.O.D. 4, gangreen
                Disease("RAD", "183"),  # Arteria iliaca communis
                Disease("RAD", "187"),  # Aorta-iliacaal
                Disease("RAD", "191"),  # Arteria femoralis communis
                Disease("RAD", "192"),  # Arteria femoral superficialis
                Disease("RAD", "194"),  # Arteria poplitea
                Disease("CAR", "204"),  # ST elevatie hartinfarct
                Disease("CAR", "205"),  # Non ST elevatie hartinfarct
                Disease("CAR", "601"),  # Arteriele vaatafw / stenose
                Disease("CAR", "801"),  # Follow-up na acuut cor syndr
                Disease("CAR", "808")]  # f-up na vaatoper(arte/ven)

# Currently a copy of chads_vasc_s but might differ in the future
stroke_diseases = chads_vasc_s

atrial_fib = [Disease("CAR", "401")]
