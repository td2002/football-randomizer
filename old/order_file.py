file_in_name = "ids_with_market_vals_buf"
file_out_name = "testout"

flag = {"no_market_val" : True}
index = 0
num_of_with_market_val = 0

with open(f"./new/{file_in_name}.txt", "r") as file:
    lines = [line.split() for line in file]
    lines_ordered = sorted(lines, key=lambda x : [-int(x[1]), int(x[0])])
    with open(f"./new/{file_out_name}.txt", "w") as file_out, open(f"./new/metadata.txt", "w") as file_meta_out:
        for line in lines_ordered:
            index+=1
            file_out.write(f"{line[0]} {line[1]}\n")
            if flag["no_market_val"] and line[1] == "1":
                file_meta_out.write(f"first_no_market_val(its_file_row_index): {index}\n")
                num_of_with_market_val = index
                flag["no_market_val"] = False
        file_meta_out.write(f"num_of_total_rows: {index}\n")
