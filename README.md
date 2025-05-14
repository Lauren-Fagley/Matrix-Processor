#Matrix Processor with Optional Multiprocessing
#Overview

This Python program processes a matrix from an input file and writes a transformed version to an output file. It includes an optional multiprocessing mode to enhance performance on large matrices.

The core logic transforms each cell in the matrix based on the values of its neighbors using a custom rule set. In multiprocessing mode, the matrix is divided into overlapping chunks so that each process has the necessary context (neighboring cells) to apply the transformation accurately.
#Features

    Reads a matrix from an input file.

    Applies transformation rules iteratively for 100 cycles.

    Optionally uses multiprocessing for performance.

    Efficient memory use via chunking strategy.

    Writes the final matrix to an output file.

#How It Works
#Serial Mode

    Processes the entire matrix in a single process.

    Applies neighbor-based transformation rules for 100 iterations.

#Multiprocessing Mode

    Splits the matrix into core chunks to be modified.

    Surrounds each core chunk with an expanded chunk to ensure each process has access to neighboring values.

    Spawns n worker processes using Python’s multiprocessing.Pool.

    Each worker modifies only the core chunk, using the expanded chunk for context.

    Final matrix is reconstructed by merging the results from all processes after each iteration.

#Transformation Rules

Each cell is transformed based on the sum of its 8 neighbors, where neighbors contribute values based on their symbols:
Symbol	Value Contribution
O	+2
o	+1
x	-1
X	-2
.	0

Based on the sum, each symbol has custom rules for transformation, for example:

    O turns into . for certain powers of 2, or o if the sum is less than 10.

    . turns into o or x if the sum is in specific prime numbers or their negative counterparts.

#Usage

python3 main.py -i input.txt -o output.txt [-p num_processes]

Arguments

    -i (required): Path to the input file containing the initial matrix.

    -o (required): Path to the output file to save the processed matrix.

    -p: Optional. Number of parallel processes to use. If omitted or set to 1, serial mode is used.

#Input Format

The input file should contain a matrix where each line represents a row of characters like:

.O.oX
xO..o
.OXx.

#Output Format

The output is a matrix in the same format, written to the specified file.
Requirements

    Python 3.6+

    No external libraries required.

#Performance Notes

    Multiprocessing is most beneficial for large matrices.

    Overhead from process management may outweigh the benefit on smaller datasets.

    Neighbor calculation and chunk expansion are optimized to minimize redundant computation.

#Author

Lauren
