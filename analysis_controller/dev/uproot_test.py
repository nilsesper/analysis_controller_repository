
import uproot

events = uproot.open("https://scikit-hep.org/uproot3/examples/Zmumu.root:events")
print(events)
awk_arr = events.array()
print(array)


