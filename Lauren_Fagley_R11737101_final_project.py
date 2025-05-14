#This program reads a matrix from an input file and, after going through an assigned logic, transforms the values and writes a matrix to an output file.
#Depending on user input, it can also use multiprocessing to process matrixes faster.
#The logic behind the multiprocessing is that it will chop the matrix up into different chunks. This helps preserve memory and time because each process is not receiving the entire matrix
#to parse through. They can divide and conquer. However in order to properly use the logic, each chunk must know its neighboring values. Because of this I also created expanded chunks which 
#would read the surrounding values of the core chunk they were reading. They would only edit the core chunk values and simply read the expanded chunk. There is overlap between expanded chunks
#in the process, but it still remains efficient because the expanded chunks are smaller than passing the entire matrix.
import argparse
import os
from multiprocessing import Pool

#verifies input file path and input file
def verify_input_file(file_path):
    # Check if the input path exists and is a file
    if os.path.exists(file_path) and os.path.isfile(file_path):
        #print(f"Verified: {file_path} exists and is a valid file.")
        return file_path
    else:
        raise argparse.ArgumentTypeError(f"Error: {file_path} does not exist or is not a valid file.")
#verifies output file path
def verify_output_path(file_path):
    #Check if the directory for the output file exists
    dir_path = os.path.dirname(file_path)
    if not dir_path:
        #If no directory is specified, assume the current working directory
        dir_path = os.getcwd()
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        #print(f"Verified: {dir_path} exists for the output file.")
        return file_path
    else:
        raise argparse.ArgumentTypeError(f"Error: {dir_path} does not exist or is not a valid directory.")

def main():
    #sets up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, type=verify_input_file, help="Path to input file")
    parser.add_argument("-o", required=True, type=verify_output_path,help="Path to output file")
    parser.add_argument("-p", type=int, help="Number of processes")
    args1= parser.parse_args()

    input_file = args1.i
    output_file = args1.o
    num_processes = args1.p
    
    
    #reads matrix from input file
    with open(input_file, 'r') as file:
        matrix = [list(line.strip()) for line in file]

    num_row = len(matrix)
    num_col = len(matrix[0])
    print("Project::R11737101")

    #checks if there was an inputed number of processes and if there was, runs parallel programming
    if num_processes or num_processes==1:
        chunk_size = num_row//num_processes
        remainder = num_row % num_processes
    
        
        chunk_sizes = [chunk_size + 1 if i < remainder else chunk_size for i in range(num_processes)] #divides matrix evenly among processes accounting for unequal number of processes
        
        # Compute start and end indices for each process
        start_indices = [sum(chunk_sizes[:i]) for i in range(num_processes)]
        end_indices = [start + size for start, size in zip(start_indices, chunk_sizes)]
        processed_matrix = [['.']*num_col for _ in range(num_row)]

        core_chunk_coords = [] # To store the precomputed chunk boundaries
        #Finds core chunk sizes
        for _, (start, end) in enumerate(zip(start_indices, end_indices)):
            for j in range(0, num_col, chunk_size):
                i_start = start   
                i_end = end
                j_start = j
                j_end = j+chunk_size

                # Extract chunk based on indices
                # Store boundaries for this chunk
                core_chunk_coords.append((i_start, i_end, j_start, j_end))
        
        expanded_chunk_coords = []  # To store the expanded chunk boundaries

        # Determines the expanded chunk boundaries based on core chunk boundaries, expanded chunk should wrap around all sides of core chunk unless the core chunk is on the edge of the matrix
        #If the core chunk is on the edge, the core chunk should include the row or column on the edge of the matrix
        #This ensures that all rows and columns are covered
        for i_start, i_end, j_start, j_end in core_chunk_coords:
            expanded_i_start = max(0, i_start - 1)  # Ensure it doesn't go below row 0
            expanded_i_end = min(num_row, i_end + 1)  # Ensure it doesn't exceed max rows
            expanded_j_start = max(0, j_start - 1)  # Ensure it doesn't go below column 0
            expanded_j_end = min(num_col, j_end + 1)  # Ensure it doesn't exceed max columns

            # Append expanded boundaries
            expanded_chunk_coords.append((expanded_i_start, expanded_i_end, expanded_j_start, expanded_j_end))
        
        #Loops 100 times for 100 processes
        for k in range(100):       
            processed_data =[]
            # Extract and process chunks for the current matrix
            chunk_data = []
            #Now we fill our expanded chunks with data based on the established expanded chunk coords
            for expanded_coords in expanded_chunk_coords:
                expanded_i_start, expanded_i_end, expanded_j_start, expanded_j_end = expanded_coords

                # Calculate local core chunk boundaries relative to the expanded chunk, originally they are set boundaries based on the matrix but this gives boundaries based on the expanded chunk
                #This is why they are indicated as local values since they are 'local' to the expanded chunk
                local_core_i_start = 1 if expanded_i_start > 0 else 0
                local_core_i_end = (expanded_i_end - expanded_i_start) - 1 if expanded_i_end < num_row else (expanded_i_end - expanded_i_start)
                local_core_j_start = 1 if expanded_j_start > 0 else 0
                local_core_j_end = (expanded_j_end - expanded_j_start) - 1 if expanded_j_end < num_col else (expanded_j_end - expanded_j_start)

                #sets core coords
                core_coords = (
                    local_core_i_start, local_core_i_end,
                    local_core_j_start, local_core_j_end,
                )

                # Fill expanded chunk with data from the matrix
                expanded_chunk = [
                    row[expanded_j_start:expanded_j_end]
                    for row in matrix[expanded_i_start:expanded_i_end]
                ]
                #Adds the expanded chunk, its coords, and core coords to be sent to the process matrix function later
                chunk_data.append((expanded_chunk, expanded_coords, core_coords))

            #Uses pool to send each process its own data to calculate the values of
            with Pool(num_processes) as pool:
                processed_data = pool.map(process_matrix, chunk_data)    #returns global core coords (the position of the core in the matrix not in the expanded chunk) and the result chunk
            
            #Parses through the processed data that contains the core coords and the result chunk
            for (core_chunk_coords, result_chunk) in processed_data:
                i_start, i_end, j_start, j_end = core_chunk_coords
                # Write back the processed core chunk into the correct place in the global matrix
                for ci, row in enumerate(result_chunk):
                    for cj, val in enumerate(row):
                        processed_matrix[i_start + ci][j_start + cj] = val
            
            matrix = processed_matrix #sets matrix as processed_matrix so that next process picks up where it left off
    
        #Writes final matrix to outputfile
        with open(output_file, 'w') as outputfile:
            for row in matrix:
                outputfile.write(' '.join(map(str, row)) + '\n')
    else: #if it doesn't have processes indicated or the number of processes is one, it calls it serially
        serial(matrix, output_file, num_row, num_col)

