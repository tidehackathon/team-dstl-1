import simplekml

with open("output.csv", "w") as f:
    f.write("offset,predicted_lon,predicted_lat,truth_lon,truth_lat\n")

kml = simplekml.Kml(name='Proof of Concept')
kml.save("output.kml")