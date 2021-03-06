import sys

from struct import *

if len(sys.argv) < 3:
    raise Exception("Specify wtb file as input file and csv file as output file!")

wtb_file = sys.argv[1]
csv_file = sys.argv[2]
try:
    infile = open(wtb_file, mode='rb')
    outfile = open(csv_file, mode='w')

    ## firstly, read header and write them to csv file ##
    header = unpack('<bbbbihhbbbb', infile.read(16))  # little-endian
    
    created_year = str(header[0]) + str(header[1])
    created_date = str(header[2]) + str(header[3])
    num_match = header[4]
    num_record = str(header[5])    # must be 0 in wtb file
    year = str(header[6])          # year in which matches taken place
    othello_size = str(header[7])  # default size is 8
    match_type = str(header[8])    # must be 0
    # If the black-disc player chose perfect moves from this depth
    # (number of blank squares), the total score of black-disc will be
    # 'theoretical score', described later.
    depth = str(header[9])
    padding = str(header[10])

    outfile.writelines("created year : " + created_year + ",")
    outfile.writelines("created date : " + created_date + ",")
    outfile.writelines("number of matches : " + str(num_match) + ",")
    outfile.writelines("number of records : " + num_record + ",")
    outfile.writelines("year : " + year + ",")
    outfile.writelines("othello size : " + othello_size + ",")
    outfile.writelines("match type : " + match_type + ",")
    outfile.writelines("depth : " + depth + ",")
    outfile.writelines("padding : " + padding + ",")
    outfile.writelines("\n")


    ## read all data about matches ##
    # write headers to the csv file
    outfile.writelines("tournament id,dark-player id,light-player id,score,theoretical score,")
    for j in range(1,60):
        outfile.writelines(f"{j},")
    outfile.writelines("60\n")

    # read data and write it to the csv file
    for i in range(num_match):
        # first 8-byte data tells information about the match
        match_data = unpack('<hhhbb', infile.read(8))
        tournament_id = match_data[0]
        dark_player_id = match_data[1]
        light_player_id = match_data[2]
        dark_score = match_data[3]       # implies the result of the match
        theoretical_score = match_data[4] # best score by perfect moves
        outfile.writelines(f"{tournament_id},")
        outfile.writelines(f"{dark_player_id},")
        outfile.writelines(f"{light_player_id},")
        outfile.writelines(f"{dark_score},")
        outfile.writelines(f"{theoretical_score},")
        
        # latter 60-byte data represents moves
        for j in range(59):
            move = str(unpack('b', infile.read(1))[0]).zfill(2)
            if move == "00": # the game is already over
                outfile.writelines("---,")
            else:
                outfile.writelines(f"{int(move[0])-1}-{int(move[1])-1},")
        move = str(unpack('b', infile.read(1))[0]).zfill(2)
        if move == "00": # the game is already over
            outfile.writelines("---\n")
        else:
            outfile.writelines(f"{int(move[0])-1}-{int(move[1])-1}\n")

finally:
    infile.close()
    outfile.close()
