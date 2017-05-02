from disease import Disease

# Spec name and code
# Cardiologie   CAR     3
# Interne       INT     2
# Gastro-ent    ???     7
# Neurologie    NEU     21
# Geriatrie     GER     33

chads_vasc_c = [Disease("CAR", "302"),
                Disease("GER", "262")]
chads_vasc_h = [Disease("7", "901"),
                Disease("CAR", "902"),
                Disease("INT", "311")]
chads_vasc_d = [Disease("7", "902"),
                Disease("INT", "221"),
                Disease("INT", "222"),
                Disease("INT", "223")]
chads_vasc_s = [Disease("INT", "101"),
                Disease("INT", "121"),
                Disease("NEU", "1111"),
                Disease("NEU", "1112"),
                Disease("GER", "263")]
chads_vasc_v = [Disease("INT", "102"),
                Disease("INT", "104"),
                Disease("INT", "124"),
                Disease("CAR", "204"),
                Disease("CAR", "205")]

# Currently a copy of chads_vasc_s but might differ in the future
stroke_diseases = [Disease("INT", "101"),
                   Disease("INT", "121"),
                   Disease("NEU", "1111"),
                   Disease("GER", "263")]

atrial_fib = [Disease("CAR", "401")]
