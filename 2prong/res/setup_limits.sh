region=signal
sigtype=eta
debug="0" # -1 = very quiet, 0 = quiet, 1 = verbose, 2+ = debug
crop_style=1 # 0 = old-nonextended-signal, 1 = correct, 2 = test

input="./input"
#signal="signal_10percent_eta"
#signal="signal_10percent_etaprime"
#signal="signal_10percent_lowerphimass_eta"
#signal="signal_10percent_lowerphimass_etaprime"
signal="box_around_71_75kevents_eta"

# first last npoints
#wmasspoints=(0.85 4 22)
#wmasspoints=(0.5 4 57)
#pmasspoints=(500 3000 21)
#pmasspoints=(500 3000 11)
#wmasspoints=(0.5 4 11)
#pmasspoints=(550 2925 20) 

# around 71
wmasspoints=(2 3 5)
pmasspoints=(1000 1500 6) 

#masses=(71)
masses=($(seq 0 $(( ${wmasspoints[2]} * ${pmasspoints[2]} - 1 ))))

sed -i "s|^crop_style = .*|crop_style = $crop_style|" files.py
sed -i "s|input_top_level = '.*'|input_top_level = '$input'|" files.py
sed -i "s|signal_input = '.*'|signal_input = '$signal'|" files.py
sed -i "s/^wmasspoints = numpy\.linspace(.*)$/wmasspoints = numpy.linspace(${wmasspoints[0]}, ${wmasspoints[1]}, ${wmasspoints[2]})/" files.py
sed -i "s/^pmasspoints = numpy\.linspace(.*)$/pmasspoints = numpy.linspace(${pmasspoints[0]}, ${pmasspoints[1]}, ${pmasspoints[2]})/" files.py