#This function is contains the code for each process. It goes through the expanded matrix and core matrix and applies the set logic to them to make the result matrix
#It returns the result matrix along with the global core coords so that it knows where to insert the result matrix in the original matrix
#It accepts the expanded chunk (full with matrix data) and the expanded coords and the core coords
def process_matrix(args):
    expanded_chunk, expanded_coords, core_coords = args
    local_core_i_start, local_core_i_end, local_core_j_start, local_core_j_end = core_coords

    # Extract the core chunk (called result chunk now) from expanded chunk using precomputed core_coords
    result_chunk = [
        row[local_core_j_start:local_core_j_end]
        for row in expanded_chunk[local_core_i_start:local_core_i_end]
    ]

    # Calculates global core coords so that they can be returned later
    expanded_i_start, _, expanded_j_start, _ = expanded_coords
    global_core_coords = (
        expanded_i_start + local_core_i_start,
        expanded_i_start + local_core_i_end,
        expanded_j_start + local_core_j_start,
        expanded_j_start + local_core_j_end,
    )
   
    #finds length of expanded chunk for parsing through in neighbor matrix
    num_expanded_row = len(expanded_chunk)
    num_expanded_col = len(expanded_chunk[0]) 
    neighbor_matrix = [[0 for _ in range(num_expanded_col)] for _ in range(num_expanded_row)] #sets up neighbor matrix which will be a matrix of int values containing the sum of all the neighbors of every position
    #iterates through expanded chunk calculating the sum of neighbor values
    for i in range(num_expanded_row):
        for j in range(num_expanded_col):
            n1 = '.' #sets all neighbor values as '.' for default, and sets them every loop so that a value isn't set as X and then counted as X later when it should've been '.'
            n2 = '.'
            n3 = '.'
            nL = '.'
            nR = '.'
            n4 = '.'
            n5 = '.'
            n6 = '.'
            if i != 0 and j != 0: 
                n1 = expanded_chunk[i-1][j-1]
            if i != 0:
                n2 = expanded_chunk[i-1][j]
            if i != 0 and j != num_expanded_col-1:
                n3 = expanded_chunk[i-1][j+1]
            if j != 0:
                nL = expanded_chunk[i][j-1]
            if j != num_expanded_col-1:
                nR = expanded_chunk[i][j+1]
            if i != num_expanded_row-1 and j != 0:
                n4 = expanded_chunk[i+1][j-1]
            if i != num_expanded_row-1:
                n5 = expanded_chunk[i+1][j]
            if i != num_expanded_row-1 and j != num_expanded_col-1:
                n6 = expanded_chunk[i+1][j+1]

            neighbors = [n1,n2,n3,nL,nR,n4,n5,n6] #I through all the neighbor values in a list so that I could use the count function to count their values instead of comparing each individually and counting that way

            count_X = neighbors.count('X') * -2 #counts X and multiplies by -2
            count_O = neighbors.count('O') * 2 #counts O and multiplies by 2
            count_x = neighbors.count('x') * -1 #counts x and multiplies by -1
            count_o = neighbors.count('o') #counts o
            count = 0 #I did count = 0 because if all of the other counts didn't have a value, it would equal 0 

            sum_of_neighbors = count_X + count_O + count_x + count_o + count #get the sum of all the neighbors
            neighbor_matrix[i][j] = sum_of_neighbors #put the sum of the neighbors into the neighbor matrix to be read later
    
    #This iterates through the core matrix and compares values in the neighbor matrix using the assigned logic to update the values
    for ci in range(local_core_i_start, local_core_i_end):
        for cj in range(local_core_j_start, local_core_j_end):
            symbol = result_chunk[ci - local_core_i_start][cj - local_core_j_start] #sets the current symbol that it will compare
            sum_of_neighbors = neighbor_matrix[ci][cj] #finds the neighbor value at that equivalent spot
            #List of comparisons based on neighbor and symbol value. Sets result_chunk to new value
            if symbol == 'O':
                if sum_of_neighbors in {1,2,4,8,16}:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = '.'
                elif sum_of_neighbors < 10:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'o'
            elif symbol == 'o':
                if sum_of_neighbors <= 0:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = '.'
                elif sum_of_neighbors >= 8:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'O'
            elif symbol == '.':
                if sum_of_neighbors in {2, 3, 5, 7, 11, 13}:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'o'
                elif sum_of_neighbors in {-2,-3, -5, -7, -11, -13}:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'x'
            elif symbol == 'x':
                if sum_of_neighbors >= 1:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = '.'
                elif sum_of_neighbors <= -8:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'X'
            else:
                if sum_of_neighbors in {-1,-2,-4,-8,-16,1,2,4,8,16}:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = '.'
                elif sum_of_neighbors > -10:
                    result_chunk[ci - local_core_i_start][cj - local_core_j_start] = 'x'

    
    return global_core_coords, result_chunk
