import subprocess
import re

def run_mutmut():
    # Run the mutation tests using mutmut
    print("Starting mutation testing...")
    subprocess.call("mutmut run --tests-dir=tests", shell=True)
    
    # Show the results after running
    print("Mutation testing completed. Showing the results...")
    subprocess.call("mutmut results", shell=True)

def analyze_results():
    # Analyze the results to see which mutations were killed or survived
    result_output = subprocess.getoutput("mutmut results")

    survived_count = len(re.findall(r"survived", result_output))
    killed_count = len(re.findall(r"killed", result_output))
    unknown_count = len(re.findall(r"unknown", result_output))

    # Print summary of mutation testing results
    print("\n--- Mutation Test Summary ---")
    print(f"Survived Mutants: {survived_count}")
    print(f"Killed Mutants: {killed_count}")
    print(f"Unknown Mutants: {unknown_count}")
    print(f"Total Mutants: {survived_count + killed_count + unknown_count}\n")

    # Decide on taking any action
    if survived_count > 0:
        print("There are some surviving mutants. Consider improving your test cases.")
    else:
        print("All mutants were killed. Great job on your test coverage!")

if __name__ == "__main__":
    run_mutmut()
    analyze_results()
