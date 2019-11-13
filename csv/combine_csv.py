from subprocess import Popen, PIPE
import pandas as pd
import argparse
import csv
from subprocess import check_output, check_call
from getpass import getpass
import pandas as pd




def get_mse(c1,c2, out, col):
    print("running...")

    df1 = pd.read_csv("{}".format(c1))
    df2 = pd.read_csv("{}".format(c2))
    result = pd.merge(left =df1, right=df2, on=col,how='outer')
    print(result)
    result.to_csv(out)
     

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you merge two csv files, ex; python combine_csv.py -csv1 <csv1> -csv2 <csv2> -o <output_csv> -col "column name"  ')
    parser.add_argument('-csv1', help = 'the first csv you want to merge')
    parser.add_argument('-csv2', help = 'the second csv you want to merge')
    parser.add_argument('-col', help= 'this is the name of the column that is common in the two csvs' )
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c1 = args.csv1
    c2 = args.csv2
    col = args.col
    out = args.o
    print(c1,c2, out, col)
    get_mse(c1,c2, out, col)