#Basically the same logic as the process_matrix but takes the entire matrix, iterates 100 times within the function and prints to the output file in the function    
def serial(matrix, output_file,num_row,num_col):
    neighbor_matrix = [[0 for _ in range(num_row)]for _ in range(num_col)]
    for k in range(100): 
        for i in range(num_row):
            for j in range(num_col):
                n1 = '.'
                n2 = '.'
                n3 = '.'
                nL = '.'
                nR = '.'
                n4 = '.'
                n5 = '.'
                n6 = '.'
                if i != 0 and j != 0: 
                    n1 = matrix[i-1][j-1]
                if i != 0:
                    n2 = matrix[i-1][j]
                if i != 0 and j != num_col-1:
                    n3 = matrix[i-1][j+1]
                if j != 0:
                    nL = matrix[i][j-1]
                if j != num_row-1:
                    nR = matrix[i][j+1]
                if i != num_row-1 and j != 0:
                    n4 = matrix[i+1][j-1]
                if i != num_row-1:
                    n5 = matrix[i+1][j]
                if i != num_row-1 and j != num_col-1:
                    n6 = matrix[i+1][j+1]

                neighbors = [n1,n2,n3,nL,nR,n4,n5,n6]

                count_X = neighbors.count('X') * -2
                count_O = neighbors.count('O') * 2
                count_x = neighbors.count('x') * -1
                count_o = neighbors.count('o')
                count = 0

                sum_of_neighbors = count_X + count_O + count_x + count_o + count
                neighbor_matrix[i][j] = sum_of_neighbors
    
        for i in range(num_row):
            for j in range(num_col):
                symbol = matrix[i][j]
                sum_of_neighbors = neighbor_matrix[i][j]
                if symbol == 'O':
                    if sum_of_neighbors in {1,2,4,8,16}:
                        matrix[i][j] = '.'
                    elif sum_of_neighbors < 10:
                        matrix[i][j] = 'o'
                elif symbol == 'o':
                    if sum_of_neighbors <= 0:
                        matrix[i][j] = '.'
                    elif sum_of_neighbors >= 8:
                        matrix[i][j] = 'O'
                elif symbol == '.':
                    if sum_of_neighbors in {2, 3, 5, 7, 11, 13}:
                        matrix[i][j] = 'o'
                    elif sum_of_neighbors in {-2,-3, -5, -7, -11, -13}:
                        matrix[i][j] = 'x'
                elif symbol == 'x':
                    if sum_of_neighbors >= 1:
                        matrix[i][j] = '.'
                    elif sum_of_neighbors <= -8:
                        matrix[i][j] = 'X'
                else:
                    if sum_of_neighbors in {-1,-2,-4,-8,-16,1,2,4,8,16}:
                        matrix[i][j] = '.'
                    elif sum_of_neighbors > -10:
                        matrix[i][j] = 'x'
    
    with open(output_file, 'w') as outputfile:
        for row in matrix:
            outputfile.write(' '.join(map(str, row)) + '\n')

if __name__ == "__main__":
    main()