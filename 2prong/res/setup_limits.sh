region=sideband
sigtype=etaprime
#wmasspoints=(1 2 8) # first last npoints
#pmasspoints=(1000 2500 14) # first last npoints
#wmasspoints=(0.75 2 6) # first last npoints
#pmasspoints=(1000 2500 4) # first last npoints
wmasspoints=(0.5 4 15) # first last npoints
pmasspoints=(500 3000 11) # first last npoints
debug="0" # -1 = very quiet, 0 = quiet, 1 = verbose, 2+ = debug

input="./input"
#signal="signal_10percent_eta"
signal="signal_10percent_etaprime"
#signal="signal_original_box"

masses=(40)
#masses=(0 7 32 39 96 103)
#masses=(0 1 5 6 7 11 18 19 23)
#masses=($(seq 0 49))
#masses=($(seq 0 $(( ${wmasspoints[2]} * ${pmasspoints[2]} - 1 ))))
#masses=(0 1 2 6 10 14 15 16 17 21 25 29 30 31 32 36 40 44 60 61 62 66 70 74 120 121 122 126 130 134 150 151 152 156 160)

sed -i "s|input_top_level = '.*'|input_top_level = '$input'|" files.py
sed -i "s|signal_input = '.*'|signal_input = '$signal'|" files.py
sed -i "s/^wmasspoints = numpy\.linspace(.*)$/wmasspoints = numpy.linspace(${wmasspoints[0]}, ${wmasspoints[1]}, ${wmasspoints[2]})/" files.py
sed -i "s/^pmasspoints = numpy\.linspace(.*)$/pmasspoints = numpy.linspace(${pmasspoints[0]}, ${pmasspoints[1]}, ${pmasspoints[2]})/" files.py
./files.py
