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
chads_vasc_c = [Disease("INT", "107", description="Decompensatio cordis"),
                Disease("CAR", "301", description="Acuut hartfalen"),
                Disease("CAR", "302", description="chronisch hartfalen"),
                Disease("CAR", "802", description="followup na PTCA e/o CABG/abl"),
                Disease("GER", "262", description="Decompensatio cordis"),
                Disease("CAR", "203", description="angina pectoris, onstabiel"),
                Disease("PLA", "352", description="decompr overige compr syndr")]
chads_vasc_h = [Disease("7", "901"),
                Disease("CAR", "902", description="hypertensie"),
                Disease("INT", "311", description="Hypertensie")]
chads_vasc_d = [Disease("7", "902"),
                Disease("INT", "221", description="DM znd secundaire complicaties"),
                Disease("INT", "222", description="DM met secundaire complicaties"),
                Disease("INT", "223", description="DM chronisch pomptherapie"),
                Disease("CHI", "432", description="diabetische voet(diabetes nno)")]
chads_vasc_s = [Disease("INT", "101"),
                Disease("INT", "121", description="cerebrovasculair acc/TIA"),
                Disease("OGK", "101", description="CVA"),
                Disease("NEU", "1111", description="onbloedige beroerte"),
                Disease("NEU", "1112", description="TIA (incl amaurosis fugax)"),
                Disease("NEU", "1199", description="overige cerebrovasc aand"),
                Disease("NEU", "9927", description="Geen neur, werkdiag TIA"),
                Disease("GER", "263", description="CVA / TIA"),
                Disease("REV", "0313", description="CVA")]
chads_vasc_v = [Disease("INT", "102", description="Instabiele AP, myocardinfarct"),
                Disease("INT", "104"),
                Disease("INT", "124", description="atheroscl extr/perif vaatlijd"),
                Disease("GER", "261", description="Aandoeningen hartvaatstelsel"),
                Disease("OOG", "657", description="vaatafsluiting"),
                Disease("ANE", "110", description="Ischaem pijn a/d extremiteiten"),
                Disease("CHI", "406", description="aneurysma aorta abd, ruptuur"),
                Disease("CHI", "402", description="Carotispathologie"),
                Disease("CHI", "405", description="Aneurysma aorta iliacaal"),
                Disease("CHI", "409", description="Vaat afw abdominaal / bekken"),
                Disease("CHI", "412", description="P.A.O.D. arm"),
                Disease("CHI", "417", description="Arteriële embolie+trombose,336"),
                Disease("CHI", "418", description="P.A.O.D. 2, claudicatio interm"),
                Disease("CHI", "419", description="P.A.O.D. 3, rustpijn"),
                Disease("CHI", "420", description="P.A.O.D. 4, gangreen"),
                Disease("RAD", "183", description="Arteria iliaca communis"),
                Disease("RAD", "187", description="Aorta-iliacaal"),
                Disease("RAD", "191", description="Arteria femoralis communis"),
                Disease("RAD", "192", description="Arteria femoral superficialis"),
                Disease("RAD", "194", description="Arteria poplitea"),
                Disease("CAR", "204", description="ST elevatie hartinfarct"),
                Disease("CAR", "205", description="Non ST elevatie hartinfarct"),
                Disease("CAR", "601", description="Arteriele vaatafw / stenose"),
                Disease("CAR", "801", description="Follow-up na acuut cor syndr"),
                Disease("CAR", "808", description="f-up na vaatoper(arte/ven)")]

# Currently a copy of chads_vasc_s but might differ in the future
stroke_diseases = chads_vasc_s

atrial_fib = [Disease("CAR", "401")]
