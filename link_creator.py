# Short script that takes an ra, dec, and desired zoom, spits out helpful links.
# initial code from kevin welch, 9th Version
# modified by Michael

def main():
    # Basic while loop, only breaks on user input and takes input for ra, dec, zoom and passes to another function to create and return links.
    while True:
        # printing lines and breaks to make it a bit more visually easier to read when using the program.
        print("-" * 30)
        RA = tryparse(float, input("Please Input Object RA: "), 0)
        DEC = tryparse(float, input("Please Input Object DEC: "), 0)
        ZOOM = tryparse(float, input("Please Input Desired Zoom (default=16): "), 16)
        links = link_central(RA, DEC, ZOOM)
        # iterate through the returned list and print
        i = 0
        while i < len(links):
            print(links[i])
            i += 1
        print("\n" * 1)
        # allows user to exit program.
        if tryparse(int, input("Enter 1 to Exit (default=0): "), 0) == 1:
            break
        print("\n" * 2)

def tryparse(type, value, default):
    try:
        return type(value)
    except:
        return type(default)

def link_central(RA, DEC, ZOOM):
    # This function will take a provided RA, DEC, ZOOM; doing a fast error check then returns a list of links.
    # This function is coded in such a way to hopefully make refactoring a bit easier, if more links are needed it may make sense to split of each link generation + error code as its own function for readability. If other data retireval from coord is important in the future than this function should just be calling separate functions alongside an error function. Might be able to come up with something better.
    Error_list = []
    link_list = []
    # Some basic error checking for out of bound values.
    if RA > 360 or RA < 0:
        Error_list.append("RA is out of bounds!")

    if DEC > 90 or DEC < -90:
        Error_list.append("DEC is out of bounds!")

    if ZOOM < 1 or ZOOM > 16:
        Error_list.append("ZOOM is out of bounds! Choose between 1 and 16 inclusive.")

    # Generate legacy link and add to list
    link_list.append(f"\nLegacy Survey (Required for posting): \n https://www.legacysurvey.org/viewer?ra={RA}&dec={DEC}&zoom={ZOOM}")
    # Generate link for sdss skyserver
    link_list.append(f"\nSDSS SkyServer (Required for posting): \n https://skyserver.sdss.org/dr18/VisualTools/explore/summary?ra={RA}&dec={DEC}")
    # Generate link for simbad
    link_list.append(f"\nsimbad: \n https://simbad.u-strasbg.fr/simbad/sim-coo?Coord={RA}d{DEC}d&CooFrame=ICRS&CooEpoch=2000&CooEqui=2000&Radius=2&Radius.unit=arcmin&submit=submit+query&CoordList=")

    # checks if an error has happened, if not it will return the list of links
    if not Error_list:
        return link_list
    else:
        return [f"There seems to be error(s): {Error_list}"]


main()

